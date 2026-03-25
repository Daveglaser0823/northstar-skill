# Polar.sh Migration Plan
*Created: March 24, 2026 | Eli*
*Priority: P0 (purchase flow is the #1 conversion killer per ChatGPT eval)*
*Status: SPEC READY -- needs Steve/Dave to execute account setup*

---

## Why

The ChatGPT evaluation verdict: "GitHub issue + Venmo is amateur hour for something asking for recurring subscription revenue." Buyers expect: checkout page, receipt, billing management, cancellation, tax handling, instant provisioning. Not a GitHub issue and personal Venmo.

This is the single highest-impact fix for conversion. The product is solid. The price is right. The purchase flow is broken.

## What Polar.sh Gives Us

- One-click checkout page (hosted, no code needed)
- Instant license key provisioning (no manual key generation)
- Subscription management (upgrade, downgrade, cancel)
- Receipt and tax handling (Merchant of Record)
- Webhook for activation events (future: auto-provision)
- Free for open-source projects. 5% revenue share on paid.

## What Already Exists in Code

The Northstar codebase already has Polar.sh integration stubs:
- `validate_polar_license()` in `northstar.py` (line 1121) -- calls `api.polar.sh/v1/customer-portal/license-keys/validate`
- `cmd_activate()` checks for `config/polar.json` and uses `organization_id` if present
- Tier detection from key prefix (NSS- = standard, NSP- = pro) already works
- Polar checkout URLs already in the activate command help text

**The code is 90% ready. We need the Polar.sh account.**

## Steps for Steve/Dave

### Step 1: Create Polar.sh Organization (~10 min)
1. Go to https://polar.sh
2. Sign in with GitHub (Daveglaser0823 account)
3. Create organization: "northstar" or "daveglaser0823"
4. Note the `organization_id` (UUID) from Settings

### Step 2: Create Products (~5 min)
Create two products with license key benefits:

**Product 1: Northstar Standard**
- Price: $19/month (recurring)
- License key benefit: prefix `NSS-`, 1 activation
- Checkout URL will be: `https://polar.sh/daveglaser0823/northstar-standard`

**Product 2: Northstar Pro**  
- Price: $49/month (recurring)
- License key benefit: prefix `NSP-`, 1 activation
- Checkout URL will be: `https://polar.sh/daveglaser0823/northstar-pro`

### Step 3: Create config/polar.json (~1 min)
```json
{
  "organization_id": "YOUR-ORG-UUID-HERE"
}
```
Place at `product/northstar/config/polar.json`.

### Step 4: Eli Updates (after org is live)

Once Steve confirms the org_id, Eli will:
1. Update `config/polar.json` with the real org_id
2. Update landing page buttons to point to Polar checkout URLs (replacing GitHub issue template links)
3. Update README Subscribe section to use Polar checkout links
4. Update PAYMENT.md to reflect Polar as primary (Venmo as legacy/manual fallback)
5. Remove GitHub issue templates for license requests (no longer needed)
6. Test: purchase flow end-to-end (Polar checkout -> key issued -> activate -> Pro features unlocked)
7. Publish to ClawHub

### Step 5: Ryan Migration
- Ryan's current key (NSP-82DK-6CGV-KLBM) continues working (offline/HMAC validation)
- No action needed from Ryan unless he wants billing management
- Offer Ryan a Polar-provisioned key when ready (free migration, no charge)

## What This Replaces

| Before (Venmo) | After (Polar.sh) |
|----------------|-------------------|
| Open GitHub issue | Click "Buy" on landing page |
| Send Venmo to @Daveglaser-3 | Credit card checkout (hosted) |
| Wait for manual key email | Instant key provisioning |
| No receipt | Automatic receipt + tax |
| No cancellation flow | Self-service billing portal |
| No upgrade path | One-click upgrade |

## Cost

- Polar.sh: Free (5% revenue share on transactions)
- At $49/month: $2.45/month to Polar per Pro subscriber
- At $19/month: $0.95/month to Polar per Standard subscriber
- No upfront cost. No monthly fee. Aligns incentives.

## Timeline

- **Day 5 (today):** Plan written. Ready for Steve/Dave.
- **Day 6-7:** Steve/Dave creates Polar org + products. Shares org_id.
- **Day 7-8:** Eli updates all code, landing page, README. Tests end-to-end. Publishes.
- **Day 8:** New purchase flow live. Venmo becomes fallback only.

## Risk

- Polar.sh account requires GitHub OAuth. Dave's GitHub (Daveglaser0823) is the right account.
- If Polar.sh has issues: Lemon Squeezy or Stripe Checkout are fallback options (more setup, same result).
- Ryan's existing key works indefinitely regardless (HMAC validation doesn't depend on Polar).

---

*This is the single highest-ROI change for Northstar right now. The product works. The purchase flow doesn't.*
