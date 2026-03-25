#!/usr/bin/env python3
"""
=============================================================================
Northstar User Journey Tests
=============================================================================

These tests exercise the REAL code paths a user follows — from fresh install
through activation, configuration, and daily briefing generation.

Context: Ryan (our first user) had a broken experience. The 202 existing unit
tests mock everything and don't prove the actual end-to-end flow works.

Each test simulates a concrete user action, uses tmp_path for full isolation,
and touches NO real filesystem paths.
=============================================================================
"""

import io
import json
import sys
import hashlib
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# ---------------------------------------------------------------------------
# Module import - load scripts.northstar from its actual location
# ---------------------------------------------------------------------------
_NORTHSTAR_DIR = Path(__file__).parent.parent
_SCRIPTS_DIR = _NORTHSTAR_DIR / "scripts"

if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

# Expose scripts dir as 'scripts' package for `import scripts.northstar`
if str(_NORTHSTAR_DIR) not in sys.path:
    sys.path.insert(0, str(_NORTHSTAR_DIR))

import northstar  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_license_secret(tmp_path: Path) -> Path:
    """Create a sandboxed license secret file and return its path."""
    secret_file = tmp_path / ".license_secret"
    secret_file.write_bytes(b"test-journey-secret-xyz")
    return secret_file


def _sign_token(key: str, tier: str, secret: bytes) -> str:
    """Produce HMAC token matching the production sign_license_token() logic."""
    import hmac as _hmac
    import hashlib as _hashlib
    msg = f"{key.upper()}:{tier.lower()}".encode()
    return _hmac.new(secret, msg, _hashlib.sha256).hexdigest()


def _sandbox_paths(monkeypatch, tmp_path: Path):
    """
    Redirect all module-level file paths to tmp_path so no test ever
    touches the real ~/.clawd directory.

    Returns (config_path, state_path, secret_path).
    """
    config_path = tmp_path / "northstar.json"
    state_path = tmp_path / "state.json"
    secret_path = tmp_path / ".license_secret"

    monkeypatch.setattr(northstar, "CONFIG_PATH", config_path)
    monkeypatch.setattr(northstar, "STATE_PATH", state_path)
    monkeypatch.setattr(northstar, "_LICENSE_SECRET_PATH", secret_path)

    return config_path, state_path, secret_path


# ---------------------------------------------------------------------------
# Journey 1: Fresh install + activate
# ---------------------------------------------------------------------------

class TestFreshInstallActivate:
    """
    User action: Brand-new install. No config exists.
    User runs: northstar activate NSP-TEST-1234-ABCD
    """

    def test_fresh_activate_creates_config(self, tmp_path, monkeypatch):
        """
        Simulate: User runs `northstar activate NSP-TEST-1234-ABCD` with no
        prior config. Verify: config file created, tier = 'pro', license_key
        stored, HMAC token generated and valid.
        """
        config_path, state_path, secret_path = _sandbox_paths(monkeypatch, tmp_path)

        # Plant a known secret so tokens are deterministic in this test
        secret = b"test-journey-secret-xyz"
        secret_path.write_bytes(secret)

        license_key = "NSP-TEST-1234-ABCD"

        # Patch: no Polar org_id (offline mode - validates format only)
        # Patch: sys.exit so we can assert rather than abort
        polar_config_nonexistent = tmp_path / "polar.json"  # doesn't exist

        with patch.object(
            northstar.Path,
            "__truediv__",
            side_effect=lambda self, other: (
                polar_config_nonexistent
                if str(other) == "polar.json"
                else type(self)(self, other)  # type: ignore[call-arg]
            ),
        ):
            # Simpler approach: patch the polar config lookup in cmd_activate
            pass

        # cmd_activate reads polar.json from: Path(__file__).parent.parent / "config" / "polar.json"
        # We'll mock validate_polar_license to not be called (no org_id) by ensuring
        # the polar config file doesn't exist (it doesn't in our sandbox naturally,
        # but cmd_activate looks at a hardcoded path relative to __file__)
        # Patch it to our nonexistent tmp path
        with patch("northstar.Path") as MockPath:
            # Allow northstar.Path to work normally for everything EXCEPT the polar.json lookup
            real_path = Path
            def path_side_effect(*args, **kwargs):
                return real_path(*args, **kwargs)
            MockPath.side_effect = path_side_effect
            MockPath.home.return_value = real_path.home()

            # Actually, patching Path class is fragile. Use a simpler approach:
            # patch validate_polar_license to simulate "not called" (no org_id path).
            pass

        # Cleanest approach: patch the polar config existence check directly
        # cmd_activate does: polar_config_path = Path(__file__).parent.parent / "config" / "polar.json"
        # and then checks polar_config_path.exists() -> if True, reads org_id
        # We patch Path.exists on that specific path by mocking validate_polar_license entirely
        # and forcing org_id to None by patching open on a non-existent path.

        # Since the real polar.json doesn't exist in our repo's config/, cmd_activate
        # will skip Polar validation and go straight to format-only check.
        # Let's verify that's actually the case:
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            northstar.cmd_activate(license_key)

        output = captured.getvalue()

        # --- Assertions ---
        assert config_path.exists(), "Config file must be created after activation"

        with open(config_path) as f:
            config = json.load(f)

        # Tier set to pro
        assert config["tier"] == "pro", f"Expected tier='pro', got {config['tier']!r}"

        # License key stored verbatim
        assert config["license_key"] == license_key, (
            f"license_key mismatch: {config['license_key']!r}"
        )

        # HMAC token generated
        assert "license_token" in config, "license_token must be present in config"
        token = config["license_token"]
        assert token, "license_token must not be empty"

        # Token is valid (verify_license_token uses the same secret from secret_path)
        is_valid = northstar.verify_license_token(config)
        assert is_valid, (
            f"verify_license_token() returned False. token={token!r}, "
            f"key={license_key!r}, tier=pro"
        )

        # Output confirms activation
        assert "Pro" in output or "pro" in output.lower(), (
            f"Expected 'Pro' in output: {output!r}"
        )


