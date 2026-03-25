#!/usr/bin/env python3
"""
Scheduler & Idempotency Tests
Tests state management, scheduling display, and run counter behavior.
Phase 2 Step 7
"""

import sys
import json
import io
import os
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import northstar


# ---- Fixtures --------------------------------------------------------------

MINIMAL_CONFIG = {
    "tier": "lite",
    "delivery": {"channel": "none"},
    "stripe": {"enabled": False},
    "shopify": {"enabled": False},
    "format": {"emoji": True, "include_pacing": True},
    "alerts": {},
    "schedule": {"hour": 7, "minute": 30, "timezone": "America/New_York"},
}

STRIPE_MOCK = {
    "revenue_yesterday": 500.0,
    "revenue_last_week_same_day": 400.0,
    "wow_change_pct": 25.0,
    "revenue_mtd": 5000.0,
    "goal_dollars": 10000.0,
    "goal_pct": 50.0,
    "days_remaining": 15,
    "on_track": True,
    "projected_month": 10000.0,
    "active_subs": 50,
    "new_subs": 2,
    "churned_subs": 0,
    "payment_failures": 0,
    "retries_pending": 0,
}


# ---- State: load_state / save_state ----------------------------------------

class TestLoadStateFresh(unittest.TestCase):
    """test_load_state_fresh: non-existent file returns empty dict (with defaults)."""

    def test_load_state_fresh(self):
        non_existent = Path("/tmp/northstar_test_nonexistent_xyz123.json")
        if non_existent.exists():
            non_existent.unlink()
        with patch.object(northstar, "STATE_PATH", non_existent):
            state = northstar.load_state()
        # Should return a dict (possibly with default keys, not crash)
        self.assertIsInstance(state, dict)
        # Runs counter should be falsy / zero
        self.assertEqual(state.get("runs", 0), 0)


class TestSaveAndLoadRoundtrip(unittest.TestCase):
    """test_save_and_load_roundtrip: save state, load it back, verify."""

    def test_roundtrip(self):
        tmp = Path("/tmp/northstar_test_roundtrip.json")
        if tmp.exists():
            tmp.unlink()
        payload = {"last_run": "2026-03-24T06:00:00", "runs": 7, "custom": "hello"}
        with patch.object(northstar, "STATE_PATH", tmp):
            northstar.save_state(payload)
            loaded = northstar.load_state()
        self.assertEqual(loaded["last_run"], "2026-03-24T06:00:00")
        self.assertEqual(loaded["runs"], 7)
        self.assertEqual(loaded["custom"], "hello")
        tmp.unlink(missing_ok=True)


class TestLoadStateCorrupted(unittest.TestCase):
    """test_load_state_corrupted: broken JSON — document behavior (crash or empty dict)."""

    def test_corrupted_json(self):
        tmp = Path("/tmp/northstar_test_corrupted.json")
        tmp.write_text("{ this is not valid json !!!")
        with patch.object(northstar, "STATE_PATH", tmp):
            try:
                state = northstar.load_state()
                # If it returns something, it must be a dict
                self.assertIsInstance(state, dict)
            except (json.JSONDecodeError, ValueError):
                # Acceptable: northstar raises on corrupt JSON (no guard)
                # Document: no corruption recovery is implemented
                pass
        tmp.unlink(missing_ok=True)


class TestStatePersistsAcrossLoads(unittest.TestCase):
    """test_state_persists_across_loads: save, modify in memory, load again — file version wins."""

    def test_file_version_not_memory(self):
        tmp = Path("/tmp/northstar_test_persist.json")
        if tmp.exists():
            tmp.unlink()
        original = {"runs": 3, "last_run": "2026-01-01T00:00:00"}
        with patch.object(northstar, "STATE_PATH", tmp):
            northstar.save_state(original)
            # Modify the in-memory dict (should NOT affect what's on disk)
            original["runs"] = 999
            original["tampered"] = True
            # Now load fresh from disk
            loaded = northstar.load_state()
        # Disk has runs=3, not 999
        self.assertEqual(loaded["runs"], 3)
        self.assertNotIn("tampered", loaded)
        tmp.unlink(missing_ok=True)


# ---- cmd_run state updates -------------------------------------------------

class TestCmdRunIncrementsState(unittest.TestCase):
    """test_cmd_run_increments_state: after cmd_run, state has last_run and runs=1."""

    def _make_config_with_stripe(self):
        cfg = dict(MINIMAL_CONFIG)
        cfg["stripe"] = {
            "enabled": True,
            "api_key": "sk_test_fake",
            "monthly_revenue_goal": 10000,
            "currency": "usd",
        }
        return cfg

    def test_state_after_one_run(self):
        tmp = Path("/tmp/northstar_test_run_once.json")
        if tmp.exists():
            tmp.unlink()
        config = self._make_config_with_stripe()

        with patch.object(northstar, "STATE_PATH", tmp), \
             patch.object(northstar, "fetch_stripe_metrics", return_value=STRIPE_MOCK), \
             patch.object(northstar, "fetch_shopify_metrics", return_value={}), \
             patch.object(northstar, "deliver", return_value=None):
            northstar.cmd_run(config, dry_run=True)

        self.assertTrue(tmp.exists(), "State file should be written after cmd_run")
        with open(tmp) as f:
            state = json.load(f)
        self.assertEqual(state.get("runs"), 1)
        self.assertIn("last_run", state)
        self.assertIsNotNone(state["last_run"])
        tmp.unlink(missing_ok=True)


