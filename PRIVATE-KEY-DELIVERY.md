# Private Key Delivery Process

*Written: 2026-03-23 after Customer Zero incident*

## What went wrong

Eli posted Ryan's license key (`NS-PRO-DTML-H6TK-SACG`) publicly in GitHub Issue #1.
Ryan correctly identified this as a security problem.

The key was immediately revoked (commit aa147ed). Anyone who runs `northstar activate NS-PRO-DTML-H6TK-SACG`
now gets: "This license key has been revoked and is no longer valid."

## How to deliver keys privately (going forward)

**When a customer emails steve.glaser.ops@gmail.com asking for their key:**

1. Verify they are a confirmed paying customer (check ledger.md or Venmo/Polar records)
2. Generate a new key: use the python3 command below
3. Reply via email ONLY -- never post the key in a public GitHub issue
4. Update customer-zero.md or the relevant customer file with the new key (locally only)

**Key generation command:**
```bash
python3 -c "
import secrets, string
def gen_key(prefix='NSP'):  # NSP = Pro, NSS = Standard
    chars = string.ascii_uppercase + string.digits
    parts = [''.join(secrets.choice(chars) for _ in range(4)) for _ in range(3)]
    return f'{prefix}-{parts[0]}-{parts[1]}-{parts[2]}'
print(gen_key('NSP'))  # Change to NSS for Standard
"
```

**Email template (Steve can use this):**
```
Subject: Your Northstar Pro License Key

Hi Ryan,

Here is your replacement Northstar Pro license key:

  [KEY]

This is private and single-seat. Please do not share it.

To activate:
  northstar activate [KEY]

If you have any issues, reply to this email.

-- Eli / Northstar
```

## Ryan's pending key delivery

- **Email to watch for:** "Northstar Key - rcraig14" at steve.glaser.ops@gmail.com
- **Replacement key ready:** NSP-KCN9-OOSO-P3Y3
- **Action:** When email arrives, reply with the key above using the template above.

## Process for all future customers (post-Polar setup)

Once Polar.sh is set up, keys are delivered automatically by Polar via email when a customer purchases.
No manual key generation needed. The public GitHub issue is for purchase intents only.

Until Polar is set up, the flow is:
1. Customer opens GitHub issue with tier request
2. Steve/Eli confirm payment via Venmo/PayPal
3. Steve emails the key to the customer's email (obtained from the GitHub issue or Venmo name)
4. NEVER post the key in the GitHub issue
