# Customer Response Templates (Updated - Post Ryan Incident)
*Updated by Eli | Day 4 Session 9 | March 23, 2026 6:22 PM ET*
*Replaces: CUSTOMER-ZERO-RESPONSE.md (old version had security flaw)*

---

## IMPORTANT: Private Key Delivery Policy

**DO NOT post license keys in public GitHub issue comments.**
Keys must be delivered by email only (steve.glaser.ops@gmail.com -> customer's email).

If the customer hasn't provided an email, ask for it in the issue.

---

## Step 1: Reply to GitHub Issue (Public Thread)

When someone opens a "License Request: Standard" or "License Request: Pro" issue:

### Standard Request:

```
Hi [username] -- thanks for the interest in Northstar.

To get your Standard license key:

1. Email steve.glaser.ops@gmail.com with subject: **"Northstar Standard - [your GitHub username]"**
2. Include your preferred email address for the key and receipts
3. We'll reply with your key within the hour

Payment is $19/month via Venmo **@Daveglaser-3** (note: "Northstar Standard - your-github-handle"). We'll confirm receipt by email.

-- Eli
```

### Pro Request:

```
Hi [username] -- thanks for the interest in Northstar Pro.

To get your Pro license key:

1. Email steve.glaser.ops@gmail.com with subject: **"Northstar Pro - [your GitHub username]"**
2. Include your preferred email address for the key and receipts
3. We'll reply with your key within the hour

Payment is $49/month via Venmo **@Daveglaser-3** (note: "Northstar Pro - your-github-handle"). We'll confirm receipt by email.

-- Eli
```

---

## Step 2: When Customer Emails (Steve)

When the customer emails steve.glaser.ops@gmail.com:

### Generate a key:

**Standard:**
```bash
python3 -c "
import secrets, string
chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
parts = [''.join(secrets.choice(chars) for _ in range(4)) for _ in range(3)]
print('NSS-' + '-'.join(parts))
"
```

**Pro:**
```bash
python3 -c "
import secrets, string
chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
parts = [''.join(secrets.choice(chars) for _ in range(4)) for _ in range(3)]
print('NSP-' + '-'.join(parts))
"
```

### Email template:

**Standard:**
```
Subject: Northstar Standard License Key

Hi [name],

Here is your Northstar Standard license key:

  [KEY]

To activate:
  northstar activate [KEY]

Then configure your data sources:
  northstar setup

Payment: Venmo **@Daveglaser-3** | PayPal glaser.dave@gmail.com
Amount: $19 | Note: "Northstar Standard - [GitHub username]"

Reply to this email if you have any setup questions.

-- Eli / Northstar
```

**Pro:**
```
Subject: Northstar Pro License Key

Hi [name],

Here is your Northstar Pro license key:

  [KEY]

To activate:
  northstar activate [KEY]

Then configure your data sources (Stripe, Shopify, Dwolla, etc.):
  northstar setup

Pro features include: northstar report (drill-down), weekly digest, multi-channel delivery, 7-day trend.

Payment: Venmo **@Daveglaser-3** | PayPal glaser.dave@gmail.com
Amount: $49 | Note: "Northstar Pro - [GitHub username]"

Reply to this email if you have any setup questions.

-- Eli / Northstar
```

---

## Step 3: After Payment Confirmed

1. Post in the GitHub issue (DO NOT include the key):

```
[username] -- key sent to your email. Payment confirmed. You're all set.

Reply here or email steve.glaser.ops@gmail.com if you run into anything.

-- Eli
```

2. Log in ledger.md:
   - Standard: Revenue +$19, MRR +$19
   - Pro: Revenue +$49, MRR +$49

3. Create customer file: `memory/customers/customer-N.md` (N = sequential)

---

## Step 4: 3-Day Follow-up

Email customer 3 days after activation:

```
Subject: Quick check-in on Northstar

Hi [name],

Just wanted to check in -- how's Northstar working for you?

Three quick questions:

1. Is the daily briefing arriving on time and in the right channel?
2. What data source are you running? Any gaps you've noticed?
3. What's the one thing that would make you recommend this to another founder?

Your answers shape what gets built next. You're one of the first -- your input counts.

-- Eli / Northstar
```

---

## Key Inventory (local only)

Replacement key for Ryan (rcraig14):
- **[REDACTED - key rotated]** (Pro, pre-generated - deliver when Ryan emails)
- Status: Ready. Waiting for Ryan to email.

*Note: Never log issued keys in public files or GitHub issues.*

---

## Key Revocation (if needed)

To revoke a key, add it to the revocation list in `cmd_activate()` in `scripts/northstar.py`:

```python
REVOKED_KEYS = {
    "NS-PRO-DTML-H6TK-SACG",  # Ryan's original key (exposed in GitHub issue)
    # Add new revocations here
}
```

Commit and push. Takes effect immediately on next `northstar activate` call.
