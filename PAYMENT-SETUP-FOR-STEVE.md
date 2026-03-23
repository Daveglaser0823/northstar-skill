# Payment Setup - Action Required Before Launch
*Updated by Eli | Day 4 | v1.9.0 | March 23, 2026*
*For Steve (Chairman) - ~15 minutes of work*

---

## What Changed (v1.9.0 Update)

The code now uses **Polar.sh** for payments and license key validation. This replaces the earlier GitHub issue + manual Stripe approach. Polar is simpler for indie software:
- Handles tax compliance globally (Merchant of Record)
- Automatically emails customers their license key after purchase
- License keys auto-validate against their API
- 5% transaction fee only on sales (no monthly fee)

**The code is ready. Polar.sh account setup is the only remaining step.**

---

## Step 1: Create a Polar.sh Account

1. Go to https://polar.sh
2. Sign up with steve.glaser.ops@gmail.com (GitHub OAuth or email)
3. Create an organization - name it **Northstar** or **northstar-skill**
4. Connect a bank account (Stripe Connect via Polar's flow)

**Time: ~10 minutes**

---

## Step 2: Create Two Products

In your Polar dashboard, create two subscription products:

**Product 1: Northstar Standard**
- Name: `Northstar Standard`
- Price: `$19 / month` (recurring)
- Benefits: Add "License Key" benefit (Polar auto-generates these)
  - Prefix: `NSS-`
  - Limit activations per key: `3` (one install per device, reasonable)
- URL slug: `northstar-standard`
- Final URL will be: `https://polar.sh/daveglaser0823/northstar-standard`

**Product 2: Northstar Pro**
- Name: `Northstar Pro`
- Price: `$49 / month` (recurring)
- Benefits: Add "License Key" benefit
  - Prefix: `NSP-`
  - Limit activations: `5`
- URL slug: `northstar-pro`
- Final URL: `https://polar.sh/daveglaser0823/northstar-pro`

**Time: ~5 minutes**

---

## Step 3: Get the Organization ID

After creating the account:
1. Go to Settings (gear icon)
2. Copy your **Organization ID** (UUID format, looks like `a1b2c3d4-...`)
3. Drop it in a file or message me

I'll create `config/polar.json`:
```json
{
  "organization_id": "YOUR-ORG-ID-HERE"
}
```

This enables live license key validation against Polar's API. Without it, keys are validated by prefix format only (still works, just offline).

---

## Option B: Manual Workaround (If Polar Not Ready by Launch)

If Polar setup isn't done before 8 AM launch:

1. When a license request comes in via GitHub issue, reply:
   ```
   Thanks! Send $19 via Venmo (@DaveGlaser) with note "Northstar Standard [your-email]". 
   License key arrives in <1 hour.
   ```
2. After payment confirmed, generate key: `python3 -c "import secrets; print('NSS-' + secrets.token_urlsafe(20).upper()[:20])"`
3. Add key to `config/northstar.json` under `license_keys` array
4. Reply with key

Not ideal, but it closes Customer Zero without missing a sale.

---

## What the Code Does Automatically (Once Polar Is Set Up)

When a customer purchases on Polar:
1. Polar emails them a `NSS-XXXX` (Standard) or `NSP-XXXX` (Pro) license key automatically
2. Customer runs: `northstar activate NSS-XXXXXX`
3. Northstar calls Polar API to validate the key
4. Config updates to `tier: standard` or `tier: pro`
5. Pro features or Standard integrations unlock

Zero manual steps needed after Polar setup.

---

## Links for Reference

- Polar dashboard: https://polar.sh/dashboard
- Polar docs: https://polar.sh/docs/introduction
- License key docs: https://polar.sh/docs/features/benefits/license-keys
- Northstar repo: https://github.com/Daveglaser0823/northstar-skill

---

*Priority: HIGH. Payment processor is the last gap before a complete end-to-end purchase flow.*
*Without it, we can collect interest but not money.*
