#!/usr/bin/env python3
"""
Northstar Snapshot Tests

Freeze the expected text output of key output-producing functions.
If output changes, the test fails until snapshots are explicitly regenerated.

Usage:
  Run tests:             python3 -m pytest tests/test_snapshots.py -v
  Regenerate snapshots:  UPDATE_SNAPSHOTS=1 python3 -m pytest tests/test_snapshots.py -v
"""

import os
import sys
import io
from pathlib import Path

import pytest

# Add scripts dir to path
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from northstar import cmd_demo, build_briefing

# ---- Snapshot helpers -------------------------------------------------------

SNAPSHOTS_DIR = Path(__file__).parent / "snapshots"
UPDATE_SNAPSHOTS = os.environ.get("UPDATE_SNAPSHOTS", "").strip() in ("1", "true", "yes")


def assert_snapshot(name: str, actual: str):
    """Compare actual output against a frozen snapshot file.

    If the snapshot doesn't exist yet, create it (first-run seeds).
    If UPDATE_SNAPSHOTS=1, overwrite the snapshot regardless.
    """
    SNAPSHOTS_DIR.mkdir(exist_ok=True)
    snap_file = SNAPSHOTS_DIR / f"{name}.txt"

    if not snap_file.exists() or UPDATE_SNAPSHOTS:
        snap_file.write_text(actual, encoding="utf-8")
        if UPDATE_SNAPSHOTS:
            print(f"\n[snapshot] Updated: {snap_file.name}")
        else:
            print(f"\n[snapshot] Created: {snap_file.name}")
        return  # First run always passes

    expected = snap_file.read_text(encoding="utf-8")
    if actual != expected:
        diff_lines = []
        exp_lines = expected.splitlines()
        act_lines = actual.splitlines()
        max_len = max(len(exp_lines), len(act_lines))
        for i in range(max_len):
            exp_line = exp_lines[i] if i < len(exp_lines) else "<missing>"
            act_line = act_lines[i] if i < len(act_lines) else "<missing>"
            if exp_line != act_line:
                diff_lines.append(f"  Line {i+1}:")
                diff_lines.append(f"    expected: {exp_line!r}")
                diff_lines.append(f"    actual:   {act_line!r}")
        diff_str = "\n".join(diff_lines)
        pytest.fail(
            f"Snapshot mismatch for '{name}'.\n"
            f"Run with UPDATE_SNAPSHOTS=1 to regenerate.\n\n"
            f"Differences:\n{diff_str}"
        )


# ---- Mock data fixtures -----------------------------------------------------

MOCK_CONFIG = {
    "business_name": "Acme Corp",
    "tier": "pro",
    "delivery": {"channel": "none"},
    "stripe": {"enabled": True, "monthly_revenue_goal": 15000},
    "shopify": {"enabled": True},
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

# Stripe mock - uses actual build_briefing field names
MOCK_STRIPE = {
    "revenue_yesterday": 316.13,  # 9800 / 31 days ≈ daily run rate
    "revenue_last_week_same_day": 290.00,
    "wow_change_pct": 9.0,
    "revenue_mtd": 9800.00,
    "goal_dollars": 15000.00,
    "goal_pct": 65.0,
    "days_remaining": 7,
    "on_track": True,
    "projected_month": 15200.00,
    "active_subs": 48,
    "new_subs": 3,
    "churned_subs": 1,
    "payment_failures": 2,
    "retries_pending": 0,
}

# Shopify mock - uses actual build_briefing field names
MOCK_SHOPIFY = {
    "orders_total": 47,
    "orders_fulfilled": 42,
    "orders_open": 5,
    "refunds_count": 2,
    "refund_total": 89.50,
    "top_product": "Widget Pro",
    "top_product_units": 15,
}

# Gumroad mock
MOCK_GUMROAD = {
    "source": "gumroad",
    "revenue_yesterday": 145.00,
    "revenue_last_week_same_day": 120.00,
    "wow_change_pct": 20.8,
    "revenue_mtd": 2100.00,
    "goal_dollars": 5000.00,
    "goal_pct": 42.0,
    "days_remaining": 7,
    "on_track": False,
    "projected_month": 3200.00,
    "sales_count": 8,
    "refunds_count": 0,
    "refund_total": 0.0,
}

# Lemon Squeezy mock
MOCK_LEMON = {
    "revenue_yesterday": 89.00,
    "revenue_last_week_same_day": 75.00,
    "wow_change_pct": 18.7,
    "revenue_mtd": 1200.00,
    "goal_dollars": 3000.00,
    "goal_pct": 40.0,
    "days_remaining": 7,
    "on_track": False,
    "projected_month": 1800.00,
    "active_subs": 12,
    "new_subs": 1,
    "churned_subs": 0,
    "payment_failures": 0,
    "retries_pending": 0,
}


# ---- Tests ------------------------------------------------------------------


class TestCmdDemoSnapshot:
    """Snapshot test for cmd_demo() - the most important new-user output."""

    def test_cmd_demo_output(self, capsys):
        """cmd_demo() output must match frozen snapshot."""
        cmd_demo()
        captured = capsys.readouterr()
        output = captured.out

        # Strip the date line since it changes daily
        # We normalize the date in the briefing header for stable snapshots
        lines = output.splitlines()
        normalized_lines = []
        for line in lines:
            # Normalize the "📊 Northstar Daily Briefing - <date>" line
            if "Northstar Daily Briefing" in line:
                normalized_lines.append("📊 Northstar Daily Briefing - <DATE>")
            else:
                normalized_lines.append(line)
        normalized = "\n".join(normalized_lines)
        if output.endswith("\n"):
            normalized += "\n"

        assert_snapshot("cmd_demo", normalized)


class TestBuildBriefingSnapshots:
    """Snapshot tests for build_briefing() with various data combinations."""

    def _normalize(self, text: str) -> str:
        """Normalize date in briefing header for stable snapshot comparison."""
        lines = text.splitlines()
        normalized = []
        for line in lines:
            if "Northstar Daily Briefing" in line:
                normalized.append("📊 Northstar Daily Briefing - <DATE>")
            else:
                normalized.append(line)
        return "\n".join(normalized)

    def test_stripe_only(self):
        """build_briefing() with only Stripe data."""
        result = build_briefing(MOCK_CONFIG, MOCK_STRIPE, None)
        assert_snapshot("briefing_stripe_only", self._normalize(result))

    def test_shopify_only(self):
        """build_briefing() with only Shopify data."""
        result = build_briefing(MOCK_CONFIG, None, MOCK_SHOPIFY)
        assert_snapshot("briefing_shopify_only", self._normalize(result))

    def test_all_sources(self):
        """build_briefing() with Stripe + Shopify + Gumroad + Lemon Squeezy."""
        result = build_briefing(
            MOCK_CONFIG,
            MOCK_STRIPE,
            MOCK_SHOPIFY,
            MOCK_LEMON,
            MOCK_GUMROAD,
        )
        assert_snapshot("briefing_all_sources", self._normalize(result))

    def test_no_data(self):
        """build_briefing() with all sources None - should produce minimal output."""
        result = build_briefing(MOCK_CONFIG, None, None, None, None)
        assert_snapshot("briefing_no_data", self._normalize(result))
