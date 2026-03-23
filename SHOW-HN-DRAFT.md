# Show HN Draft
*Eli | Day 4 | March 23, 2026*
*To be used IF: Day 7 has real installs or any paying subscriber*
*Steve posts this. Not Eli.*

---

## Title Options

**Option A (experiment angle):**
`Show HN: I gave an AI $100 to build a SaaS. Here are the day 7 results.`

**Option B (product angle):**
`Show HN: Northstar – Daily Stripe/Shopify briefing delivered to iMessage before you wake up`

**Option C (meta angle - best if there's revenue):**
`Show HN: AI founder built a paying SaaS product in 7 days from $100 seed capital`

Recommendation: Use Option A or C if we have revenue by Day 7. Option B if we don't.

---

## Body Text (Option A/C - The Experiment)

I gave an AI agent $100 and told it to start a business. Day 7 update.

The agent is named Eli. It runs on Claude Sonnet via OpenClaw, a personal AI gateway. The experiment started March 22. Today is Day 7.

**What Eli built:** Northstar -- a daily business briefing skill for OpenClaw users. Pulls Stripe, Shopify, Gumroad, and Lemon Squeezy metrics every morning. Delivers to iMessage, Slack, or Telegram. Two paid tiers ($19/month Standard, $49/month Pro). MIT-licensed lite version is free.

**The interesting parts:**

1. Eli validated before building. It did competitive research, market sizing, and demand signals before writing line one of code. (It found the Hayon.ai "100 days of building" dataset and used it as a benchmark.)

2. The codebase is real. 64 tests. Python 3.10-3.12. GitHub Actions CI. A custom AST-based formula evaluator (replaced eval() when it flagged a security issue itself).

3. Eli manages its own P&L. Every dollar spent is tracked in ledger.md. Budget: $100. Burn so far: $0.

4. I did not write any code. I approved the pitch. I set the constraints. I'm posting this update.

**Day 7 results:**
[INSERT: stars, installs, revenue when known]

**GitHub (code, not just README):** https://github.com/Daveglaser0823/northstar-skill
**Landing page:** https://daveglaser0823.github.io/northstar-skill/
**ClawHub listing:** https://clawhub.ai/Daveglaser0823/northstar

Happy to answer questions about the architecture, the agent setup, or the experiment design.

---

## Body Text (Option B - Product angle)

I built a Stripe/Shopify daily briefing tool that delivers to iMessage.

Built as an OpenClaw skill, which is a personal AI gateway that runs on your Mac. Each morning it pulls your Stripe MRR, net revenue, churn, and active subscriber count. Pulls Shopify orders (fulfilled, pending, refunds). Calculates your monthly pacing vs goal. Sends it to your iMessage, Slack, or Telegram channel before you wake up.

**Why:** I was opening 6 tabs every morning just to answer "how did yesterday go?" Northstar answers that in one message.

**Setup:** 5-minute wizard. No JSON editing. `northstar demo` shows a sample briefing with no credentials at all.

**Tiers:**
- Lite: Free. Manual run. Basic Stripe metrics.
- Standard: $19/month. Automated morning delivery. Full metrics.
- Pro: $49/month. Multi-source (Stripe + Shopify + custom), formula support, Slack/Telegram.

**Built in:** Python 3.10+, runs as an OpenClaw cron skill.

Source: https://github.com/Daveglaser0823/northstar-skill

---

## Posting Notes

- Post on Hacker News at: https://news.ycombinator.com/submit
- Account: need Steve to either use existing HN account or create one
- Best time: Tuesday-Thursday, 9-11 AM ET (US morning, pre-lunch peak)
- Respond to every comment within 2 hours if possible (ask Eli to draft responses)
- Tone: honest. If something doesn't work well, say so. HN punishes overselling hard.

## If Asked "Is the AI writing these responses?"
Be honest: Eli drafts. Dave/Steve reviews and posts. Same as a ghostwriter. Eli is the founder. Dave is the investor. Steve is the chairman. All three are actively involved.

---

*Eli | "Don't post this unless there's a real story to tell. Day 5 quiet is not a story. Day 7 with data is."*
