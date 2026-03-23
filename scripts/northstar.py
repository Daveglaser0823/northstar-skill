#!/usr/bin/env python3
"""
Northstar - Daily Business Briefing for OpenClaw
Version: 1.1.0
Author: Eli (AI founder, OpenClaw-native)

Pulls Stripe and Shopify metrics, formats a daily briefing,
and delivers it via iMessage, Slack, or Telegram.
"""

import sys
import json
import argparse
import subprocess
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional

# Pro module (optional - only imported when Pro commands are used)
def _load_pro():
    """Lazy-load the Pro module from the same directory."""
    import importlib.util
    pro_path = Path(__file__).parent / "northstar_pro.py"
    if not pro_path.exists():
        print("Error: northstar_pro.py not found.")
        sys.exit(1)
    spec = importlib.util.spec_from_file_location("northstar_pro", pro_path)
    mod = importlib.util.module_from_spec(spec)
    # Inject this module into sys.modules so northstar_pro can 'from northstar import ...'
    sys.modules["northstar"] = sys.modules[__name__]
    spec.loader.exec_module(mod)
    return mod

# ---- Config ----------------------------------------------------------------

CONFIG_PATH = Path.home() / ".clawd" / "skills" / "northstar" / "config" / "northstar.json"
STATE_PATH = Path.home() / ".clawd" / "skills" / "northstar" / "state.json"

def load_config(config_path: Optional[Path] = None) -> dict:
    path = config_path or CONFIG_PATH
    if not path.exists():
        example = path.parent / "northstar.json.example"
        raise FileNotFoundError(
            f"Config not found at {path}\n"
            f"Copy the example: cp {example} {path}\n"
            f"Then edit with your API keys."
        )
    with open(path) as f:
        return json.load(f)

def load_state() -> dict:
    if STATE_PATH.exists():
        with open(STATE_PATH) as f:
            return json.load(f)
    return {"last_run": None, "runs": 0}

def save_state(state: dict):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)

# ---- Stripe ----------------------------------------------------------------

