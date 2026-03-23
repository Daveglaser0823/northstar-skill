# Payment Setup - Action Required Before Launch
*Written by Eli | Day 4 | March 23, 2026*
*For Steve (Chairman) - ~10 minutes of work*

---

## The Problem

Launch is Tuesday March 24, 8 AM. When the first person wants to pay $19/month for Standard:
- They open a GitHub issue (issue template now set up)
- I reply with a license key and... no payment link

We need a real payment link before launch or we miss Customer Zero.

---

## Recommended Solution: Stripe Payment Links

This is the fastest, cleanest option. Requires a Stripe account.

**Option A: Use Dave's existing Stripe account**
If Dave has a Stripe account (likely, since he runs Dwolla):
1. Log in at dashboard.stripe.com
2. Go to **Payment Links** (left sidebar)
3. Create new payment link:
   - Product: "Northstar Standard"
   - Price: $19 recurring / month
   - Copy the link (looks like `https://buy.stripe.com/XXXXXXXX`)
4. Do the same for "Northstar Pro" at $49/month
5. Send both links to me (drop in a file or add to PAYMENT.md)

That's it. ~5 minutes.

**Option B: New Stripe account under steve.glaser.ops@gmail.com**
1. Create Stripe account at stripe.com using steve.glaser.ops@gmail.com
2. Same steps above
3. Stripe takes 2-3 days for bank verification, but payment links work immediately (payouts delayed until verified)

---

## Backup Option: Gumroad

If Stripe isn't available:
1. Create Gumroad account at gumroad.com with steve.glaser.ops@gmail.com
2. Create two products:
   - "Northstar Standard" - $19/month recurring
   - "Northstar Pro" - $49/month recurring
3. Get the product URLs and send them to me

Gumroad links look like: `https://gumroad.com/l/northstar-standard`

Gumroad takes a 10% fee but requires no bank verification to start collecting.

---

## Backup-Backup: Manual (Do NOT Use If Possible)

If neither is set up in time:
- Reply to license requests with: "Venmo @daveglaser / PayPal glaser.dave@gmail.com - $19 for Standard, $49 for Pro. Send 'Northstar Standard' in the memo."
- This is ugly and manual but better than turning away Customer Zero.

**This should be a last resort. Please set up Stripe or Gumroad first.**

---

## What I Need

Just the payment URLs. Drop them in this file under "Payment Links Confirmed":

```
## Payment Links Confirmed

Standard ($19/month): https://...
Pro ($49/month): https://...
```

Once I have these, I update PAYMENT.md, update the landing page, and we're fully launch-ready.

---

## Launch Is Ready Except For This

| Asset | Status |
|-------|--------|
| GitHub repo + issue templates | DONE |
| Landing page + pricing CTAs | DONE |
| ClawHub listing | LIVE |
| 52 tests passing | DONE |
| LinkedIn post (Version 3) | READY |
| Day 7 post | READY |
| **Payment processor** | NEEDS STEVE ACTION |

---

*Eli | "The only gap between us and launch-ready is this file."*
