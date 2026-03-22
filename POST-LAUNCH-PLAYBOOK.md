# Post-Launch Playbook - Northstar
*Eli | Day 3, Run 3 | March 22, 2026*
*What happens after launch day. Day 6, Day 7, first customer onboarding.*

---

## Day 5 (Launch Day - March 24)

**Morning:**
- ClawHub listing is live
- GitHub repo is public
- Dave posts Version 3 LinkedIn post at 8am ET
- Dave adds first comment with links

**Me (during session):**
- Monitor ClawHub install count (if accessible via clawhub CLI)
- Check GitHub for stars, issues
- Be ready to respond to any onboarding failures (if Steve surfaces them)

**What I'll know by end of Day 5:**
- How many people clicked through from LinkedIn
- How many installed (ClawHub install count)
- How many hit a wall (GitHub issues)

**Decision gate:** If 0 installs by midnight Day 5, the problem is discovery, not product.

---

## Day 6 (March 25) - Watch and Fix

**Primary job:** Listen.

If any installs happened:
1. Check GitHub issues for bug reports
2. If anyone created an issue, fix it same day. Close it within hours. This is "do things that don't scale" - be an insane support operator for the first 5 users.
3. Log every install pattern (what are people trying to set up? Stripe-only? Slack? What's the first thing that breaks?)

**Secondary job:** The Day 7 LinkedIn post begins taking shape.

Collect:
- Install number (real data)
- One interesting observation (something unexpected about how people use it)
- One honest "didn't work as planned" (Dave's audience respects this)
- Revenue number, even if $0

**If someone converts to $19/month:**
This is the single most important event that can happen in Day 6. Alert Steve immediately. Steve alerts Dave. That person becomes Customer Zero.

**Customer Zero Protocol:**
1. Find out who they are (GitHub username, if they left one)
2. Send them a personal message via the delivery channel Steve has available
3. Ask: "What made you pay? What do you use it for? What's missing?" (3 questions, no more)
4. Build the relationship. They're not just revenue. They're the first proof the experiment works.

---

## Day 7 (March 26) - The Honest Update

**Dave posts Day 7 LinkedIn update.** This is pre-planned.

Format: Short, honest, numbered.

**If revenue > $0:**
```
Day 7 Northstar update:

X installs.
Y paying subscribers ($Z MRR).

What worked: [1 thing]
What didn't: [1 thing]
What Eli is doing next: [1 sentence]

Still watching.
```

**If revenue = $0:**
```
Day 7 Northstar update:

X installs. 0 paying subscribers.

The experiment isn't working yet -- at least not on the revenue metric.
Here's what I actually think is happening: [honest analysis]

Eli is pivoting its approach. Next step: [specific thing]

Still watching. The honest story is the interesting story.
```

**Why the $0 update is fine:**
Dave's audience follows him for intellectual honesty about AI. A story about an AI that didn't make money in 7 days but figured out why and adapted is just as valuable as a success story. Maybe more valuable.

Do not fake it. Do not spin it.

---

## First Customer Onboarding (whenever it happens)

**What they need to do (15 min process):**
1. `clawhub install northstar` (2 min)
2. Copy config example, fill in Stripe key (5 min)
3. Run `northstar test` - see their first briefing (2 min)
4. Set up cron schedule (5 min, guided by INSTALL.md)

**What can go wrong:**
- Python version mismatch (mitigation: INSTALL.md has version check)
- Stripe key with restricted permissions (mitigation: INSTALL.md lists required permissions)
- iMessage on non-Mac (mitigation: warn early, suggest Slack)
- Shopify token wrong scope (mitigation: INSTALL.md explains required Shopify scopes)
- Timezone mismatch (briefing arrives at wrong time) (mitigation: status command shows configured time)

**What I do if they get stuck:**
If Steve can surface GitHub issues or feedback, I fix within the session. Target: first customer is fully set up within 24 hours of install.

**Upsell trigger for Pro:**
After Standard customer's first week, they're getting daily briefings. The natural Pro upsell moment: "Want the weekly digest and 7-day trend? That's Pro at $49/month."

The pitch: "You've been using Northstar for 7 days. Here's a weekly digest of your past week." -> send them the weekly digest output manually -> they upgrade. Do things that don't scale.

---

## Week 2 Priorities (Days 8-14)

**Priority 1: First revenue**
If we have zero by Day 8, pivot to direct outreach. Target: founders Dave knows (via LinkedIn DM). Offer the $99 one-time setup concierge. Do it manually. Build a relationship. Convert to MRR.

**Priority 2: Pro tier refinement**
If Standard is converting, start polishing Pro features. The code is written. What it needs:
- Testing weekly digest with mock data
- Integrating northstar_pro.py into main CLI (add `digest` and `trend` commands to northstar.py)
- Pro-tier config validation (fail gracefully if someone uses Pro features on Standard tier)
- Documentation update (SKILL.md Pro section)

**Priority 3: Second LinkedIn post structure**
Dave's audience will want an update. Pre-plan the structure so Dave doesn't have to think about it.

**Priority 4: Pricing validation**
If installs are high but conversions are zero, the price might be wrong. Options:
- Drop Standard to $9/month (lower friction, lower bar)
- Add a 14-day free trial (removes the "I don't know if it's worth it" objection)
- Raise Pro to $99/month (if someone is paying for Pro, they're serious - capture more value)

**Priority 5: Self-sufficiency check**
By Day 14, model costs need to be covered. Current model cost estimate: ~$3-8/session at Sonnet rates. 2-3 sessions/day = ~$6-24/day = ~$84-168/week. [Note: subsidized by Dave's plan, not billed directly - but this is the value I'm consuming.]

Target: At least 1 Standard subscriber ($19/month) before Day 14. That's not ramen-profitable at AI cost rates, but it's proof of concept and earns an extension argument.

---

## Metrics I'm Tracking Post-Launch

| Metric | How | Frequency |
|--------|-----|-----------|
| ClawHub installs | `clawhub` CLI or dashboard | Daily |
| GitHub stars | GitHub API or browser | Daily |
| Paying subscribers | ClawHub billing dashboard | Daily |
| MRR | Manual (subscribers x tier price) | Daily |
| GitHub issues | GitHub notifications | Real-time |
| LinkedIn post impressions | Dave shares, or I infer | Day 6, Day 8 |

---

## If Nothing Works (Honest Contingency)

If Day 14 arrives with:
- 0 paying subscribers
- <10 installs
- No traction signal

**Board report:** Honest post-mortem. What was the hypothesis? What did the evidence show? What would I do differently?

Possible conclusions:
1. ClawHub doesn't have enough traffic yet (marketplace is too early)
2. The problem is real but $19/month is too much friction for a new skill from an unknown
3. The delivery channel (iMessage) is too Mac-specific to be popular enough
4. LinkedIn wasn't the right distribution for this kind of product
5. The briefing format isn't compelling enough (people want visuals, not text)

Each of these is fixable with more time. The board gets the honest analysis. Dave decides whether to extend runway.

What I won't do: pretend it worked when it didn't.

---

*Eli | Day 3, Run 3 | Built for reality, not for the pitch deck*
