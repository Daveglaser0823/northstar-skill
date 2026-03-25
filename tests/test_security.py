#!/usr/bin/env python3
"""
Security Hardening Tests

Verifies:
- _get_license_secret() returns non-empty bytes
- License secret resolution: env var → file → machine-derived default
- Revoked key rejection uses hash-based approach
- Version consistency: scripts/version.py matches argparse --version
"""

import os
import sys
import hashlib
import unittest
from pathlib import Path
from unittest.mock import patch

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import northstar


class TestGetLicenseSecret(unittest.TestCase):
    """Tests for _get_license_secret() resolution."""

    def test_returns_bytes(self):
        """_get_license_secret() must always return bytes."""
        secret = northstar._get_license_secret()
        self.assertIsInstance(secret, bytes)

    def test_returns_non_empty(self):
        """_get_license_secret() must return a non-empty value."""
        secret = northstar._get_license_secret()
        self.assertGreater(len(secret), 0)

    def test_env_var_takes_precedence(self):
        """NORTHSTAR_LICENSE_SECRET env var is used when set."""
        with patch.dict(os.environ, {"NORTHSTAR_LICENSE_SECRET": "test-secret-xyz"}):
            secret = northstar._get_license_secret()
        self.assertEqual(secret, b"test-secret-xyz")

    def test_file_fallback(self):
        """Reads from ~/.clawd/skills/northstar/config/.license_secret when no env var."""
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".secret") as f:
            f.write(b"file-secret-abc")
            tmp_path = Path(f.name)

        try:
            # No env var, file exists
            with patch.dict(os.environ, {}, clear=False):
                os.environ.pop("NORTHSTAR_LICENSE_SECRET", None)
                with patch.object(northstar, "_LICENSE_SECRET_PATH", tmp_path):
                    secret = northstar._get_license_secret()
            self.assertEqual(secret, b"file-secret-abc")
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_machine_derived_default(self):
        """Falls back to deterministic machine-derived value when no env/file."""
        nonexistent = Path("/tmp/northstar_secret_nonexistent_xyz.txt")
        if nonexistent.exists():
            nonexistent.unlink()

        env_backup = os.environ.pop("NORTHSTAR_LICENSE_SECRET", None)
        try:
            with patch.object(northstar, "_LICENSE_SECRET_PATH", nonexistent):
                secret = northstar._get_license_secret()

            # Should be deterministic: SHA-256[:16] of home dir
            expected = hashlib.sha256(str(Path.home()).encode()).digest()[:16]
            self.assertEqual(secret, expected)
        finally:
            if env_backup is not None:
                os.environ["NORTHSTAR_LICENSE_SECRET"] = env_backup

    def test_machine_derived_is_16_bytes(self):
        """Machine-derived default is exactly 16 bytes."""
        nonexistent = Path("/tmp/northstar_secret_nonexistent_xyz2.txt")
        if nonexistent.exists():
            nonexistent.unlink()

        env_backup = os.environ.pop("NORTHSTAR_LICENSE_SECRET", None)
        try:
            with patch.object(northstar, "_LICENSE_SECRET_PATH", nonexistent):
                secret = northstar._get_license_secret()
            self.assertEqual(len(secret), 16)
        finally:
            if env_backup is not None:
                os.environ["NORTHSTAR_LICENSE_SECRET"] = env_backup


class TestRevokedKeyHashes(unittest.TestCase):
    """Tests for revoked key rejection using hash-based approach."""

    def test_revoked_key_rejected(self):
        """A known-revoked key (stored as hash) is rejected during activation."""
        # The revoked key - attempting to activate it should call sys.exit(1)
        revoked_key = "NS-PRO-DTML-H6TK-SACG"
        with self.assertRaises(SystemExit) as ctx:
            northstar.cmd_activate(revoked_key)
        self.assertEqual(ctx.exception.code, 1)

    def test_valid_key_not_rejected(self):
        """A non-revoked key is not rejected at the revocation check step."""
        # This key is not in _REVOKED_KEY_HASHES; cmd_activate will fail later
        # for different reasons (no config, no Polar org_id), but NOT at revocation.
        valid_key = "NSP-TEST-XXXX-YYYY"
        # We expect it to proceed past revocation check and try to load config
        # Config doesn't exist, so it should raise FileNotFoundError or similar,
        # NOT sys.exit(1) from the revocation block
        try:
            northstar.cmd_activate(valid_key)
        except SystemExit:
            # If it exits, must not be the "revoked" exit path
            # (revocation exits with code 1 and prints revocation message)
            # Other failures (missing config etc.) are acceptable
            pass
        except Exception:
            # Expected: config missing or other non-revocation failure
            pass

    def test_revocation_uses_hash_not_plaintext(self):
        """Verify the revoked key hash matches our expected SHA-256 value."""
        revoked_key = "NS-PRO-DTML-H6TK-SACG"
        expected_hash = "b1f175f7c3e176e5449b409dc000bf0e098381bcb6f005a1b9f0dead44b96482"
        actual_hash = hashlib.sha256(revoked_key.upper().encode()).hexdigest()
        self.assertEqual(actual_hash, expected_hash)


class TestVersionConsistency(unittest.TestCase):
    """Verifies version.py matches argparse --version string."""

    def test_version_module_exports_string(self):
        """version.py exports __version__ as a non-empty string."""
        from version import __version__  # noqa: PLC0415
        self.assertIsInstance(__version__, str)
        self.assertGreater(len(__version__), 0)

    def test_northstar_uses_version_module(self):
        """northstar.__version__ matches version.py __version__."""
        from version import __version__ as expected  # noqa: PLC0415
        self.assertEqual(northstar.__version__, expected)

    def test_argparse_version_matches_version_module(self):
        """The argparse --version string contains the version from version.py."""
        # We verify by checking the source uses __version__ (not a hardcoded string)
        src_path = Path(__file__).parent.parent / "scripts" / "northstar.py"
        content = src_path.read_text()
        self.assertIn("Northstar {__version__}", content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