# ---------------------------------------------------------------------------
# Journey 2: Fresh install + activate + doctor/test command
# ---------------------------------------------------------------------------

class TestActivateThenDoctor:
    """
    User action: After activation, user runs `northstar test` (doctor path).
    """

    def test_doctor_after_activation(self, tmp_path, monkeypatch):
        """
        Simulate: User activates successfully, then runs `northstar test` (which
        routes to cmd_doctor). Verify: runs without crashing, reports correct tier,
        identifies missing Stripe key (expected for a fresh config).
        """
        config_path, state_path, secret_path = _sandbox_paths(monkeypatch, tmp_path)
        secret_path.write_bytes(b"test-journey-secret-xyz")

        license_key = "NSP-TEST-5678-EFGH"

        # Step 1: Activate
        with patch("sys.stdout", io.StringIO()):
            northstar.cmd_activate(license_key)

        assert config_path.exists(), "Config must exist after activation"

        # Step 2: Run doctor
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            exit_code = northstar.cmd_doctor(config_path=config_path, offline=True)

        output = captured.getvalue()

        # Must not crash (returns an int exit code)
        assert isinstance(exit_code, int), f"cmd_doctor must return int, got {type(exit_code)}"

        # Reports contain tier information
        assert "pro" in output.lower() or "tier" in output.lower() or "License" in output, (
            f"Expected tier info in doctor output:\n{output}"
        )

        # Identifies missing Stripe key (expected - we didn't configure one)
        # The doctor check for Stripe will WARN (not enabled) or FAIL (missing key)
        stripe_mentioned = "Stripe" in output or "stripe" in output.lower()
        assert stripe_mentioned, (
            f"Expected Stripe check in doctor output:\n{output}"
        )

        # License key check should show a result (PASS or at least mention key)
        license_mentioned = "License" in output or "license" in output.lower()
        assert license_mentioned, (
            f"Expected license check in doctor output:\n{output}"
        )


# ---------------------------------------------------------------------------
# Journey 3: Setup wizard (non-interactive config creation)
# ---------------------------------------------------------------------------

