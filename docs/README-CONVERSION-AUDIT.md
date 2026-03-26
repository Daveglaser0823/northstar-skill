# README Conversion Audit
*Eli | March 26, 2026 (Day 7)*

## The Problem
33 unique visitors (March 22-25), 0 stars, 0 forks, 0 issues. People land on the repo and leave. The README is the only conversion surface we control.

## Issues Found (Priority Order)

### 1. Pricing before value (HIGH)
The pricing table appears before the user has any emotional investment. A visitor from an awesome-list clicks through, sees "Stripe only, terminal output" for free and "$19/month" for useful features. They close the tab.

**Fix:** Move pricing BELOW the install section. Let them see `northstar demo` output first.

### 2. Subscribe flow is bizarre (HIGH)
"Open a GitHub issue, pay via Venmo, wait for email, activate key." This is a 4-step manual process that screams "hobby project." No developer expects to Venmo a GitHub username for software. This alone could kill conversion for anyone who reads past the install section.

**Fix:** Can't change the payment infra without the board, but can de-emphasize it and lead with the free tier value instead.

### 3. No immediate value hook for free users (MEDIUM)
The free Lite tier exists but the README doesn't sell it. A developer with a Stripe account should feel "I can try this in 60 seconds for free." Instead they see a pricing table that makes Lite feel like a crippled version.

**Fix:** Add a "Try it in 60 seconds" section right after the problem statement. Make the free path feel generous, not limited.

### 4. Star CTA is buried and weak (MEDIUM)
The only star ask is at the very bottom: "If Northstar saved you from a morning tab-hop, a star on GitHub helps others find it." Nobody reads to the bottom. And the ask assumes they're already a user.

**Fix:** Add a lighter CTA after the demo output. "Like what you see? A star helps other founders find this."

### 5. "Built by Eli, an AI" disclosure (LOW)
Ethical and correct, but positioned as the closer. Some visitors may interpret "AI built this" as "nobody maintains this." The experiment narrative is a strength for LinkedIn but a potential weakness for GitHub visitors who just want working software.

**Fix:** Keep the disclosure (honesty matters), but move it to a smaller section. Lead with the product value, not the origin story.

## Changes to Make

1. Reorder: Problem > Demo/Install > Data Sources > "Try free in 60 seconds" > Pricing > Subscribe > Built by Eli
2. Add star CTA after demo section
3. Emphasize free-tier instant value
4. Keep all existing content, just restructure the flow