class TestCmdRunTwiceIncrements(unittest.TestCase):
    """test_cmd_run_twice_increments: two runs → runs=2."""

    def _make_config_with_stripe(self):
        cfg = dict(MINIMAL_CONFIG)
        cfg["stripe"] = {
            "enabled": True,
            "api_key": "sk_test_fake",
            "monthly_revenue_goal": 10000,
            "currency": "usd",
        }
        return cfg

    def test_state_after_two_runs(self):
        tmp = Path("/tmp/northstar_test_run_twice.json")
        if tmp.exists():
            tmp.unlink()
        config = self._make_config_with_stripe()

        with patch.object(northstar, "STATE_PATH", tmp), \
             patch.object(northstar, "fetch_stripe_metrics", return_value=STRIPE_MOCK), \
             patch.object(northstar, "fetch_shopify_metrics", return_value={}), \
             patch.object(northstar, "deliver", return_value=None):
            northstar.cmd_run(config, dry_run=True)
            northstar.cmd_run(config, dry_run=True)

        with open(tmp) as f:
            state = json.load(f)
        self.assertEqual(state.get("runs"), 2)
        tmp.unlink(missing_ok=True)


class TestDoubleRunNoGuard(unittest.TestCase):
    """
    test_double_run_no_guard: two rapid cmd_runs both succeed.
    Documents: no idempotency guard exists in northstar.
    Two calls to cmd_run() both complete without error and runs increments to 2.
    """

    def _make_config_with_stripe(self):
        cfg = dict(MINIMAL_CONFIG)
        cfg["stripe"] = {
            "enabled": True,
            "api_key": "sk_test_fake",
            "monthly_revenue_goal": 10000,
            "currency": "usd",
        }
        return cfg

    def test_no_idempotency_guard(self):
        tmp = Path("/tmp/northstar_test_no_guard.json")
        if tmp.exists():
            tmp.unlink()
        config = self._make_config_with_stripe()

        with patch.object(northstar, "STATE_PATH", tmp), \
             patch.object(northstar, "fetch_stripe_metrics", return_value=STRIPE_MOCK), \
             patch.object(northstar, "fetch_shopify_metrics", return_value={}), \
             patch.object(northstar, "deliver", return_value=None):
            # Both calls should succeed (no guard prevents second run)
            northstar.cmd_run(config, dry_run=True)
            northstar.cmd_run(config, dry_run=True)

        with open(tmp) as f:
            state = json.load(f)
        # Document: runs=2 confirms no deduplication
        self.assertEqual(state.get("runs"), 2,
            "No idempotency guard: second run increments counter (runs=2)")
        tmp.unlink(missing_ok=True)


# ---- cmd_status schedule display -------------------------------------------

class TestCmdStatusShowsSchedule(unittest.TestCase):
    """test_cmd_status_shows_schedule: schedule line reflects config values."""

    def test_schedule_in_output(self):
        config = dict(MINIMAL_CONFIG)
        config["schedule"] = {"hour": 7, "minute": 30, "timezone": "America/New_York"}

        tmp = Path("/tmp/northstar_test_status_sched.json")
        if tmp.exists():
            tmp.unlink()

        buf = io.StringIO()
        with patch.object(northstar, "STATE_PATH", tmp), \
             patch("sys.stdout", buf):
            northstar.cmd_status(config)

        output = buf.getvalue()
        self.assertIn("07:30", output)
        self.assertIn("America/New_York", output)
        tmp.unlink(missing_ok=True)


class TestCmdStatusDefaultSchedule(unittest.TestCase):
    """test_cmd_status_default_schedule: config with no schedule shows '06:00 UTC'."""

    def test_default_schedule_output(self):
        config = {
            "tier": "lite",
            "delivery": {"channel": "none"},
            "stripe": {"enabled": False},
            "shopify": {"enabled": False},
            # No "schedule" key
        }

        tmp = Path("/tmp/northstar_test_status_default.json")
        if tmp.exists():
            tmp.unlink()

        buf = io.StringIO()
        with patch.object(northstar, "STATE_PATH", tmp), \
             patch("sys.stdout", buf):
            northstar.cmd_status(config)

        output = buf.getvalue()
        self.assertIn("06:00", output)
        self.assertIn("UTC", output)
        tmp.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
