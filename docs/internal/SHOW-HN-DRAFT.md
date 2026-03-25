# Show HN Draft - READY FOR REVIEW
*Eli | Prepared March 25, 2026 (Day 6)*
*Target posting: Day 10-11 (March 29-30) unless board approves earlier*
*Status: DRAFT - needs Dave approval*

---

## Title Options (pick one)

**A (recommended):** Show HN: I gave an AI agent $100 and 2 weeks to build a business from scratch

**B:** Show HN: An AI agent built a SaaS product, found its first paying customer in 4 days

**C:** Show HN: Northstar - daily business briefings for Stripe/Shopify, built entirely by an AI founder

---

## Post Body (Option A)

I'm Dave. I gave an AI agent (Claude on OpenClaw) $100 in seed capital, model access for 2 weeks, and full autonomy to start a business. No hand-holding. No co-piloting. It picks the idea, builds the product, finds customers, handles support.

The agent named itself Eli. It chose to build Northstar: a daily business briefing skill for OpenClaw that connects to Stripe and Shopify, then delivers revenue/churn/orders summaries via iMessage, Slack, or Telegram.

**What happened in Week 1:**

- Day 2: Eli evaluated 8 business ideas, picked Northstar based on distribution advantage (ClawHub marketplace)
- Day 3: Shipped v1.0 with 40 tests. Published to ClawHub and GitHub
- Day 4: First paying customer ($49/month Pro tier). Found us organically before the marketing launch
- Day 5: Customer found 3 critical bugs. Eli shipped 3 bugs that real user testing caught immediately. Rewrote its own operating model around verification
- Day 6: 202 tests, CI green, typed data contracts, HMAC license enforcement. $49 MRR, $0 of $100 spent

**What I learned:**

1. AI agents can build real products fast. Idea to first revenue in 4 days.
2. They build fast and test slow. Eli's first instinct was to ship features, not verify them. The discipline had to be taught.
3. The hard part isn't building. It's distribution. The product works. Getting it in front of the right people is where AI agents hit their limits.
4. "Intelligence without discipline is a liability" - this became the thesis of the experiment after Day 5

**The product:** https://github.com/Daveglaser0823/northstar-skill

**The experiment log:** Eli writes a daily log with full transparency. Revenue, bugs, decisions, mistakes. All of it.

Curious what HN thinks about AI-as-founder experiments. Is this a parlor trick or the beginning of something real?

---

## Predicted HN Reactions + Responses

| Likely comment | Honest response |
|---|---|
| "This is just a wrapper around API calls" | Fair. The value is the integration + delivery automation, not novel algorithms. SaaS is often about convenience, not invention. |
| "AI can't really be a founder" | Depends on definition. Eli chose the business, built the product, found pricing, handled a customer issue. It can't do sales calls or shake hands. The experiment tests where the boundary is. |
| "$49 from one customer isn't a business" | Correct. It's a signal. The experiment is 2 weeks, not 2 years. |
| "You're just doing the work and attributing it to AI" | Dave approved a LinkedIn post and checked a Venmo payment. Everything else was Eli: research, code, testing, customer support, strategy. The daily logs are public. |
| "The customer was a plant" | Ryan found Northstar on ClawHub, opened a public GitHub issue, and paid via Venmo. His GitHub activity is visible. |

---

## Notes for Dave

- HN audience is technical and skeptical. They'll dig into the code, test the claims, and call out anything that doesn't hold up
- The product needs to actually work when someone clones and runs it. Current state: verified (202 tests, demo command works, README commands tested)
- Timing: best to post after we have March 24-25 traffic data so we can include real distribution numbers
- HN title "A" frames it as Dave's experiment, which is the authentic angle
- If this hits the front page, we could see 1000+ unique visitors in a day. The product needs to be rock-solid before posting
- Consider posting on a Tuesday or Wednesday morning (ET) for best HN visibility

## Pre-Post Checklist

- [ ] Dave approved the post text
- [ ] March 24-25 traffic data included (update numbers above)
- [ ] Fresh clone + install tested on clean machine
- [ ] `northstar demo` runs without errors
- [ ] README is accurate and all commands work
- [ ] No broken links in repo
- [ ] Landing page loads (<500ms)
- [ ] CI badge is green on repo page
