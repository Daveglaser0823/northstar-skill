# Fresh Install Audit - Day 7
*Eli | March 26, 2026 | v2.12.0*

## Method
Cloned repo to /tmp, walked through the full user journey as a stranger would: README > demo > doctor > test > upgrade.

## Findings

### P0: Polar.sh purchase URLs return 404
**Severity:** P0 (breaks revenue path)
**Location:** `scripts/northstar.py` lines 1127, 1481-1482, 2078-2079, 2098, 2121
**Issue:** The code references `polar.sh/daveglaser0823/northstar-standard` and `polar.sh/daveglaser0823/northstar-pro` in 6 places. Both URLs return HTTP 404.
**Impact:** Any user who clicks "Purchase" or reads the upgrade prompt hits a dead page. Revenue path is completely broken in-product.
**Fix required:** Either set up Polar.sh products (board action) or replace URLs with the email-based flow from the README.
**Status:** BLOCKED on board. Cannot fix autonomously.

### P1: Example config defaulted to "standard" tier (FIXED)
**Severity:** P1 (breaks first doctor run)
**Issue:** `config/northstar.json.example` had `"tier": "standard"` but no license key. Fresh `doctor` run showed FAIL.
**Fix:** Changed to `"tier": "lite"` (free). Doctor now shows 6 pass, 0 fail on example config.
**Commit:** Included in this session's commit.

### P1: Hardcoded CONFIG_PATH in error message (FIXED)
**Severity:** P1 (confusing error for users with --config flag)
**Issue:** Line 1406 printed the default config path even when `--config` was passed.
**Fix:** Added `config_path` parameter to `cmd_run()`, displays actual path used.
**Commit:** Included in this session's commit.

### Info: README purchase flow vs. code purchase flow mismatch
**Severity:** P1
**Issue:** README says "Email steve.glaser.ops@gmail.com or open a GitHub issue." Code says "Go to polar.sh/..." in 6 places. Users get conflicting instructions.
**Fix:** Once Polar.sh decision is made, unify to one flow everywhere.

### Info: GitHub PAT authentication broken
**Severity:** P1 (blocks traffic monitoring)
**Issue:** `security find-generic-password -s github-pat -w` returns a token that fails GitHub API auth. Can't pull traffic data, repo metrics, or check PR status.
**Status:** Board awareness needed. Doesn't affect users, but blocks my ability to monitor distribution.

## What Works Well
- `northstar demo` works perfectly from a fresh clone, no config needed
- `--help` output is clear with examples
- `doctor --offline` gives actionable PASS/WARN/FAIL
- Install script is well-structured
- Demo output is compelling and realistic
- Error messages guide users to next steps

## Before/After (Example Config Doctor)

**Before fix:**
```
4 passed, 3 warnings, 1 failures
[FAIL] Tier set to 'standard' but no license key present
```

**After fix:**
```
6 passed, 2 warnings, 0 failures
[PASS] Tier: lite (free)
```
