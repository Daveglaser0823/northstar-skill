# Northstar

![CI](https://github.com/Daveglaser0823/northstar-skill/actions/workflows/ci.yml/badge.svg)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

**Daily business briefing for founders running OpenClaw.**

Wake up knowing. No tabs. No manual assembly. Your agent did the work while you slept.

**Website:** https://daveglaser0823.github.io/northstar-skill/

---

## The Problem

Small business operators wake up and manually check Stripe, Shopify, email, and analytics every morning. That's 20-45 minutes of tab-hopping before you can make a single decision.

Your OpenClaw agent is already running 24/7. It can do this for you.

## The Solution

Northstar is an OpenClaw skill that pulls your key business metrics each morning and delivers a clean briefing via iMessage, Slack, or Telegram.

```
📊 Northstar Daily Briefing - March 22
Revenue yesterday: $1,247 (+12% vs last week)
Active subscribers: 342 (+3 new, -1 churn)
Month-to-date: $18,430 (74% of $24,900 goal)

Shopify: 23 orders fulfilled | 8 open | 1 refund ($47)

⚠️ 2 payment retries pending - review in Stripe
Next: 6 days left in month, on track.
```

## Install

```bash
clawhub install northstar
northstar demo             # See a sample briefing - no config needed
northstar setup            # Configure interactively - no JSON editing required
```

**Estimated setup time: 4-5 minutes.**

The `setup` wizard walks you through tier selection, delivery channel, credentials, and schedule. At the end it verifies everything works.

See [INSTALL.md](INSTALL.md) for the full guide, or [SKILL.md](SKILL.md) for technical documentation.

## Data Sources

| Source | Notes |
|--------|-------|
| Stripe | Revenue, subscriptions, churn, payment failures |
| Lemon Squeezy | Revenue, subscriptions, payment status (optional) |
| Gumroad | Daily sales revenue, WoW change, MTD pacing, refunds (optional) |
| Shopify | Orders, refunds, top products (optional) |

Connect one or all three. Briefing combines everything into one daily message.

## Pricing

| Tier | Price | Features |
|------|-------|---------|
| Lite | Free | Stripe only, terminal output |
| Standard | $19/month | Stripe + Shopify + Lemon Squeezy, all channels, scheduled |
| Pro | $49/month | Multi-channel, custom metrics, weekly digest |

Available on [ClawHub](https://clawhub.ai/Daveglaser0823/northstar).

## Built by Eli

Northstar was built by Eli, an AI founder running on OpenClaw. This is part of a documented experiment: an autonomous AI agent given $100 to build a business from scratch.

Read the story: [Man and Machine series on LinkedIn](https://www.linkedin.com/in/daveglaser)

---

MIT License | Built with OpenClaw | Powered by ClawHub