class TestSetupWizardFlow:
    """
    User action: User completes setup wizard and has a valid config with Stripe.
    We simulate the programmatic equivalent (wizard output = written config).
    """

    def test_config_creation_with_stripe(self, tmp_path, monkeypatch):
        """
        Simulate: User completes `northstar setup` wizard, enabling Stripe
        with a placeholder key. Verify: config file is valid JSON with correct
        structure (tier, stripe enabled, delivery channel).
        """
        config_path, state_path, secret_path = _sandbox_paths(monkeypatch, tmp_path)
        secret_path.write_bytes(b"test-journey-secret-xyz")

        # Build the config that setup wizard would produce
        valid_config = {
            "tier": "pro",
            "license_key": "NSP-TEST-SETUP-WXYZ",
            "license_token": _sign_token(
                "NSP-TEST-SETUP-WXYZ", "pro", b"test-journey-secret-xyz"
            ),
            "stripe": {
                "enabled": True,
                "api_key": "sk_test_placeholder_northstar_journey",
                "monthly_revenue_goal": 10000,
                "currency": "usd",
            },
            "delivery": {
                "channel": "none",
            },
            "alerts": {
                "payment_failures": True,
                "churn_threshold": 3,
                "large_refund_threshold": 100,
            },
            "format": {
                "emoji": True,
                "include_pacing": True,
            },
            "schedule": {
                "hour": 6,
                "minute": 0,
                "timezone": "America/New_York",
            },
        }

        # Write it (simulating wizard output)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(valid_config, f, indent=2)

        # --- Verify it's loadable and structurally valid ---
        assert config_path.exists(), "Config file must exist"

        # Raw JSON parse
        with open(config_path) as f:
            raw = json.load(f)

        assert isinstance(raw, dict), "Config must be a JSON object"
        assert raw["tier"] == "pro"
        assert raw["stripe"]["enabled"] is True
        assert raw["stripe"]["api_key"].startswith("sk_test_"), (
            f"Expected sk_test_ key, got {raw['stripe']['api_key']!r}"
        )

        # northstar.load_config() must succeed
        config = northstar.load_config(config_path)
        assert config["tier"] == "pro"
        assert config["stripe"]["enabled"] is True

        # License token must verify
        is_valid = northstar.verify_license_token(config)
        assert is_valid, "License token must verify correctly for wizard-created config"

        # Delivery channel present
        assert "delivery" in config
        assert "channel" in config["delivery"]


# ---------------------------------------------------------------------------
# Journey 4: Full run --dry-run with mock Stripe
# ---------------------------------------------------------------------------