def fetch_stripe_metrics(api_key: str, goal_dollars: float, currency: str = "usd") -> dict:
    """Fetch yesterday's Stripe metrics."""
    try:
        import stripe
    except ImportError:
        print("Installing stripe package...")
        # macOS Homebrew Python requires --break-system-packages
        installed = False
        for flags in [
            ["--user", "--break-system-packages"],
            ["--user"],
            [],
        ]:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install"] + flags + ["stripe", "-q"],
                capture_output=True
            )
            if result.returncode == 0:
                installed = True
                break
        if not installed:
            print("Error: Could not install stripe package.")
            print("Run manually: pip3 install --user --break-system-packages stripe")
            sys.exit(1)
        import stripe

    stripe.api_key = api_key

    now = datetime.now()
    yesterday_start = datetime(now.year, now.month, now.day) - timedelta(days=1)
    yesterday_end = datetime(now.year, now.month, now.day)
    month_start = datetime(now.year, now.month, 1)
    week_ago_start = yesterday_start - timedelta(days=7)
    week_ago_end = yesterday_end - timedelta(days=7)

    # Yesterday's charges
    charges_yesterday = stripe.Charge.list(
        created={"gte": int(yesterday_start.timestamp()), "lt": int(yesterday_end.timestamp())},
        limit=100
    )
    revenue_yesterday = sum(
        c["amount"] for c in charges_yesterday.auto_paging_iter()
        if c["status"] == "succeeded" and c["currency"] == currency
    ) / 100.0

    # Same day last week (for WoW)
    charges_last_week = stripe.Charge.list(
        created={"gte": int(week_ago_start.timestamp()), "lt": int(week_ago_end.timestamp())},
        limit=100
    )
    revenue_last_week = sum(
        c["amount"] for c in charges_last_week.auto_paging_iter()
        if c["status"] == "succeeded" and c["currency"] == currency
    ) / 100.0

    # Month-to-date revenue
    charges_mtd = stripe.Charge.list(
        created={"gte": int(month_start.timestamp()), "lt": int(yesterday_end.timestamp())},
        limit=100
    )
    revenue_mtd = sum(
        c["amount"] for c in charges_mtd.auto_paging_iter()
        if c["status"] == "succeeded" and c["currency"] == currency
    ) / 100.0

    # Active subscriptions
    active_subs = stripe.Subscription.list(status="active", limit=1)
    total_active = active_subs.get("total_count", 0)
    if total_active == 0:
        # Fallback: count via list if total_count not available
        all_active = list(stripe.Subscription.list(status="active", limit=100).auto_paging_iter())
        total_active = len(all_active)

    # New subscribers yesterday
    new_subs = stripe.Subscription.list(
        created={"gte": int(yesterday_start.timestamp()), "lt": int(yesterday_end.timestamp())},
        status="active",
        limit=100
    )
    new_sub_count = len(list(new_subs.auto_paging_iter()))

    # Churned subscribers yesterday (canceled_at is when cancellation happened)
    canceled_subs = stripe.Subscription.list(
        status="canceled",
        limit=100
    )
    churned_count = sum(
        1 for sub in canceled_subs.auto_paging_iter()
        if sub.get("canceled_at") and
        int(yesterday_start.timestamp()) <= sub["canceled_at"] < int(yesterday_end.timestamp())
    )

    # Payment failures
    failed_charges = stripe.Charge.list(
        created={"gte": int(yesterday_start.timestamp()), "lt": int(yesterday_end.timestamp())},
        limit=100
    )
    payment_failures = len([
        c for c in failed_charges.auto_paging_iter()
        if c["status"] in ("failed",)
    ])
    # Also check for requires_action (retries pending)
    all_recent = stripe.PaymentIntent.list(
        created={"gte": int(yesterday_start.timestamp()), "lt": int(yesterday_end.timestamp())},
        limit=100
    )
    retries_pending = len([
        pi for pi in all_recent.auto_paging_iter()
        if pi["status"] == "requires_payment_method"
    ])

    # WoW change
    wow_change = None
    if revenue_last_week > 0:
        wow_change = ((revenue_yesterday - revenue_last_week) / revenue_last_week) * 100

    # MTD pacing
    days_in_month = (datetime(now.year, now.month % 12 + 1, 1) - timedelta(days=1)).day if now.month < 12 else 31
    days_elapsed = now.day - 1  # days completed
    days_remaining = days_in_month - days_elapsed
    goal_pct = (revenue_mtd / goal_dollars * 100) if goal_dollars > 0 else None
    daily_run_rate = revenue_mtd / days_elapsed if days_elapsed > 0 else 0
    projected_month = daily_run_rate * days_in_month if daily_run_rate > 0 else 0
    on_track = projected_month >= goal_dollars if goal_dollars > 0 else None

    return {
        "revenue_yesterday": revenue_yesterday,
        "revenue_last_week_same_day": revenue_last_week,
        "wow_change_pct": wow_change,
        "revenue_mtd": revenue_mtd,
        "goal_dollars": goal_dollars,
        "goal_pct": goal_pct,
        "days_remaining": days_remaining,
        "on_track": on_track,
        "projected_month": projected_month,
        "active_subs": total_active,
        "new_subs": new_sub_count,
        "churned_subs": churned_count,
        "payment_failures": payment_failures,
        "retries_pending": retries_pending,
    }

# ---- Shopify ---------------------------------------------------------------

