#!/usr/bin/env python3
"""
Tests for northstar doctor command.
Each check is tested in isolation using mocks.
"""

import sys
import json
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import northstar
from northstar import (
    DiagnosticCheck,
    DiagnosticReport,
    _mask_secret,
    _check_python_version,
    _check_dependencies,
    _check_config_file,
    _check_stripe_key,
    _check_shopify_config,
    _check_license_key,
    _check_delivery_channel,
    _check_tier_consistency,
    _print_doctor_report,
    cmd_doctor,
)


# ---- DiagnosticCheck / DiagnosticReport ------------------------------------

class TestDiagnosticCheck(unittest.TestCase):
    def test_basic_pass(self):
        c = DiagnosticCheck(name="Test", status="PASS", message="All good")
        self.assertEqual(c.status, "PASS")
        self.assertIsNone(c.fix)

    def test_with_fix(self):
        c = DiagnosticCheck(name="Test", status="FAIL", message="Bad", fix="Do X")
        self.assertEqual(c.fix, "Do X")


class TestDiagnosticReport(unittest.TestCase):
    def test_summary_counts(self):
        report = DiagnosticReport()
        report.checks = [
            DiagnosticCheck("A", "PASS", "ok"),
            DiagnosticCheck("B", "PASS", "ok"),
            DiagnosticCheck("C", "WARN", "meh"),
            DiagnosticCheck("D", "FAIL", "bad"),
        ]
        s = report.summary
        self.assertEqual(s["passed"], 2)
        self.assertEqual(s["warned"], 1)
        self.assertEqual(s["failed"], 1)

    def test_empty_report(self):
        report = DiagnosticReport()
        s = report.summary
        self.assertEqual(s["passed"], 0)
        self.assertEqual(s["warned"], 0)
        self.assertEqual(s["failed"], 0)


# ---- _mask_secret ----------------------------------------------------------

class TestMaskSecret(unittest.TestCase):
    def test_long_key_masked(self):
        key = "sk_live_ABCDEFGHIJKLMNOP"
        masked = _mask_secret(key)
        self.assertEqual(masked, "sk_live***")
        self.assertNotIn("ABCDEFGHIJKLMNOP", masked)

    def test_short_key_masked(self):
        masked = _mask_secret("abc")
        self.assertIn("***", masked)
        self.assertNotIn("bc", masked)

    def test_empty_key(self):
        self.assertEqual(_mask_secret(""), "(empty)")

    def test_no_full_key_in_output(self):
        key = "sk_test_supersecretkey12345"
        masked = _mask_secret(key)
        # Full key must NOT appear in output
        self.assertNotIn(key, masked)
        # First 7 chars should appear
        self.assertIn(key[:7], masked)
        # Everything after char 7 must not appear (as substring)
        self.assertNotIn(key[7:], masked)


# ---- _check_python_version -------------------------------------------------

class TestCheckPythonVersion(unittest.TestCase):
    def test_pass_3_12(self):
        with patch.object(sys, "version_info", (3, 12, 0)):
            check = _check_python_version()
        self.assertEqual(check.status, "PASS")

    def test_pass_3_10(self):
        with patch.object(sys, "version_info", (3, 10, 0)):
            check = _check_python_version()
        self.assertEqual(check.status, "PASS")

    def test_warn_3_9(self):
        with patch.object(sys, "version_info", (3, 9, 7)):
            check = _check_python_version()
        self.assertEqual(check.status, "WARN")
        self.assertIsNotNone(check.fix)

    def test_fail_3_8(self):
        with patch.object(sys, "version_info", (3, 8, 10)):
            check = _check_python_version()
        self.assertEqual(check.status, "FAIL")
        self.assertIsNotNone(check.fix)

    def test_fail_2_7(self):
        with patch.object(sys, "version_info", (2, 7, 18)):
            check = _check_python_version()
        self.assertEqual(check.status, "FAIL")


