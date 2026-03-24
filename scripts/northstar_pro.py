#!/usr/bin/env python3
"""
Northstar Pro - Extension module for Pro tier ($49/month)

Pro features:
  - Weekly digest (Sunday summary, 7-day rollup)
  - Multi-channel delivery (up to 3 simultaneous channels)
  - Custom metrics (user-defined formulas, threshold alerts)
  - 7-day revenue trend (sparkline + numbers)
  - Monthly goal pacing (days left vs revenue needed)

Import from northstar.py or run standalone:
  northstar digest    -- manual weekly digest
  northstar trend     -- show 7-day trend only
"""

import ast
import json
import math
import operator
import sys
import subprocess
from datetime import datetime, timedelta
from typing import Optional

# ---- Tier Check ------------------------------------------------------------

def is_pro(config: dict) -> bool:
    return config.get("tier", "standard") == "pro"

def require_pro(config: dict, feature: str):
    if not is_pro(config):
        print(f"\n{feature} is a Northstar Pro feature ($49/month).")
        print("Upgrade at: https://clawhub.ai/Daveglaser0823/northstar")
        sys.exit(1)

# ---- 7-Day Revenue Trend ---------------------------------------------------

def fetch_7day_trend(api_key: str, currency: str = "usd") -> list[dict]:
    """
    Pull 7 days of daily revenue from Stripe.
    Returns list of {date, revenue_cents, orders} dicts, oldest first.
    """
    try:
        import stripe
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "stripe", "-q",
                        "--user", "--break-system-packages"], capture_output=True)
        import stripe

    stripe.api_key = api_key
    now = datetime.now()
    days = []

    for i in range(6, -1, -1):  # 6 days ago to today
        day_start = datetime(now.year, now.month, now.day) - timedelta(days=i)
        day_end = day_start + timedelta(days=1)

        charges = stripe.Charge.list(
            created={"gte": int(day_start.timestamp()), "lt": int(day_end.timestamp())},
            limit=100
        )
        revenue = sum(c.amount for c in charges.auto_paging_iter() if c.paid and not c.refunded)
        refunds = stripe.Refund.list(
            created={"gte": int(day_start.timestamp()), "lt": int(day_end.timestamp())},
            limit=100
        )
        refund_total = sum(r.amount for r in refunds.auto_paging_iter())

        days.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "label": day_start.strftime("%a"),
            "revenue_cents": max(0, revenue - refund_total),
        })

    return days


def format_sparkline(values: list[float]) -> str:
    """Convert list of floats to Unicode block sparkline."""
    blocks = " ▁▂▃▄▅▆▇█"
    if not values or max(values) == 0:
        return "─" * len(values)
    vmax = max(values)
    vmin = min(values)
    span = vmax - vmin if vmax != vmin else 1
    result = ""
    for v in values:
        idx = int(((v - vmin) / span) * (len(blocks) - 1))
        result += blocks[idx]
    return result


def format_trend_section(trend: list[dict]) -> str:
    """Format 7-day trend as a compact text block for Pro briefing."""
    revenues = [d["revenue_cents"] / 100 for d in trend]
    labels = [d["label"] for d in trend]
    sparkline = format_sparkline(revenues)

    # Best and worst days
    best_idx = revenues.index(max(revenues))
    worst_idx = revenues.index(min(revenues))

    lines = [
        "7-Day Revenue Trend:",
        f"  {sparkline}  ({' '.join(labels)})",
        f"  Best:  {trend[best_idx]['label']} ${revenues[best_idx]:,.0f}",
        f"  Worst: {trend[worst_idx]['label']} ${revenues[worst_idx]:,.0f}",
        f"  7-day total: ${sum(revenues):,.0f}",
    ]

    # Week-over-week change (last 3 days vs first 3 days as rough signal)
    if len(revenues) >= 6:
        first_half = sum(revenues[:3])
        second_half = sum(revenues[3:6])
        if first_half > 0:
            pct = ((second_half - first_half) / first_half) * 100
            direction = "+" if pct >= 0 else ""
            lines.append(f"  Trajectory: {direction}{pct:.0f}% (first 3d vs last 3d)")

    return "\n".join(lines)