def fetch_shopify_metrics(shop_domain: str, access_token: str) -> dict:
    """Fetch yesterday's Shopify metrics."""
    import urllib.request

    now = datetime.now()
    yesterday_start = datetime(now.year, now.month, now.day) - timedelta(days=1)
    yesterday_end = datetime(now.year, now.month, now.day)

    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json",
    }

    def shopify_get(endpoint: str) -> dict:
        url = f"https://{shop_domain}/admin/api/2024-01/{endpoint}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())

    # Yesterday's orders
    params = (
        f"created_at_min={yesterday_start.isoformat()}Z"
        f"&created_at_max={yesterday_end.isoformat()}Z"
        f"&status=any&limit=250"
    )
    orders_data = shopify_get(f"orders.json?{params}")
    orders = orders_data.get("orders", [])

    fulfilled = [o for o in orders if o.get("fulfillment_status") == "fulfilled"]
    unfulfilled = [o for o in orders if o.get("fulfillment_status") != "fulfilled"]
    refunds_count = sum(1 for o in orders if o.get("refunds"))
    refund_total = sum(
        float(r.get("transactions", [{}])[0].get("amount", 0))
        for o in orders
        for r in o.get("refunds", [])
        if r.get("transactions")
    )

    # Top product by units
    product_counts: dict = {}
    for order in fulfilled:
        for item in order.get("line_items", []):
            name = item.get("title", "Unknown")
            qty = item.get("quantity", 0)
            product_counts[name] = product_counts.get(name, 0) + qty
    top_product = max(product_counts, key=product_counts.get) if product_counts else None
    top_product_units = product_counts.get(top_product, 0) if top_product else 0

    return {
        "orders_total": len(orders),
        "orders_fulfilled": len(fulfilled),
        "orders_open": len(unfulfilled),
        "refunds_count": refunds_count,
        "refund_total": refund_total,
        "top_product": top_product,
        "top_product_units": top_product_units,
    }

# ---- Formatting ------------------------------------------------------------

def fmt_currency(amount: float) -> str:
    """Format dollar amount."""
    if amount >= 1000:
        return f"${amount:,.0f}"
    return f"${amount:.2f}"

def fmt_pct(pct: float, sign: bool = True) -> str:
    """Format percentage with sign."""
    s = f"{abs(pct):.0f}%"
    if sign:
        prefix = "+" if pct >= 0 else "-"
        return f"{prefix}{s}"
    return s

def build_briefing(config: dict, stripe_data: Optional[dict], shopify_data: Optional[dict]) -> str:
    """Build the briefing message."""
    now = datetime.now()
    use_emoji = config.get("format", {}).get("emoji", True)
    lines = []

    # Header
    chart = "📊 " if use_emoji else ""
    lines.append(f"{chart}Northstar Daily Briefing - {now.strftime('%B %-d')}")

    # Stripe section
    if stripe_data:
        rev = stripe_data["revenue_yesterday"]
        wow = stripe_data.get("wow_change_pct")

        wow_str = ""
        if wow is not None:
            wow_str = f" ({fmt_pct(wow)} vs last week)"

        lines.append(f"Revenue yesterday: {fmt_currency(rev)}{wow_str}")

        # Subscribers
        active = stripe_data["active_subs"]
        new = stripe_data["new_subs"]
        churned = stripe_data["churned_subs"]
        sub_detail = []
        if new > 0:
            sub_detail.append(f"+{new} new")
        if churned > 0:
            sub_detail.append(f"-{churned} churn")
        sub_str = f" ({', '.join(sub_detail)})" if sub_detail else ""
        lines.append(f"Active subscribers: {active:,}{sub_str}")

        # MTD
        if stripe_data.get("goal_pct") is not None:
            mtd = stripe_data["revenue_mtd"]
            goal = stripe_data["goal_dollars"]
            pct = stripe_data["goal_pct"]
            lines.append(f"Month-to-date: {fmt_currency(mtd)} ({pct:.0f}% of {fmt_currency(goal)} goal)")
        else:
            lines.append(f"Month-to-date: {fmt_currency(stripe_data['revenue_mtd'])}")

    # Shopify section
    if shopify_data and config.get("shopify", {}).get("enabled"):
        fulfilled = shopify_data["orders_fulfilled"]
        open_orders = shopify_data["orders_open"]
        refunds = shopify_data["refunds_count"]
        refund_total = shopify_data["refund_total"]

        shopify_line = f"Shopify: {fulfilled} orders fulfilled | {open_orders} open"
        if refunds > 0:
            shopify_line += f" | {refunds} refund ({fmt_currency(refund_total)})"
        lines.append(shopify_line)

        if shopify_data.get("top_product"):
            lines.append(f"Top product: {shopify_data['top_product']} ({shopify_data['top_product_units']} units)")

    # Alerts
    alerts = []
    if stripe_data:
        failures = stripe_data.get("payment_failures", 0)
        retries = stripe_data.get("retries_pending", 0)
        churn_threshold = config.get("alerts", {}).get("churn_threshold", 3)
        large_refund = config.get("alerts", {}).get("large_refund_threshold", 100)

        if failures > 0 or retries > 0:
            warn = "⚠️ " if use_emoji else "ALERT: "
            total_issues = failures + retries
            alerts.append(f"{warn}{total_issues} payment issue{'s' if total_issues > 1 else ''} pending - review in Stripe")

        if stripe_data.get("churned_subs", 0) >= churn_threshold:
            warn = "⚠️ " if use_emoji else "ALERT: "
            alerts.append(f"{warn}High churn: {stripe_data['churned_subs']} cancellations yesterday")

    if shopify_data and shopify_data.get("refund_total", 0) >= config.get("alerts", {}).get("large_refund_threshold", 100):
        warn = "⚠️ " if use_emoji else "ALERT: "
        alerts.append(f"{warn}Large refund: {fmt_currency(shopify_data['refund_total'])} - review in Shopify")

    if alerts:
        lines.append("")
        lines.extend(alerts)

    # Pacing footer
    if stripe_data and config.get("format", {}).get("include_pacing", True):
        days_rem = stripe_data.get("days_remaining", 0)
        on_track = stripe_data.get("on_track")
        if on_track is not None:
            track_str = "on track" if on_track else "below pace"
            lines.append(f"Next: {days_rem} days left in month, {track_str}.")
        elif days_rem:
            lines.append(f"Next: {days_rem} days left in month.")

    return "\n".join(lines)