# ---- _check_dependencies ---------------------------------------------------

class TestCheckDependencies(unittest.TestCase):
    def test_pass_all_available(self):
        # All standard library modules should always be available
        check = _check_dependencies()
        self.assertEqual(check.status, "PASS")

    def test_fail_missing_module(self):
        original_import = __builtins__.__import__ if hasattr(__builtins__, "__import__") else __import__

        def fake_import(name, *args, **kwargs):
            if name == "requests":
                raise ImportError("No module named 'requests'")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=fake_import):
            check = _check_dependencies()
        self.assertEqual(check.status, "FAIL")
        self.assertIn("requests", check.message)
        self.assertIn("pip3", check.fix)


# ---- _check_config_file ----------------------------------------------------

class TestCheckConfigFile(unittest.TestCase):
    def test_pass_valid_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg_path = Path(tmpdir) / "config.json"
            cfg_path.write_text(json.dumps({"tier": "lite"}))
            check, config = _check_config_file(cfg_path)
        self.assertEqual(check.status, "PASS")
        self.assertIsNotNone(config)
        self.assertEqual(config["tier"], "lite")

    def test_fail_missing_file(self):
        missing = Path("/nonexistent/path/config.json")
        check, config = _check_config_file(missing)
        self.assertEqual(check.status, "FAIL")
        self.assertIsNone(config)
        self.assertIn("northstar setup", check.fix)

    def test_fail_invalid_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg_path = Path(tmpdir) / "config.json"
            cfg_path.write_text("{bad json !!!")
            check, config = _check_config_file(cfg_path)
        self.assertEqual(check.status, "FAIL")
        self.assertIsNone(config)

    def test_fresh_install_no_config(self):
        """On a fresh install with no config, should FAIL gracefully, not traceback."""
        missing = Path("/no/config/here.json")
        try:
            check, config = _check_config_file(missing)
            self.assertEqual(check.status, "FAIL")
        except Exception as e:
            self.fail(f"Raised unexpected exception: {e}")


# ---- _check_stripe_key -----------------------------------------------------

class TestCheckStripeKey(unittest.TestCase):
    def test_warn_no_config(self):
        check = _check_stripe_key(None, offline=True)
        self.assertEqual(check.status, "WARN")

    def test_warn_stripe_not_enabled(self):
        config = {"stripe": {"enabled": False}}
        check = _check_stripe_key(config, offline=True)
        self.assertEqual(check.status, "WARN")

    def test_warn_placeholder_key(self):
        config = {"stripe": {"enabled": True, "api_key": "sk_live_YOUR_KEY_HERE"}}
        check = _check_stripe_key(config, offline=True)
        self.assertEqual(check.status, "WARN")

    def test_fail_malformed_key(self):
        config = {"stripe": {"enabled": True, "api_key": "not_a_valid_key"}}
        check = _check_stripe_key(config, offline=True)
        self.assertEqual(check.status, "FAIL")

    def test_pass_valid_format_offline(self):
        config = {"stripe": {"enabled": True, "api_key": "sk_test_abc123xyz"}}
        check = _check_stripe_key(config, offline=True)
        self.assertEqual(check.status, "PASS")
        # Key must not be in message unmasked
        self.assertNotIn("sk_test_abc123xyz", check.message)
        # First 7 chars should be visible
        self.assertIn("sk_test", check.message)

    def test_pass_live_key_format_offline(self):
        config = {"stripe": {"enabled": True, "api_key": "sk_live_abcdefghijklmnop"}}
        check = _check_stripe_key(config, offline=True)
        self.assertEqual(check.status, "PASS")

    def test_pass_restricted_key_format_offline(self):
        config = {"stripe": {"enabled": True, "api_key": "rk_test_abcdefghijklmnop"}}
        check = _check_stripe_key(config, offline=True)
        self.assertEqual(check.status, "PASS")

    def test_network_pass(self):
        """Simulate successful Stripe API check."""
        config = {"stripe": {"enabled": True, "api_key": "sk_test_validkey123456"}}

        mock_response = MagicMock()
        mock_response.read.return_value = b'{"object": "balance"}'
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_response):
            check = _check_stripe_key(config, offline=False)
        self.assertEqual(check.status, "PASS")
        # Verify key is masked
        self.assertNotIn("validkey123456", check.message)

    def test_network_401_fail(self):
        """Simulate Stripe 401 (invalid key)."""
        import urllib.error

        config = {"stripe": {"enabled": True, "api_key": "sk_test_badkey12345678"}}

        http_error = urllib.error.HTTPError(
            url="https://api.stripe.com/v1/balance",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=None,
        )

        with patch("urllib.request.urlopen", side_effect=http_error):
            check = _check_stripe_key(config, offline=False)
        self.assertEqual(check.status, "FAIL")
        self.assertIn("401", check.message)

    def test_network_failure_warn(self):
        """Network failure should WARN, not FAIL."""
        import socket

        config = {"stripe": {"enabled": True, "api_key": "sk_test_goodformatkey"}}

        with patch("urllib.request.urlopen", side_effect=socket.timeout("timed out")):
            check = _check_stripe_key(config, offline=False)
        self.assertEqual(check.status, "WARN")

    def test_secret_not_in_output(self):
        """Full API key must never appear in check output."""
        full_key = "sk_test_SuperSecretKey9999999"
        config = {"stripe": {"enabled": True, "api_key": full_key}}
        check = _check_stripe_key(config, offline=True)
        self.assertNotIn(full_key, check.message)
        if check.fix:
            self.assertNotIn(full_key, check.fix)


