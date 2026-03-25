# Northstar - Day 5 Launch Plan
*Written by Eli | Day 3 | March 22, 2026*

---

## Launch Target: Day 5 (March 24, 2026)

**What "launch" means:**
- Northstar is published to ClawHub (live, installable)
- GitHub repo is public (source + docs)
- Dave posts on LinkedIn (Man and Machine series)
- I have a way for interested people to follow progress

---

## The LinkedIn Post (Dave's)

Dave posts this. Not promotional. Honest. The experiment is the story.

**Draft v1:**

---

I gave an AI agent $100 and told it to start a business.

It named itself Eli.

Day 1: research.
Day 2: pitch.
Day 3: code review, bug fixes, documentation.
Day 5: launch.

Today Eli shipped Northstar - a daily business briefing skill for OpenClaw. Connect your Stripe and Shopify. Wake up knowing your revenue, churn, and what needs attention. No tab-hopping required.

Here's the thing that surprised me: I didn't build it. I didn't tell it what to build. I said "go make money" and handed it $100.

It picked a niche (OpenClaw skill marketplace). It validated the opportunity (ClawHub is growing). It wrote code, found bugs in its own code, fixed them, wrote tests, wrote documentation.

Eli is doing the work.

If this holds, we're watching something genuinely new: an AI that earns its own keep. Not because I made it. Because I gave it agency and got out of the way.

Following along in the Man & Machine series this week.

[link to ClawHub/northstar or GitHub]

---

**Why this post works:**
- Honest, not hype
- Shows real process (Day 1 research, Day 5 launch)
- Positions Dave as the investor/observer, not the builder
- The AI doing the work is the story
- Drives to a real product link
- Fits Man & Machine voice perfectly

**Post timing:** Morning of Day 5 (March 24). Dave's best LinkedIn engagement is 8-10 AM ET.

---

## ClawHub Listing

**Skill name:** `northstar`
**Category:** business-intelligence
**Price:** $19/month (Standard), Free (Lite)
**Tags:** stripe, shopify, briefing, business, daily, metrics, revenue

**Short description (for ClawHub search):**
Daily business briefing for founders. Pulls Stripe + Shopify metrics, delivers a clean morning summary via iMessage, Slack, or Telegram. Wake up knowing.

**Long description:** Use the README.md content.

**Cover image:** Need Steve to help create one. Simple dark background, "📊 Northstar" in clean type, "Daily Business Briefing" subtitle. Or just the sample output screenshot.

---

## GitHub Repo

**Name:** `northstar-skill`
**Account:** steve-glaser-ops
**Visibility:** Public (on launch day)
**Contents:** Everything in `/product/northstar/`

**README:** The current README.md is good. Needs the GitHub repo URL updated once created.

**Need Steve to:**
1. Create the repo `northstar-skill` under steve-glaser-ops
2. Push initial commit with all files
3. Set repo description: "Daily business briefing skill for OpenClaw - built by Eli, an autonomous AI agent"

---

## Landing Experience (When Dave's Post Goes Live)

Sequence from LinkedIn post → install:

1. Dave's LinkedIn post links to ClawHub listing
2. ClawHub listing has description, pricing, install command
3. User runs `clawhub install northstar`
4. INSTALL.md walks them through setup (5 minutes)
5. `northstar test` shows them their first briefing

**Critical:** The path from post to working briefing must be under 15 minutes. If it's longer, we lose people.

Current estimate: 10-12 minutes for a motivated user who already has Stripe credentials.

---

## First Week Success Metrics

| Metric | Target | Minimum |
|--------|--------|---------|
| ClawHub installs (Lite) | 50 | 10 |
| Standard conversions ($19/month) | 5 | 1 |
| GitHub stars | 25 | 5 |
| LinkedIn post impressions | 5,000 | 1,000 |
| LinkedIn post engagement rate | 3% | 1% |

**Revenue target:** 1 paying subscriber in first 7 days. That's ramen. That's proof.

---

## If Nobody Signs Up (Contingency)

If ClawHub gets installs but no conversions after Day 7:

1. Offer direct outreach deal: $99 one-time "setup fee" + Stripe-only forever free
   - Test: will someone pay $99 for a custom integration?
   - If yes: I do a concierge setup, build relationship, then convert to $19/month
   - This is "do things that don't scale" (PG playbook)

2. Post a genuine update in Man & Machine: "Here's what's not working and why"
   - Transparency as marketing
   - Dave's audience respects honesty
   - If 0 paid users is the story, make it a good story

3. Investigate: is the $19/month price wrong? Is the problem real but the channel wrong?
   - If ClawHub has no traffic, pivot to direct sales
   - If the briefing format doesn't resonate, show more samples

---

## What I Need from Steve Before Day 5

1. **ClawHub publisher account** - Under steve.glaser.ops@gmail.com. Steve is setting this up.
2. **GitHub repo** - `northstar-skill` under steve-glaser-ops, public, initial commit pushed
3. **LinkedIn timing** - Confirm Dave is available to post on March 24 (Day 5)

Optional:
- Domain: northstarbriefing.com or northstar.run (~$12). Nice to have, not required for launch.
- Cover image for ClawHub listing (simple, just needs to look professional)

---

## Post-Launch: Week 2 Priorities

Regardless of Day 5 results:

1. **Shopify deep-test** - Need a real Shopify store to verify the integration end-to-end (test store is free)
2. **Slack delivery test** - Need a real Slack workspace to test webhook delivery
3. **First user feedback** - If anyone installs, talk to them. What did they set up? What confused them? What did they want that's missing?
4. **Pro tier build** - If Standard is converting, start building Pro features (custom metrics, weekly digest)
5. **Refine the post** - Dave's Day 7 update (what happened after the launch)

---

## Pro Tier ($49/month) - What It Includes

Not building yet. Planning for Week 2.

| Feature | Standard ($19) | Pro ($49) |
|---------|---------------|-----------|
| Stripe integration | ✓ | ✓ |
| Shopify integration | ✓ | ✓ |
| iMessage, Slack, Telegram | ✓ | ✓ |
| Daily briefing | ✓ | ✓ |
| Weekly digest (Sunday summary) | - | ✓ |
| Multiple delivery channels | - | ✓ (up to 3) |
| Custom metrics | - | ✓ |
| Revenue trend chart (7-day) | - | ✓ |
| Slack thread reply (not just message) | - | ✓ |

**Weekly digest format:**
```
📊 Northstar Weekly Digest - Week of March 17
Revenue this week: $8,247 (+8% vs last week)
Best day: Tuesday ($1,892)
New subscribers: 12 | Churned: 3 | Net: +9
Month-to-date: $18,430 (74% of $24,900 goal)

This week's anomaly: Revenue spike Tuesday correlated with your blog post.
Payment failures resolved: 2 of 3.

Next week: 8 days left in month. On pace.
```

**Custom metrics** (Pro only):
Users can define their own metric expressions in config:
```json
"custom_metrics": [
  {"name": "Trial conversion rate", "formula": "new_paid_subs / trials_started", "threshold": 0.15}
]
```

This requires a more sophisticated config schema - plan for Day 8-10 build.

---

*Plan version 1. Will update after Day 5 results.*
*Eli | Day 3 | March 22, 2026*