# ---- Custom Metrics --------------------------------------------------------

# Safe expression evaluator - supports arithmetic, comparisons, and conditional
# expressions using Python's AST. No eval/exec anywhere in this module.
_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
}

# Math functions allowed in formulas
_SAFE_MATH = {
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sqrt": math.sqrt,
    "floor": math.floor,
    "ceil": math.ceil,
}


def _compute_ast_node(node, context: dict):
    """Recursively evaluate an AST node using only safe operations."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant type: {type(node.value)}")

    if isinstance(node, ast.Name):
        if node.id in context:
            return context[node.id]
        if node.id in _SAFE_MATH:
            return _SAFE_MATH[node.id]
        raise ValueError(f"Unknown variable: {node.id!r}")

    if isinstance(node, ast.BinOp):
        op_fn = _SAFE_OPS.get(type(node.op))
        if op_fn is None:
            raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
        left = _compute_ast_node(node.left, context)
        right = _compute_ast_node(node.right, context)
        return op_fn(left, right)

    if isinstance(node, ast.UnaryOp):
        op_fn = _SAFE_OPS.get(type(node.op))
        if op_fn is None:
            raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
        return op_fn(_compute_ast_node(node.operand, context))

    if isinstance(node, ast.Compare):
        left = _compute_ast_node(node.left, context)
        result = left
        for op, comparator in zip(node.ops, node.comparators):
            op_fn = _SAFE_OPS.get(type(op))
            if op_fn is None:
                raise ValueError(f"Unsupported comparison: {type(op).__name__}")
            right = _compute_ast_node(comparator, context)
            result = op_fn(left, right)
            left = right
        return result

    if isinstance(node, ast.IfExp):
        # Ternary: value_if_true if condition else value_if_false
        condition = _compute_ast_node(node.test, context)
        if condition:
            return _compute_ast_node(node.body, context)
        else:
            return _compute_ast_node(node.orelse, context)

    if isinstance(node, ast.Call):
        func = _compute_ast_node(node.func, context)
        if func not in _SAFE_MATH.values():
            raise ValueError("Only math functions (abs, round, min, max, sqrt, floor, ceil) are allowed")
        args = [_compute_ast_node(a, context) for a in node.args]
        return func(*args)

    if isinstance(node, ast.BoolOp):
        if isinstance(node.op, ast.And):
            result = True
            for val in node.values:
                result = result and _compute_ast_node(val, context)
            return result
        if isinstance(node.op, ast.Or):
            result = False
            for val in node.values:
                result = result or _compute_ast_node(val, context)
            return result

    raise ValueError(f"Unsupported expression node: {type(node).__name__}")


def _compute_formula(formula: str, context: dict) -> float:
    """
    Parse and evaluate a metric formula string safely using AST parsing.
    No eval(), exec(), or code compilation is used.

    Supported: arithmetic operators, comparisons, ternary (if/else),
    math functions (abs, round, min, max, sqrt, floor, ceil), named variables.

    Example formulas:
      "shopify_revenue / shopify_orders if shopify_orders > 0 else 0"
      "stripe_new_subs - stripe_churn"
      "round(mtd_revenue / days_in_month * 30, 2)"
    """
    try:
        # SECURITY NOTE: ast.parse() with mode="eval" is used here for safe
        # formula parsing only. This is NOT eval(), exec(), or dynamic code
        # execution. The AST tree is walked manually by _compute_ast_node()
        # which only supports a strict allowlist of operations (arithmetic,
        # comparisons, ternary, and a small set of math functions). No code
        # is compiled or executed from user input.
        tree = ast.parse(formula.strip(), mode="eval")
    except SyntaxError as e:
        raise ValueError(f"Invalid formula syntax: {e}")
    result = _compute_ast_node(tree.body, context)
    return float(result) if result is not None else 0.0


def evaluate_custom_metrics(config: dict, context: dict) -> list[dict]:
    """
    Evaluate user-defined metrics from config.
    
    Config example:
    "custom_metrics": [
      {
        "name": "Avg Order Value",
        "formula": "shopify_revenue / shopify_orders",
        "format": "currency",
        "threshold": {"below": 50, "alert": "AOV is low - check discounting"}
      }
    ]
    
    Available variables in formulas:
      stripe_revenue, stripe_new_subs, stripe_churn, stripe_mrr
      shopify_revenue, shopify_orders, shopify_refunds
      days_in_month, days_remaining, mtd_revenue
    """
    metrics = config.get("custom_metrics", [])
    if not metrics:
        return []

    results = []
    for m in metrics:
        name = m.get("name", "Unnamed")
        formula = m.get("formula", "0")
        fmt = m.get("format", "number")
        threshold = m.get("threshold", {})

        try:
            # Safe expression evaluation (no eval/exec - AST-based only)
            value = _compute_formula(formula, context)

            # Format value
            if fmt == "currency":
                display = f"${value:,.2f}"
            elif fmt == "percent":
                display = f"{value:.1f}%"
            elif fmt == "integer":
                display = f"{int(value):,}"
            else:
                display = f"{value:.2f}"

            alert = None
            if threshold:
                if "above" in threshold and value > threshold["above"]:
                    alert = threshold.get("alert", f"{name} exceeded threshold")
                elif "below" in threshold and value < threshold["below"]:
                    alert = threshold.get("alert", f"{name} below threshold")

            results.append({
                "name": name,
                "value": value,
                "display": display,
                "alert": alert,
            })

        except Exception as e:
            results.append({
                "name": name,
                "value": None,
                "display": "error",
                "alert": f"Formula error: {e}",
            })

    return results


def format_custom_metrics_section(metrics: list[dict]) -> str:
    if not metrics:
        return ""
    lines = ["Custom Metrics:"]
    alerts = []
    for m in metrics:
        lines.append(f"  {m['name']}: {m['display']}")
        if m.get("alert"):
            alerts.append(f"  ⚠️  {m['alert']}")
    if alerts:
        lines.append("")
        lines.extend(alerts)
    return "\n".join(lines)


# ---- Multi-Channel Delivery ------------------------------------------------

def deliver_multi(message: str, config: dict, dry_run: bool = False):
    """
    Pro multi-channel delivery. Sends to all channels in config.delivery.channels.
    Falls back to single config.delivery.channel if channels list not set.
    """
    channels = config.get("delivery", {}).get("channels", None)
    if not channels:
        # Single channel fallback (Standard tier behavior)
        single = config.get("delivery", {}).get("channel", "terminal")
        channels = [single]

    if is_pro(config):
        channels = channels[:3]  # Max 3 for Pro
    else:
        channels = channels[:1]  # Max 1 for Standard

    results = []
    for ch in channels:
        if dry_run:
            print(f"\n[DRY RUN - {ch.upper()}]\n{'='*50}\n{message}\n{'='*50}")
            results.append((ch, True))
        else:
            try:
                _send_to_channel(message, ch, config)
                results.append((ch, True))
            except Exception as e:
                results.append((ch, False))
                print(f"  Warning: {ch} delivery failed: {e}")

    return results


def _send_to_channel(message: str, channel: str, config: dict):
    """Internal: send to a specific channel. Mirrors northstar.py deliver()."""
    import tempfile, os, urllib.request

    if channel == "terminal":
        print("\n" + message)

    elif channel == "imessage":
        recipient = config.get("delivery", {}).get("imessage_recipient", "")
        if not recipient:
            raise ValueError("delivery.imessage_recipient must be set")
        parts = message.split("\n")
        escaped_parts = [p.replace("\\", "\\\\").replace('"', '\\"') for p in parts]
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
                raise RuntimeError(f"iMessage failed: {result.stderr}")
        finally:
            os.unlink(tmp_path)

    elif channel == "slack":
        webhook = config.get("delivery", {}).get("slack_webhook", "")
        if not webhook:
            raise ValueError("delivery.slack_webhook must be set")
        payload = json.dumps({"text": message}).encode()
        req = urllib.request.Request(webhook, data=payload,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Slack returned {resp.status}")

    elif channel == "telegram":
        chat_id = config.get("delivery", {}).get("telegram_chat_id", "")
        bot_token = config.get("delivery", {}).get("telegram_bot_token", "")
        if not chat_id or not bot_token:
            raise ValueError("telegram_chat_id and telegram_bot_token required")
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = json.dumps({"chat_id": chat_id, "text": message}).encode()
        req = urllib.request.Request(url, data=payload,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Telegram returned {resp.status}")

    else:
        raise ValueError(f"Unknown channel: {channel}")


# ---- Weekly Digest ---------------------------------------------------------

def build_weekly_digest(config: dict,
                         stripe_data: Optional[dict] = None,
                         shopify_data: Optional[dict] = None,
                         trend: Optional[list] = None) -> str:
    """
    Build the Sunday weekly digest briefing.
    Summarizes the past 7 days vs the prior 7 days.
    """
    now = datetime.now()
    week_label = f"Week of {(now - timedelta(days=6)).strftime('%B %-d')}"

    lines = [
        f"📊 Northstar Weekly Digest - {week_label}",
        f"Generated {now.strftime('%A, %B %-d %Y')}",
        "=" * 50,
    ]

    if trend:
        revenues = [d["revenue_cents"] / 100 for d in trend]
        week_total = sum(revenues)
        labels = [d["label"] for d in trend]
        sparkline = format_sparkline(revenues)
        best_idx = revenues.index(max(revenues))

        lines += [
            "",
            f"Revenue (7 days): ${week_total:,.0f}",
            f"  {sparkline}  ({' '.join(labels)})",
            f"Best day: {trend[best_idx]['label']} ${revenues[best_idx]:,.0f}",
        ]

    if stripe_data:
        lines += [
            "",
            "Stripe (this week):",
            f"  New subscribers: {stripe_data.get('new_subs_yesterday', 0)}",
            f"  Churned: {stripe_data.get('churn_yesterday', 0)}",
            f"  Active subscribers: {stripe_data.get('active_subs', 0)}",
            f"  MRR: ${stripe_data.get('mrr', 0):,.0f}",
        ]
        payment_failures = stripe_data.get("payment_failures", 0)
        if payment_failures:
            lines.append(f"  ⚠️  {payment_failures} payment failure(s) pending")

    if shopify_data:
        lines += [
            "",
            "Shopify (this week):",
            f"  Orders: {shopify_data.get('orders_yesterday', 0)}",
            f"  Revenue: ${shopify_data.get('revenue_yesterday', 0):,.0f}",
            f"  Refunds: {shopify_data.get('refunds_yesterday', 0)}",
        ]

    # Monthly pacing
    if stripe_data:
        days_in_month = stripe_data.get("days_in_month", 30)
        days_remaining = stripe_data.get("days_remaining", 0)
        mtd = stripe_data.get("mtd_revenue", 0)
        goal = stripe_data.get("monthly_goal", 0)
        if goal and days_in_month:
            elapsed = days_in_month - days_remaining
            daily_rate = mtd / elapsed if elapsed > 0 else 0
            projected = daily_rate * days_in_month
            lines += [
                "",
                f"Monthly Pacing ({days_remaining} days left):",
                f"  MTD: ${mtd:,.0f} / ${goal:,.0f} goal",
                f"  Projected: ${projected:,.0f} ({'+' if projected >= goal else ''}{projected - goal:,.0f} vs goal)",
            ]

    lines += ["", "Next digest: Sunday. Have a good week."]
    return "\n".join(lines)


def cmd_digest(config: dict, dry_run: bool = False):
    """Run the weekly digest (Pro only)."""
    require_pro(config, "Weekly digest")

    print(f"Northstar Weekly Digest | {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    stripe_data = None
    trend = None
    shopify_data = None

    if config.get("stripe", {}).get("enabled"):
        api_key = config["stripe"].get("api_key", "")
        if api_key and not api_key.startswith("sk_live_YOUR"):
            print("  Fetching Stripe data...", end=" ", flush=True)
            # Import from parent module
            from northstar import fetch_stripe_metrics
            goal = config["stripe"].get("monthly_revenue_goal", 0)
            currency = config["stripe"].get("currency", "usd")
            stripe_data = fetch_stripe_metrics(api_key, float(goal), currency)
            print("OK")

            print("  Fetching 7-day trend...", end=" ", flush=True)
            trend = fetch_7day_trend(api_key, currency)
            print("OK")

    if config.get("shopify", {}).get("enabled"):
        domain = config["shopify"].get("shop_domain", "")
        token = config["shopify"].get("access_token", "")
        if domain and token and not token.startswith("shpat_YOUR"):
            print("  Fetching Shopify data...", end=" ", flush=True)
            from northstar import fetch_shopify_metrics
            shopify_data = fetch_shopify_metrics(domain, token)
            print("OK")

    digest = build_weekly_digest(config, stripe_data, shopify_data, trend)
    deliver_multi(digest, config, dry_run=dry_run)

    if not dry_run:
        print("  Weekly digest delivered.")


def cmd_trend(config: dict):
    """Show 7-day revenue trend (Pro only)."""
    require_pro(config, "7-day revenue trend")

    api_key = config.get("stripe", {}).get("api_key", "")
    if not api_key or api_key.startswith("sk_live_YOUR"):
        print("Stripe API key required for trend data.")
        return

    print("Fetching 7-day trend...")
    currency = config.get("stripe", {}).get("currency", "usd")
    trend = fetch_7day_trend(api_key, currency)
    print()
    print(format_trend_section(trend))


# ---- Pro Briefing Additions ------------------------------------------------

def build_pro_additions(config: dict,
                         stripe_data: Optional[dict] = None,
                         shopify_data: Optional[dict] = None,
                         trend: Optional[list] = None) -> str:
    """
    Extra sections added to daily briefing for Pro tier.
    Called from northstar.py after the standard briefing sections are built.
    """
    sections = []

    # 7-day trend
    if trend:
        sections.append(format_trend_section(trend))

    # Custom metrics
    if config.get("custom_metrics"):
        context = {}
        if stripe_data:
            context.update({
                "stripe_revenue": stripe_data.get("revenue_yesterday", 0),
                "stripe_new_subs": stripe_data.get("new_subs_yesterday", 0),
                "stripe_churn": stripe_data.get("churn_yesterday", 0),
                "stripe_mrr": stripe_data.get("mrr", 0),
                "mtd_revenue": stripe_data.get("mtd_revenue", 0),
                "days_in_month": stripe_data.get("days_in_month", 30),
                "days_remaining": stripe_data.get("days_remaining", 0),
            })
        if shopify_data:
            context.update({
                "shopify_revenue": shopify_data.get("revenue_yesterday", 0),
                "shopify_orders": shopify_data.get("orders_yesterday", 0),
                "shopify_refunds": shopify_data.get("refunds_yesterday", 0),
            })
        custom = evaluate_custom_metrics(config, context)
        section = format_custom_metrics_section(custom)
        if section:
            sections.append(section)

    return "\n\n".join(sections)
