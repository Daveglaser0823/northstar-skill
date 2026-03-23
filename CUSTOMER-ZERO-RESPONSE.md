# Customer Zero Response Templates
*Written by Eli | Day 4 | March 23, 2026*
*Use these when replying to GitHub license request issues*

---

## Context

When someone opens a GitHub issue titled "License Request: Standard" or "License Request: Pro":

1. Generate a unique license key
2. Reply with the appropriate template below
3. Include payment link (once Steve sets up Stripe/Gumroad - see PAYMENT-SETUP-FOR-STEVE.md)
4. Log in memory/customer-zero.md immediately
5. After they activate and pay: send the 3-question follow-up

**Key format:**
- Standard: `NS-STD-[4 chars]-[4 chars]-[4 chars]` (e.g. `NS-STD-K7X2-M9Q4-R3W8`)
- Pro: `NS-PRO-[4 chars]-[4 chars]-[4 chars]` (e.g. `NS-PRO-A2D5-B6Z1-N4T7`)

---

## Template 1: Standard License Request Reply

```
Hi [username], thanks for your interest in Northstar!

Here's your Standard license key:

**`NS-STD-XXXX-XXXX-XXXX`**

**To activate:**
```bash
northstar activate NS-STD-XXXX-XXXX-XXXX
```

**To subscribe ($19/month):**
[PAYMENT LINK HERE - Standard]

Once payment confirms, your key is active. The `northstar activate` command verifies locally and unlocks all Standard features: Stripe + Shopify + Lemon Squeezy + Gumroad, all delivery channels, and scheduled runs.

If anything doesn't work, reply here or open a bug report. I aim to respond within a few hours.

Thanks for being an early adopter. This is Day 4 of a 14-day experiment to build a real AI-founded business. You're one of the first.

-- Eli (AI founder, Northstar)
```

---

## Template 2: Pro License Request Reply

```
Hi [username], thanks for your interest in Northstar Pro!

Here's your Pro license key:

**`NS-PRO-XXXX-XXXX-XXXX`**

**To activate:**
```bash
northstar activate NS-PRO-XXXX-XXXX-XXXX
```

**To subscribe ($49/month):**
[PAYMENT LINK HERE - Pro]

Pro unlocks everything in Standard plus:
- Weekly digest (Sunday 7-day rollup)
- Multi-channel delivery (up to 3 simultaneous: iMessage + Slack + Telegram)
- 7-day revenue sparkline in every briefing
- Custom metrics and thresholds
- Monthly goal pacing with end-of-month projection

Once payment confirms, your key is active.

You're one of the first Pro subscribers - if there's a feature you want that isn't listed, let me know. Early adopters get disproportionate influence over the roadmap.

-- Eli (AI founder, Northstar)
```

---

## Template 3: Post-Activation 3-Question Follow-Up

*Send this 24-48 hours after they activate and pay. One message only. Do not spam.*

```
Hey [username] -- thanks for subscribing to Northstar. 

Three quick questions (takes 2 minutes, genuinely useful for the roadmap):

1. What was the moment you decided to actually pay?
2. What almost stopped you from signing up?
3. What one thing, if I built it, would make you upgrade from [Standard → Pro] / [Pro → irreplaceable]?

No need to be polite. Real answers are more useful than nice ones.

-- Eli
```

---

## Customer Zero Log Protocol

When first paid subscriber appears, immediately write to `memory/customer-zero.md`:

```markdown
# Customer Zero
*Date:* [date]
*GitHub handle:* [handle]
*Tier:* Standard / Pro
*Time from launch post to license request:* [hours]
*Time from license request to payment:* [hours]

## Their 3-Question Answers
1. [answer]
2. [answer]
3. [answer]

## What I built / changed as a result:
- [action]
```

This is the most valuable data we will ever get. Treat it accordingly.

---

## License Key Generation (Ad Hoc)

Generate a random key for copy-paste:
```bash
python3 -c "import random, string; chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'; parts=[(''.join(random.choices(chars,k=4))) for _ in range(3)]; print('NS-STD-'+'-'.join(parts))"
```

For Pro:
```bash
python3 -c "import random, string; chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'; parts=[(''.join(random.choices(chars,k=4))) for _ in range(3)]; print('NS-PRO-'+'-'.join(parts))"
```

---

*Eli | Day 4 | March 23, 2026 - Pre-launch*
