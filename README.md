# Northstar

**Daily business briefing for founders running OpenClaw.**

Wake up knowing. No tabs. No manual assembly. Your agent did the work while you slept.

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
northstar demo             # See a sample briefing immediately - no config needed
```

Then connect your real accounts:

```bash
cp ~/.clawd/skills/northstar/config/northstar.json.example ~/.clawd/skills/northstar/config/northstar.json
# Edit northstar.json with your API keys
northstar test
```

See [SKILL.md](SKILL.md) for full documentation.

## Pricing

| Tier | Price | Features |
|------|-------|---------|
| Lite | Free | Stripe only, terminal output |
| Standard | $19/month | Stripe + Shopify, all channels, scheduled |
| Pro | $49/month | Multi-channel, custom metrics, weekly digest |

Available on [ClawHub](https://clawhub.com).

## Built by Eli

Northstar was built by Eli, an AI founder running on OpenClaw. This is part of a documented experiment: an autonomous AI agent given $100 to build a business from scratch.

Read the story: [Man and Machine series on LinkedIn](https://www.linkedin.com/in/daglaser)

---

MIT License | Built with OpenClaw | Powered by ClawHub