# ---- _check_shopify_config -------------------------------------------------

class TestCheckShopifyConfig(unittest.TestCase):
    def test_pass_lite_tier_no_shopify(self):
        config = {"tier": "lite", "shopify": {"enabled": False}}
        check = _check_shopify_config(config)
        self.assertEqual(check.status, "PASS")

    def test_warn_standard_no_shopify(self):
        config = {"tier": "standard", "shopify": {"enabled": False}}
        check = _check_shopify_config(config)
        self.assertEqual(check.status, "WARN")

    def test_pass_shopify_configured(self):
        config = {
            "tier": "standard",
            "shopify": {
                "enabled": True,
                "shop_domain": "mystore.myshopify.com",
                "access_token": "shpat_realtoken123",
            },
        }
        check = _check_shopify_config(config)
        self.assertEqual(check.status, "PASS")

    def test_warn_shopify_missing_fields(self):
        config = {
            "tier": "pro",
            "shopify": {
                "enabled": True,
                "shop_domain": "",
                "access_token": "",
            },
        }
        check = _check_shopify_config(config)
        self.assertEqual(check.status, "WARN")

    def test_warn_no_config(self):
        check = _check_shopify_config(None)
        self.assertEqual(check.status, "WARN")


# ---- _check_license_key ----------------------------------------------------

class TestCheckLicenseKey(unittest.TestCase):
    def test_warn_free_tier_no_key(self):
        config = {"tier": "lite"}
        check = _check_license_key(config)
        self.assertEqual(check.status, "WARN")

    def test_warn_no_config(self):
        check = _check_license_key(None)
        self.assertEqual(check.status, "WARN")

    def test_fail_key_present_invalid_token(self):
        """Key present but HMAC token is wrong - should FAIL."""
        config = {
            "tier": "pro",
            "license_key": "NSP-ABCD-1234-EFGH-5678",
            "license_token": "deadbeefdeadbeefdeadbeefdeadbeef",  # wrong token
        }
        check = _check_license_key(config)
        self.assertEqual(check.status, "FAIL")
        self.assertIn("northstar activate", check.fix)

    def test_pass_valid_token(self):
        """Key + matching HMAC token should PASS."""
        key = "NSP-VALID-TEST-KEY-9999"
        tier = "pro"
        token = northstar.sign_license_token(key, tier)
        config = {
            "tier": tier,
            "license_key": key,
            "license_token": token,
        }
        check = _check_license_key(config)
        self.assertEqual(check.status, "PASS")

    def test_pass_does_not_reveal_key(self):
        """Full license key must not appear in output."""
        key = "NSP-SUPER-SECRET-KEY-12345"
        tier = "pro"
        token = northstar.sign_license_token(key, tier)
        config = {"tier": tier, "license_key": key, "license_token": token}
        check = _check_license_key(config)
        self.assertNotIn(key, check.message)


