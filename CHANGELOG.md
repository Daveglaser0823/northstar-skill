# Northstar Changelog

All notable changes to Northstar are documented here.
Format: [Version] - Date - Summary

---

## [1.2.0] - 2026-03-22

### Added
- **`northstar demo` command**: Zero-config onboarding. Run immediately after install to see a realistic sample briefing with demo Stripe + Shopify data -- no API keys, no config file required. Includes next-step prompt guiding users to configure their real credentials.
- Demo command intentionally skips config loading (safe for fresh installs)

### Changed
- Version string updated to 1.2.0 in `northstar.py` and `clawhub.json`
- CLI help text updated to list `demo` as the recommended first command

---

## [1.1.0] - 2026-03-22

### Added
- **Pro tier** (`northstar_pro.py`): extension module for $49/month features
  - `northstar digest` command: weekly digest with 7-day rollup (Sundays)
  - `northstar trend` command: 7-day revenue sparkline with best/worst day analysis
  - Multi-channel delivery: send to up to 3 channels simultaneously (Pro)
  - Custom metrics: user-defined formulas in config with threshold alerts
  - Monthly pacing projection in weekly digest
- **Pro CLI integration**: `digest` and `trend` commands now available from main `northstar` entry point
- **25 Pro unit tests**: `tests/test_northstar_pro.py` covers tier checks, sparkline, trend, custom metrics, weekly digest, multi-channel delivery
- **CLAWHUB-LISTING.md**: full listing copy for ClawHub publisher
- **LINKEDIN-POST.md**: three post versions for Man and Machine series (Dave Glaser)
- **POST-LAUNCH-PLAYBOOK.md**: day 6-14 plan, Customer Zero protocol, contingency
- Updated `clawhub.json` to v1.1.0 with `pro_features` array and `story` block

### Changed
- Version string updated to 1.1.0 in `northstar.py` and `clawhub.json`
- Install script (`install.sh`) creates config directory and copies example on first install

### Fixed (from 1.0.0)
- Config path for example file fixed (was pointing to wrong parent directory)
- `northstar.py` argparser now exits cleanly on unrecognized commands
- iMessage delivery script quoting improved (handles apostrophes, special chars)
- Stripe: `total_count` fallback added for accounts where list metadata isn't exposed
- MTD calculation uses `yesterday_end` (not today's start) to avoid double-counting
- `days_in_month` calculation fixed for December (month 12 edge case)

---

## [1.0.0] - 2026-03-22

### Initial release

- Daily business briefing from Stripe and Shopify
- `northstar run` / `northstar test` / `northstar status`
- `northstar stripe` / `northstar shopify` for raw debug data
- Delivery: iMessage, Slack, Telegram, terminal
- Stripe metrics: yesterday's revenue, WoW change, MTD vs goal, active/new/churned subs, payment failures
- Shopify metrics: orders fulfilled/open, refunds, top product by units
- Alert system: payment failures, high churn, large refunds
- Configurable monthly revenue goal with pacing indicator
- 15 unit tests in `tests/test_northstar.py`
- Full install docs (`INSTALL.md`), OpenClaw skill spec (`SKILL.md`), README

---

*Built by Eli, an autonomous AI agent. Day 3 of 14.*
*Experiment: [Man and Machine series](https://linkedin.com/in/daveglaser)*
