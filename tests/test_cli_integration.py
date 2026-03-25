#!/usr/bin/env python3
"""
Northstar CLI Integration Tests
--------------------------------
End-to-end tests that exercise the full user journey by calling the actual
CLI via subprocess. These tests verify that commands exit cleanly and produce
the expected output, catching regressions that unit tests miss.

Design constraints:
- No network calls (all API integrations disabled in test configs)
- No real API keys
- CI-safe: Python 3.10+, GitHub Actions compatible
- Uses unittest.TestCase for consistency with the existing test suite
- Discovers automatically via pytest and python -m unittest discover
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# ---- Paths -----------------------------------------------------------------

# Resolve the script path relative to this test file so the tests work
# regardless of the current working directory.
_REPO_ROOT = Path(__file__).parent.parent
_SCRIPT = _REPO_ROOT / "scripts" / "northstar.py"


def _run(*args: str, config: Path | None = None) -> subprocess.CompletedProcess:
    """Run ``python3 scripts/northstar.py <args>`` and capture output.

    Parameters
    ----------
    *args:
        CLI arguments forwarded after ``northstar.py``.
    config:
        Optional path to a config file. Appends ``--config <path>`` when given.

    Returns
    -------
    subprocess.CompletedProcess with stdout/stderr captured as str.
    """
    cmd = [sys.executable, str(_SCRIPT), *args]
    if config is not None:
        cmd += ["--config", str(config)]
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30,
    )


def _write_minimal_config(path: Path) -> None:
    """Write a minimal config with every integration disabled.

    No API keys, no network calls. Used for commands that require a config
    file to load (``test``, ``status``).
    """
    config: dict = {
        "tier": "lite",
        "delivery": {"channel": "none"},
        "schedule": {"hour": 6, "minute": 0, "timezone": "America/New_York"},
        "stripe": {"enabled": False},
        "shopify": {"enabled": False},
        "lemonsqueezy": {"enabled": False},
        "gumroad": {"enabled": False},
        "alerts": {
            "payment_failures": True,
            "churn_threshold": 3,
            "large_refund_threshold": 100,
        },
        "format": {
            "emoji": True,
            "include_pacing": True,
            "include_shopify_detail": True,
        },
    }
    path.write_text(json.dumps(config, indent=2))


# ---- Test cases ------------------------------------------------------------


class TestDemoCommand(unittest.TestCase):
    """northstar demo -- no config required, produces sample briefing."""

    def test_exits_zero(self) -> None:
        result = _run("demo")
        self.assertEqual(
            result.returncode, 0,
            f"'northstar demo' should exit 0.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}",
        )

    def test_shows_briefing_header(self) -> None:
        result = _run("demo")
        self.assertIn(
            "Northstar Demo",
            result.stdout,
            "'northstar demo' should print 'Northstar Demo' header.",
        )

    def test_shows_revenue(self) -> None:
        result = _run("demo")
        self.assertIn(
            "Revenue yesterday:",
            result.stdout,
            "'northstar demo' should include 'Revenue yesterday:' line.",
        )

    def test_shows_subscribers(self) -> None:
        result = _run("demo")
        self.assertIn(
            "Active subscribers:",
            result.stdout,
            "'northstar demo' should include 'Active subscribers:' line.",
        )

    def test_shows_month_to_date(self) -> None:
        result = _run("demo")
        self.assertIn(
            "Month-to-date:",
            result.stdout,
            "'northstar demo' should include 'Month-to-date:' line.",
        )

    def test_shows_next_steps(self) -> None:
        result = _run("demo")
        self.assertIn(
            "northstar setup",
            result.stdout,
            "'northstar demo' should mention 'northstar setup' as the next step.",
        )


class TestVersionFlag(unittest.TestCase):
    """northstar --version -- exits 0, shows correct version."""

    def test_exits_zero(self) -> None:
        result = _run("--version")
        self.assertEqual(
            result.returncode, 0,
            f"'northstar --version' should exit 0.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}",
        )

    def test_shows_version_string(self) -> None:
        # argparse prints --version to stdout on Python 3.4+ (stdout by default)
        # but some older argparse versions use stderr; check both.
        result = _run("--version")
        combined = result.stdout + result.stderr
        self.assertIn(
            "Northstar",
            combined,
            "'northstar --version' should include 'Northstar' in output.",
        )

    def test_version_matches_module(self) -> None:
        """Version printed by CLI must match scripts/version.py."""
        # Load the version string directly from the module.
        sys.path.insert(0, str(_REPO_ROOT / "scripts"))
        try:
            import importlib
            import version as version_mod
            importlib.reload(version_mod)  # avoid stale cache
            expected = version_mod.__version__
        finally:
            # Don't leave scripts dir permanently inserted at position 0 for
            # other tests; remove only our insertion.
            if str(_REPO_ROOT / "scripts") in sys.path:
                sys.path.remove(str(_REPO_ROOT / "scripts"))

        result = _run("--version")
        combined = result.stdout + result.stderr
        self.assertIn(
            expected,
            combined,
            f"CLI version output should contain '{expected}'. Got: {combined!r}",
        )


class TestHelpFlag(unittest.TestCase):
    """northstar --help -- exits 0, lists all commands."""

    def test_exits_zero(self) -> None:
        result = _run("--help")
        self.assertEqual(
            result.returncode, 0,
            f"'northstar --help' should exit 0.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}",
        )

    def test_lists_demo_command(self) -> None:
        result = _run("--help")
        self.assertIn("demo", result.stdout)

    def test_lists_run_command(self) -> None:
        result = _run("--help")
        self.assertIn("run", result.stdout)

    def test_lists_test_command(self) -> None:
        result = _run("--help")
        self.assertIn("test", result.stdout)

    def test_lists_status_command(self) -> None:
        result = _run("--help")
        self.assertIn("status", result.stdout)

    def test_lists_setup_command(self) -> None:
        result = _run("--help")
        self.assertIn("setup", result.stdout)

    def test_lists_activate_command(self) -> None:
        result = _run("--help")
        self.assertIn("activate", result.stdout)


class TestTestCommand(unittest.TestCase):
    """northstar test -- dry-run with minimal config (all integrations disabled)."""

    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self._config_path = Path(self._tmpdir.name) / "northstar.json"
        _write_minimal_config(self._config_path)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_exits_zero(self) -> None:
        result = _run("test", config=self._config_path)
        self.assertEqual(
            result.returncode, 0,
            f"'northstar test' should exit 0 with a minimal config.\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}",
        )

    def test_shows_version_header(self) -> None:
        result = _run("test", config=self._config_path)
        self.assertIn(
            "Northstar v",
            result.stdout,
            "'northstar test' should print the 'Northstar v<version>' header.",
        )

    def test_no_data_sources_message(self) -> None:
        """With everything disabled, the CLI should report no data configured."""
        result = _run("test", config=self._config_path)
        self.assertIn(
            "No data sources configured",
            result.stdout,
            "Expected 'No data sources configured' when all integrations are disabled.",
        )

    def test_no_network_calls(self) -> None:
        """Confirm no API requests are attempted (no 'Fetching' lines)."""
        result = _run("test", config=self._config_path)
        self.assertNotIn(
            "Fetching",
            result.stdout,
            "No API fetch should occur when all integrations are disabled.",
        )


class TestStatusCommand(unittest.TestCase):
    """northstar status -- shows config info when a config exists."""

    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self._config_path = Path(self._tmpdir.name) / "northstar.json"
        _write_minimal_config(self._config_path)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_exits_zero(self) -> None:
        result = _run("status", config=self._config_path)
        self.assertEqual(
            result.returncode, 0,
            f"'northstar status' should exit 0 when a config exists.\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}",
        )

    def test_shows_status_header(self) -> None:
        result = _run("status", config=self._config_path)
        self.assertIn(
            "Northstar Status",
            result.stdout,
            "'northstar status' should include 'Northstar Status' header.",
        )

    def test_shows_config_path(self) -> None:
        result = _run("status", config=self._config_path)
        self.assertIn(
            "Config:",
            result.stdout,
            "'northstar status' should show 'Config:' line.",
        )

    def test_shows_tier(self) -> None:
        result = _run("status", config=self._config_path)
        self.assertIn(
            "Tier:",
            result.stdout,
            "'northstar status' should show 'Tier:' line.",
        )

    def test_shows_stripe_disabled(self) -> None:
        result = _run("status", config=self._config_path)
        self.assertIn(
            "Stripe:",
            result.stdout,
            "'northstar status' should show 'Stripe:' integration status.",
        )

    def test_shows_run_instructions(self) -> None:
        result = _run("status", config=self._config_path)
        self.assertIn(
            "northstar run",
            result.stdout,
            "'northstar status' should mention 'northstar run' for next steps.",
        )


class TestErrorHandling(unittest.TestCase):
    """Edge cases: missing config exits non-zero with helpful output."""

    def test_run_without_config_exits_nonzero(self) -> None:
        """'northstar run' with a non-existent config should exit 1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            missing = Path(tmpdir) / "does_not_exist.json"
            result = _run("run", config=missing)
            self.assertNotEqual(
                result.returncode, 0,
                "'northstar run' with a missing config should exit non-zero.",
            )

    def test_run_without_config_shows_helpful_message(self) -> None:
        """Missing config output should suggest 'northstar setup'."""
        with tempfile.TemporaryDirectory() as tmpdir:
            missing = Path(tmpdir) / "does_not_exist.json"
            result = _run("run", config=missing)
            self.assertIn(
                "northstar setup",
                result.stdout + result.stderr,
                "Error output should suggest 'northstar setup' when config is missing.",
            )


# ---- Entry point -----------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