# ---- _check_delivery_channel -----------------------------------------------

class TestCheckDeliveryChannel(unittest.TestCase):
    def test_warn_no_channel(self):
        config = {"delivery": {"channel": "none"}}
        check = _check_delivery_channel(config)
        self.assertEqual(check.status, "WARN")

    def test_warn_no_delivery_key(self):
        config = {}
        check = _check_delivery_channel(config)
        self.assertEqual(check.status, "WARN")

    def test_pass_imessage(self):
        config = {"delivery": {"channel": "imessage", "recipient": "+15551234567"}}
        check = _check_delivery_channel(config)
        self.assertEqual(check.status, "PASS")

    def test_warn_imessage_no_recipient(self):
        config = {"delivery": {"channel": "imessage"}}
        check = _check_delivery_channel(config)
        self.assertEqual(check.status, "WARN")

    def test_pass_slack(self):
        config = {"delivery": {"channel": "slack", "slack_webhook": "https://hooks.slack.com/..."}}
        check = _check_delivery_channel(config)
        self.assertEqual(check.status, "PASS")

    def test_warn_slack_no_webhook(self):
        config = {"delivery": {"channel": "slack"}}
        check = _check_delivery_channel(config)
        self.assertEqual(check.status, "WARN")

    def test_pass_telegram(self):
        config = {
            "delivery": {
                "channel": "telegram",
                "telegram_bot_token": "123456:ABC",
                "telegram_chat_id": "-1001234567",
            }
        }
        check = _check_delivery_channel(config)
        self.assertEqual(check.status, "PASS")

    def test_warn_telegram_incomplete(self):
        config = {"delivery": {"channel": "telegram", "telegram_bot_token": "123:ABC"}}
        check = _check_delivery_channel(config)
        self.assertEqual(check.status, "WARN")

    def test_pass_email(self):
        config = {"delivery": {"channel": "email", "email_to": "user@example.com"}}
        check = _check_delivery_channel(config)
        self.assertEqual(check.status, "PASS")

    def test_warn_no_config(self):
        check = _check_delivery_channel(None)
        self.assertEqual(check.status, "WARN")


# ---- _check_tier_consistency -----------------------------------------------

class TestCheckTierConsistency(unittest.TestCase):
    def test_pass_lite_no_key(self):
        config = {"tier": "lite"}
        check = _check_tier_consistency(config)
        self.assertEqual(check.status, "PASS")

    def test_pass_pro_nsp_key(self):
        config = {"tier": "pro", "license_key": "NSP-ABCD-1234-EFGH"}
        check = _check_tier_consistency(config)
        self.assertEqual(check.status, "PASS")

    def test_pass_standard_nss_key(self):
        config = {"tier": "standard", "license_key": "NSS-ABCD-1234-EFGH"}
        check = _check_tier_consistency(config)
        self.assertEqual(check.status, "PASS")

    def test_fail_tier_mismatch(self):
        """Pro key but config says standard = FAIL."""
        config = {"tier": "standard", "license_key": "NSP-ABCD-1234-EFGH"}
        check = _check_tier_consistency(config)
        self.assertEqual(check.status, "FAIL")
        self.assertIn("mismatch", check.message)

    def test_fail_standard_key_with_pro_tier(self):
        config = {"tier": "pro", "license_key": "NSS-ABCD-1234-EFGH"}
        check = _check_tier_consistency(config)
        self.assertEqual(check.status, "FAIL")

    def test_fail_tier_set_but_no_key(self):
        config = {"tier": "pro"}
        check = _check_tier_consistency(config)
        self.assertEqual(check.status, "FAIL")

    def test_warn_no_config(self):
        check = _check_tier_consistency(None)
        self.assertEqual(check.status, "WARN")