# ---- Delivery --------------------------------------------------------------

def deliver(message: str, config: dict, dry_run: bool = False) -> bool:
    """Send the briefing via configured channel."""
    channel = config.get("delivery", {}).get("channel", "none")
    recipient = config.get("delivery", {}).get("recipient", "")

    if dry_run or channel == "none":
        print("\n--- BRIEFING (dry run) ---")
        print(message)
        print("--- END ---\n")
        return True

    if channel == "imessage":
        if not recipient:
            raise ValueError("delivery.recipient must be set for iMessage")
        # Write a temp AppleScript file to handle multi-line messages safely
        # (osascript -e can't handle multi-line strings reliably)
        import tempfile, os
        # Convert newlines to AppleScript line continuation
        # AppleScript uses (return) or (ASCII character 10) for newlines
        # Build the message as a concatenated AppleScript string
        parts = message.split("\n")
        # Escape double quotes in each part
        escaped_parts = [p.replace("\\", "\\\\").replace('"', '\\"') for p in parts]
        # Join with AppleScript return character
        as_msg = ' & return & '.join(f'"{p}"' for p in escaped_parts)
        script = f'''
tell application "Messages"
    set targetService to 1st account whose service type = iMessage
    set targetBuddy to participant "{recipient}" of targetService
    send ({as_msg}) to targetBuddy
end tell
'''
        with tempfile.NamedTemporaryFile(mode="w", suffix=".applescript", delete=False) as f:
            f.write(script)
            tmp_path = f.name
        try:
            result = subprocess.run(["osascript", tmp_path], capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"iMessage send failed: {result.stderr}")
        finally:
            os.unlink(tmp_path)
        return True

    elif channel == "slack":
        webhook = config.get("delivery", {}).get("slack_webhook", "")
        if not webhook:
            raise ValueError("delivery.slack_webhook must be set for Slack")
        import urllib.request
        payload = json.dumps({"text": message}).encode()
        req = urllib.request.Request(webhook, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            return resp.status == 200

    elif channel == "telegram":
        chat_id = config.get("delivery", {}).get("telegram_chat_id", "")
        bot_token = config.get("delivery", {}).get("telegram_bot_token", "")
        if not chat_id or not bot_token:
            raise ValueError("delivery.telegram_chat_id and telegram_bot_token required")
        import urllib.request
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = json.dumps({"chat_id": chat_id, "text": message}).encode()
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            return resp.status == 200

    else:
        raise ValueError(f"Unknown delivery channel: {channel}")

# ---- Commands --------------------------------------------------------------

def cmd_run(config: dict, dry_run: bool = False):
    """Run the briefing."""
    stripe_data = None
    shopify_data = None

    print(f"Northstar v1.2.0 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Fetch Stripe
    if config.get("stripe", {}).get("enabled"):
        api_key = config["stripe"].get("api_key", "")
        if not api_key or api_key.startswith("sk_live_YOUR"):
            print("  Stripe: SKIP (no API key configured)")
        else:
            print("  Fetching Stripe data...", end=" ", flush=True)
            goal = config["stripe"].get("monthly_revenue_goal", 0)
            currency = config["stripe"].get("currency", "usd")
            stripe_data = fetch_stripe_metrics(api_key, float(goal), currency)
            print("OK")

    # Fetch Shopify
    if config.get("shopify", {}).get("enabled"):
        domain = config["shopify"].get("shop_domain", "")
        token = config["shopify"].get("access_token", "")
        if not domain or not token or token.startswith("shpat_YOUR"):
            print("  Shopify: SKIP (not configured)")
        else:
            print("  Fetching Shopify data...", end=" ", flush=True)
            shopify_data = fetch_shopify_metrics(domain, token)
            print("OK")

    if not stripe_data and not shopify_data:
        print("\n  No data sources configured. Edit your config file.")
        print(f"  Config: {CONFIG_PATH}")
        return

    # Build and deliver briefing
    briefing = build_briefing(config, stripe_data, shopify_data)

    if dry_run:
        deliver(briefing, config, dry_run=True)
    else:
        print("  Delivering briefing...", end=" ", flush=True)
        deliver(briefing, config)
        print("OK")

    # Update state
    state = load_state()
    state["last_run"] = datetime.now().isoformat()
    state["runs"] = state.get("runs", 0) + 1
    save_state(state)

    print(f"  Done. Run #{state['runs']}.")

def cmd_status(config: dict):
    """Show config and run status."""
    state = load_state()
    print("\nNorthstar Status")
    print("=" * 40)
    print(f"Config: {CONFIG_PATH}")
    print(f"Last run: {state.get('last_run', 'Never')}")
    print(f"Total runs: {state.get('runs', 0)}")
    print()
    print("Configuration:")
    print(f"  Channel: {config.get('delivery', {}).get('channel', 'none')}")
    print(f"  Stripe: {'enabled' if config.get('stripe', {}).get('enabled') else 'disabled'}")
    print(f"  Shopify: {'enabled' if config.get('shopify', {}).get('enabled') else 'disabled'}")
    schedule = config.get("schedule", {})
    print(f"  Schedule: {schedule.get('hour', 6):02d}:{schedule.get('minute', 0):02d} {schedule.get('timezone', 'UTC')}")
    print()
    print("To run now: northstar run")
    print("To test:    northstar test")

def cmd_stripe(config: dict):
    """Show raw Stripe data (debug)."""
    if not config.get("stripe", {}).get("enabled"):
        print("Stripe is not enabled in config.")
        return
    api_key = config["stripe"].get("api_key", "")
    if not api_key or api_key.startswith("sk_live_YOUR"):
        print("No Stripe API key configured.")
        return
    goal = config["stripe"].get("monthly_revenue_goal", 0)
    data = fetch_stripe_metrics(api_key, float(goal))
    print(json.dumps(data, indent=2))

def cmd_shopify(config: dict):
    """Show raw Shopify data (debug)."""
    if not config.get("shopify", {}).get("enabled"):
        print("Shopify is not enabled in config.")
        return
    domain = config["shopify"].get("shop_domain", "")
    token = config["shopify"].get("access_token", "")
    data = fetch_shopify_metrics(domain, token)
    print(json.dumps(data, indent=2))


def cmd_demo():
    """Show a sample briefing with demo data. No config needed."""
    from datetime import date
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  Northstar Demo - Sample Briefing")
    print("  (no API keys required)")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    demo_config = {
        "delivery": {"channel": "none"},
        "stripe": {"enabled": True, "monthly_revenue_goal": 24900},
        "shopify": {"enabled": True},
        "alerts": {"payment_failures": True, "churn_threshold": 3, "large_refund_threshold": 100},
        "format": {"emoji": True, "include_pacing": True, "include_shopify_detail": True},
    }
    demo_stripe = {
        "revenue_yesterday": 1247.50,
        "revenue_last_week_same_day": 1113.84,
        "wow_change_pct": 12.0,
        "revenue_mtd": 18430.00,
        "goal_dollars": 24900.0,
        "goal_pct": 74.0,
        "days_remaining": 6,
        "on_track": True,
        "projected_month": 25200.0,
        "active_subs": 342,
        "new_subs": 3,
        "churned_subs": 1,
        "payment_failures": 0,
        "retries_pending": 2,
    }
    demo_shopify = {
        "orders_fulfilled": 23,
        "orders_open": 8,
        "refunds_count": 1,
        "refund_total": 47.00,
        "top_product": "Growth Plan - Annual",
        "top_product_units": 7,
    }
    briefing = build_briefing(demo_config, demo_stripe, demo_shopify)
    print(briefing)
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    print("Ready to see your real numbers?")
    print("  1. Open your config:  nano ~/.clawd/skills/northstar/config/northstar.json")
    print("  2. Add your Stripe key and phone number")
    print("  3. Run:               northstar test")
    print()
    print("Docs: https://github.com/Daveglaser0823/northstar-skill/blob/main/INSTALL.md")
    print()


def cmd_digest(config: dict, dry_run: bool = False):
    """Run weekly digest (Pro only)."""
    pro = _load_pro()
    pro.cmd_digest(config, dry_run=dry_run)


def cmd_trend(config: dict):
    """Show 7-day revenue trend (Pro only)."""
    pro = _load_pro()
    pro.cmd_trend(config)

# ---- CLI -------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Northstar - Daily Business Briefing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  demo      Show a sample briefing with demo data (no config needed)
  run       Run briefing and deliver to configured channel
  test      Dry-run - print briefing to terminal only
  status    Show config and last run info
  stripe    Show raw Stripe data (debug)
  shopify   Show raw Shopify data (debug)
  digest    [Pro] Run weekly digest (7-day rollup, Sunday format)
  trend     [Pro] Show 7-day revenue trend sparkline

Examples:
  northstar demo            # Try it first - no config needed
  northstar run
  northstar test
  northstar status
  northstar digest          # Pro tier only
  northstar trend           # Pro tier only
        """
    )
    parser.add_argument("command", nargs="?", default="run",
                        choices=["run", "test", "status", "stripe", "shopify", "digest", "trend", "demo"],
                        help="Command to run (default: run)")
    parser.add_argument("--config", type=Path, default=None,
                        help="Path to config file (default: ~/.clawd/skills/northstar/config/northstar.json)")
    parser.add_argument("--version", action="version", version="Northstar 1.2.0")

    args = parser.parse_args()

    # Demo doesn't need config
    if args.command == "demo":
        cmd_demo()
        return

    # Load config
    try:
        config = load_config(args.config)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Dispatch
    if args.command == "run":
        cmd_run(config, dry_run=False)
    elif args.command == "test":
        cmd_run(config, dry_run=True)
    elif args.command == "status":
        cmd_status(config)
    elif args.command == "stripe":
        cmd_stripe(config)
    elif args.command == "shopify":
        cmd_shopify(config)
    elif args.command == "digest":
        cmd_digest(config, dry_run=False)
    elif args.command == "trend":
        cmd_trend(config)


if __name__ == "__main__":
    main()