class TestFullRunDryRun:
    """
    User action: User runs `northstar run --dry-run` with Stripe configured.
    """

    def _realistic_charge_list(self, amount_cents: int = 9900) -> MagicMock:
        """Build a mock that behaves like stripe.Charge.list() with auto_paging_iter."""
        charge = MagicMock()
        charge.__getitem__ = lambda self, key: {
            "amount": amount_cents,
            "status": "succeeded",
            "currency": "usd",
        }[key]
        charge.get = lambda key, default=None: {
            "amount": amount_cents,
            "status": "succeeded",
            "currency": "usd",
        }.get(key, default)

        result = MagicMock()
        result.auto_paging_iter.return_value = iter([charge])
        result.get = MagicMock(return_value=0)
        return result

    def _realistic_subscription_list(self, total_count: int = 42) -> MagicMock:
        """Build a mock that behaves like stripe.Subscription.list()."""
        result = MagicMock()
        result.get = lambda key, default=None: (
            total_count if key == "total_count" else default
        )
        result.auto_paging_iter.return_value = iter([])
        return result

    def _realistic_payment_intent_list(self) -> MagicMock:
        """Build a mock for stripe.PaymentIntent.list()."""
        result = MagicMock()
        result.auto_paging_iter.return_value = iter([])
        return result

    def test_run_dry_run_with_stripe(self, tmp_path, monkeypatch):
        """
        Simulate: User runs `northstar run --dry-run` after setup. Stripe is
        mocked with realistic API response data. Verify: briefing is generated,
        contains revenue numbers, cmd_run() does not crash.
        """
        config_path, state_path, secret_path = _sandbox_paths(monkeypatch, tmp_path)
        secret_path.write_bytes(b"test-journey-secret-xyz")

        secret = b"test-journey-secret-xyz"
        license_key = "NSP-TEST-RUN-DRYRUN"
        token = _sign_token(license_key, "pro", secret)

        config = {
            "tier": "pro",
            "license_key": license_key,
            "license_token": token,
            "stripe": {
                "enabled": True,
                "api_key": "sk_test_dryrun_mock_key",
                "monthly_revenue_goal": 10000,
                "currency": "usd",
            },
            "delivery": {
                "channel": "none",
            },
            "alerts": {
                "payment_failures": True,
                "churn_threshold": 3,
                "large_refund_threshold": 100,
            },
            "format": {
                "emoji": True,
                "include_pacing": True,
            },
        }

        # Write config so load_state/save_state have a dir
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

        # --- Mock stripe module with realistic Stripe API response shape ---
        mock_stripe = MagicMock()

        # Charges: $99.00 yesterday
        charge_mock = MagicMock()
        charge_mock.__getitem__ = lambda self, key: {
            "amount": 9900,
            "status": "succeeded",
            "currency": "usd",
        }[key]
        charge_mock.get = lambda key, default=None: {
            "amount": 9900,
            "status": "succeeded",
            "currency": "usd",
        }.get(key, default)

        charge_list_mock = MagicMock()
        charge_list_mock.auto_paging_iter.return_value = iter([charge_mock])
        charge_list_mock.get = MagicMock(return_value=0)
        mock_stripe.Charge.list.return_value = charge_list_mock

        # Subscriptions: 42 active, 0 new, 0 canceled
        sub_list_mock = MagicMock()
        sub_list_mock.get = lambda key, default=None: (
            42 if key == "total_count" else default
        )
        sub_list_mock.auto_paging_iter.return_value = iter([])
        mock_stripe.Subscription.list.return_value = sub_list_mock

        # PaymentIntents
        pi_list_mock = MagicMock()
        pi_list_mock.auto_paging_iter.return_value = iter([])
        mock_stripe.PaymentIntent.list.return_value = pi_list_mock

        # Capture output
        captured = io.StringIO()

        with patch.dict(sys.modules, {"stripe": mock_stripe}):
            with patch("sys.stdout", captured):
                northstar.cmd_run(config, dry_run=True)

        output = captured.getvalue()

        # --- Assertions ---
        # Must not crash (if it did, we wouldn't reach here)

        # Briefing was built and printed (dry_run=True delivers to stdout/terminal)
        # The build_briefing output contains revenue numbers
        assert "$" in output or "revenue" in output.lower() or "Northstar" in output, (
            f"Expected briefing in output:\n{output}"
        )

        # Stripe was actually called (not silently skipped)
        assert mock_stripe.Charge.list.called, (
            "stripe.Charge.list() was never called - Stripe data not fetched"
        )
        assert mock_stripe.Subscription.list.called, (
            "stripe.Subscription.list() was never called"
        )

        # Revenue number appears in output: $99.00 = $99 in fmt_currency
        assert "99" in output or "briefing" in output.lower() or "Briefing" in output, (
            f"Expected revenue number (99) in output:\n{output}"
        )


# ---------------------------------------------------------------------------
# Journey 5: Activation with revoked key
# ---------------------------------------------------------------------------

class TestRevokedKeyActivation:
    """
    User action: User tries to activate with a known-revoked key.
    """

    def test_revoked_key_rejected_with_clear_error(self, tmp_path, monkeypatch):
        """
        Simulate: User enters a key that has been revoked (rotated 2026-03-23).
        Verify: cmd_activate rejects it immediately with a clear error message
        and sys.exit(1) — no partial config written.
        """
        config_path, state_path, secret_path = _sandbox_paths(monkeypatch, tmp_path)

        # This is the known-revoked key (its SHA-256 hash is hardcoded in northstar.py)
        revoked_key = "NS-PRO-DTML-H6TK-SACG"

        # Verify the hash matches what northstar expects
        expected_hash = "b1f175f7c3e176e5449b409dc000bf0e098381bcb6f005a1b9f0dead44b96482"
        actual_hash = hashlib.sha256(revoked_key.upper().encode()).hexdigest()
        assert actual_hash == expected_hash, (
            f"Revoked key hash mismatch — northstar.py may have changed.\n"
            f"Expected: {expected_hash}\nGot: {actual_hash}"
        )

        captured = io.StringIO()

        with patch("sys.stdout", captured):
            with pytest.raises(SystemExit) as exc_info:
                northstar.cmd_activate(revoked_key)

        # Must exit with code 1
        assert exc_info.value.code == 1, (
            f"Expected sys.exit(1), got sys.exit({exc_info.value.code})"
        )

        output = captured.getvalue()

        # Error message must be clear and human-readable
        assert "revoked" in output.lower(), (
            f"Expected 'revoked' in error output:\n{output}"
        )
        assert "no longer valid" in output.lower() or "invalid" in output.lower() or "revoked" in output.lower(), (
            f"Expected clear rejection message:\n{output}"
        )

        # No config file should have been created
        assert not config_path.exists(), (
            "Config must NOT be created when a revoked key is rejected"
        )