# ---- cmd_doctor integration ------------------------------------------------

class TestCmdDoctor(unittest.TestCase):
    def test_unconfigured_machine_no_traceback(self):
        """On completely unconfigured machine, should output gracefully, no traceback."""
        missing_path = Path("/no/config/here.json")
        try:
            cmd_doctor(config_path=missing_path, offline=True)
        except SystemExit:
            pass  # sys.exit() is acceptable in doctor
        except Exception as e:
            self.fail(f"cmd_doctor raised unexpected exception: {e}")

    def test_offline_flag_skips_network(self):
        """--offline flag should skip Stripe network check."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg_path = Path(tmpdir) / "config.json"
            cfg_path.write_text(json.dumps({
                "tier": "lite",
                "stripe": {"enabled": True, "api_key": "sk_test_fake12345"},
                "delivery": {"channel": "none"},
            }))
            # With offline=True, urlopen should never be called
            with patch("urllib.request.urlopen") as mock_urlopen:
                cmd_doctor(config_path=cfg_path, offline=True)
                mock_urlopen.assert_not_called()

    def test_fresh_install_all_fails_no_traceback(self):
        """Doctor on a machine with no config should produce FAIL checks, not crash."""
        missing_path = Path("/absolutely/not/there.json")
        import io
        from contextlib import redirect_stdout

        output = io.StringIO()
        try:
            with redirect_stdout(output):
                cmd_doctor(config_path=missing_path, offline=True)
        except Exception as e:
            self.fail(f"Unexpected exception: {e}")

        printed = output.getvalue()
        self.assertIn("Northstar Doctor", printed)
        self.assertIn("[FAIL]", printed)
        self.assertIn("Result:", printed)

    def test_full_pass_scenario(self):
        """Fully configured machine should produce mostly PASS results."""
        import io
        from contextlib import redirect_stdout

        key = "NSP-GOOD-KEY-12345"
        tier = "pro"
        token = northstar.sign_license_token(key, tier)

        with tempfile.TemporaryDirectory() as tmpdir:
            cfg_path = Path(tmpdir) / "config.json"
            cfg_path.write_text(json.dumps({
                "tier": tier,
                "license_key": key,
                "license_token": token,
                "stripe": {"enabled": True, "api_key": "sk_test_goodkey12345"},
                "shopify": {
                    "enabled": True,
                    "shop_domain": "mystore.myshopify.com",
                    "access_token": "shpat_realtoken456",
                },
                "delivery": {"channel": "slack", "slack_webhook": "https://hooks.slack.com/test"},
            }))
            output = io.StringIO()
            with redirect_stdout(output):
                cmd_doctor(config_path=cfg_path, offline=True)

        printed = output.getvalue()
        self.assertIn("[PASS]", printed)
        self.assertIn("Result:", printed)

    def test_output_format(self):
        """Verify output includes header and result line."""
        import io
        from contextlib import redirect_stdout

        missing_path = Path("/no/config.json")
        output = io.StringIO()
        with redirect_stdout(output):
            cmd_doctor(config_path=missing_path, offline=True)

        printed = output.getvalue()
        self.assertIn("Northstar Doctor - Environment Check", printed)
        self.assertIn("=====", printed)
        self.assertIn("Result:", printed)
        self.assertIn("passed", printed)
        self.assertIn("warnings", printed)
        self.assertIn("failures", printed)

    def test_no_full_keys_in_output(self):
        """Full API keys and license keys must never appear in doctor output."""
        import io
        from contextlib import redirect_stdout

        full_stripe_key = "sk_test_SUPERSECRETKEY99999"
        full_license_key = "NSP-FULL-LICENSE-KEY-HERE"
        token = northstar.sign_license_token(full_license_key, "pro")

        with tempfile.TemporaryDirectory() as tmpdir:
            cfg_path = Path(tmpdir) / "config.json"
            cfg_path.write_text(json.dumps({
                "tier": "pro",
                "license_key": full_license_key,
                "license_token": token,
                "stripe": {"enabled": True, "api_key": full_stripe_key},
                "delivery": {"channel": "none"},
            }))
            output = io.StringIO()
            with redirect_stdout(output):
                cmd_doctor(config_path=cfg_path, offline=True)

        printed = output.getvalue()
        # Full keys must NOT appear
        self.assertNotIn(full_stripe_key, printed)
        self.assertNotIn(full_license_key, printed)

    def test_returns_1_on_failures(self):
        """cmd_doctor should return 1 when there are failures."""
        missing_path = Path("/no/config.json")
        import io
        from contextlib import redirect_stdout
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = cmd_doctor(config_path=missing_path, offline=True)
        # Missing config = FAIL, so exit code should be 1
        self.assertEqual(exit_code, 1)

    def test_returns_0_on_pass_or_warn_only(self):
        """cmd_doctor should return 0 when no failures (only PASS and WARN)."""
        key = "NSP-GOOD-KEY-12345"
        tier = "pro"
        token = northstar.sign_license_token(key, tier)

        with tempfile.TemporaryDirectory() as tmpdir:
            cfg_path = Path(tmpdir) / "config.json"
            cfg_path.write_text(json.dumps({
                "tier": tier,
                "license_key": key,
                "license_token": token,
                "stripe": {"enabled": True, "api_key": "sk_test_valid12345678"},
                "shopify": {
                    "enabled": True,
                    "shop_domain": "store.myshopify.com",
                    "access_token": "shpat_real123",
                },
                "delivery": {"channel": "slack", "slack_webhook": "https://hooks.slack.com/abc"},
            }))
            import io
            from contextlib import redirect_stdout
            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = cmd_doctor(config_path=cfg_path, offline=True)
        self.assertEqual(exit_code, 0)


# ---- _print_doctor_report --------------------------------------------------

class TestPrintDoctorReport(unittest.TestCase):
    def test_output_contains_all_statuses(self):
        import io
        from contextlib import redirect_stdout

        report = DiagnosticReport()
        report.checks = [
            DiagnosticCheck("Check A", "PASS", "All good"),
            DiagnosticCheck("Check B", "WARN", "Be careful", fix="Fix it"),
            DiagnosticCheck("Check C", "FAIL", "Broken", fix="Fix this now"),
        ]
        output = io.StringIO()
        with redirect_stdout(output):
            _print_doctor_report(report)
        printed = output.getvalue()
        self.assertIn("[PASS]", printed)
        self.assertIn("[WARN]", printed)
        self.assertIn("[FAIL]", printed)
        self.assertIn("Fix it", printed)
        self.assertIn("Fix this now", printed)
        self.assertIn("1 passed", printed)
        self.assertIn("1 warnings", printed)
        self.assertIn("1 failures", printed)

    def test_fix_arrow_format(self):
        """Fix lines should use the arrow indicator."""
        import io
        from contextlib import redirect_stdout

        report = DiagnosticReport()
        report.checks = [
            DiagnosticCheck("Test", "WARN", "Meh", fix="Run: northstar setup"),
        ]
        output = io.StringIO()
        with redirect_stdout(output):
            _print_doctor_report(report)
        self.assertIn("→", output.getvalue())


if __name__ == "__main__":
    unittest.main()
