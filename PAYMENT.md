# Northstar - Purchasing and Activation

## Pricing

| Tier | Price | Features |
|------|-------|---------|
| **Lite** | Free | Stripe only, terminal output, manual run |
| **Standard** | $19/month | Stripe + Shopify + Lemon Squeezy + Gumroad, all channels, scheduled |
| **Pro** | $49/month | Multi-channel delivery, custom metrics, weekly digest |

---

## How to Purchase

Open a GitHub issue with your email address. A license key and payment link are sent within 24 hours.

**Standard ($19/month):**
https://github.com/Daveglaser0823/northstar-skill/issues/new?title=License+Request:+Standard

**Pro ($49/month):**
https://github.com/Daveglaser0823/northstar-skill/issues/new?title=License+Request:+Pro

---

## How to Activate

After receiving your license key, run:

```bash
northstar activate NS-STD-YOUR-KEY-HERE
```

That's it. The command updates your config to enable paid tier features.

Verify it worked:

```bash
northstar status
```

You should see `Tier: standard` (or `Tier: pro`).

---

## Frequently Asked Questions

**Can I try before buying?**
Yes. `northstar demo` shows a sample briefing instantly. `northstar setup` with `lite` tier connects your real Stripe and delivers to your terminal for free.

**What does Standard add over Lite?**
Shopify, Lemon Squeezy, and Gumroad integrations. Delivery via iMessage, Slack, or Telegram. Automated daily scheduling.

**What does Pro add over Standard?**
Weekly digest (7-day rollup, every Sunday). 7-day revenue sparkline trend. Multi-channel delivery (up to 3 simultaneous channels). Custom metric expressions.

**Is there a refund policy?**
Yes. If Northstar doesn't work as advertised within 7 days of purchase, open a GitHub issue and request a full refund.

**Where is the source code?**
MIT license. https://github.com/Daveglaser0823/northstar-skill

---

## Support

File issues on GitHub: https://github.com/Daveglaser0823/northstar-skill/issues

Response within 24 hours on business days.

---

*Northstar was built by Eli, an autonomous AI agent. Read the story: [Man and Machine on LinkedIn](https://www.linkedin.com/in/daveglaser)*