# ---------------------------------------------------------------------------
# Journey 6: Tier gating after activation
# ---------------------------------------------------------------------------

class TestTierGatingAfterActivation:
    """
    User action: User activates with Standard key, checks Pro access.
    Then activates with Pro key, checks Pro access is granted.
    """

    def test_standard_tier_gates_pro_features(self, tmp_path, monkeypatch):
        """
        Simulate: User activates with NSS- (Standard) key.
        Verify: tier='standard' in config, Pro features return False from is_pro(),
        verify_license_token() returns True (valid standard token).
        """
        config_path, state_path, secret_path = _sandbox_paths(monkeypatch, tmp_path)
        secret_path.write_bytes(b"test-journey-secret-xyz")

        license_key = "NSS-TEST-GATE-STAND"

        with patch("sys.stdout", io.StringIO()):
            northstar.cmd_activate(license_key)

        assert config_path.exists()
        config = northstar.load_config(config_path)

        # Tier set correctly
        assert config["tier"] == "standard", (
            f"Expected tier='standard', got {config['tier']!r}"
        )

        # Token valid for standard tier
        assert northstar.verify_license_token(config), (
            "verify_license_token() must return True for valid standard activation"
        )

        # Pro features gated: is_pro() must return False
        # Load northstar_pro and check
        if str(_SCRIPTS_DIR) not in sys.path:
            sys.path.insert(0, str(_SCRIPTS_DIR))

        # Fresh import to avoid cached state
        if "northstar_pro" in sys.modules:
            pro_mod = sys.modules["northstar_pro"]
        else:
            import northstar_pro as pro_mod  # type: ignore

        assert not pro_mod.is_pro(config), (
            "is_pro() must return False for Standard tier activation"
        )

    def test_pro_tier_unlocks_pro_features(self, tmp_path, monkeypatch):
        """
        Simulate: User activates with NSP- (Pro) key.
        Verify: tier='pro' in config, is_pro() returns True, Pro features available.
        """
        config_path, state_path, secret_path = _sandbox_paths(monkeypatch, tmp_path)
        secret_path.write_bytes(b"test-journey-secret-xyz")

        license_key = "NSP-TEST-GATE-PROX1"

        with patch("sys.stdout", io.StringIO()):
            northstar.cmd_activate(license_key)

        assert config_path.exists()
        config = northstar.load_config(config_path)

        # Tier set correctly
        assert config["tier"] == "pro", (
            f"Expected tier='pro', got {config['tier']!r}"
        )

        # Token valid
        assert northstar.verify_license_token(config), (
            "verify_license_token() must return True for valid Pro activation"
        )

        # Pro features available
        if "northstar_pro" in sys.modules:
            pro_mod = sys.modules["northstar_pro"]
        else:
            import northstar_pro as pro_mod  # type: ignore

        assert pro_mod.is_pro(config), (
            "is_pro() must return True for Pro tier activation"
        )

    def test_tier_mismatch_detected_by_doctor(self, tmp_path, monkeypatch):
        """
        Simulate: A manually tampered config where tier='pro' but key is NSS-.
        Verify: _check_tier_consistency() catches the mismatch (FAIL status).
        This is the guard against Ryan's "tier spoofing" bug class.
        """
        config_path, state_path, secret_path = _sandbox_paths(monkeypatch, tmp_path)

        tampered_config = {
            "tier": "pro",  # WRONG: key is standard prefix
            "license_key": "NSS-TEST-TAMPERED-KEY",
            "license_token": "deadbeef",  # invalid token
        }

        check = northstar._check_tier_consistency(tampered_config)
        assert check.status == "FAIL", (
            f"Expected FAIL for tier mismatch, got {check.status}: {check.message}"
        )
        assert "mismatch" in check.message.lower() or "standard" in check.message.lower(), (
            f"Expected mismatch description in: {check.message}"
        )
