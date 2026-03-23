# Northstar Changelog

## [1.8.2] - 2026-03-23

### Fixed
- **Version string sync**: northstar.py now matches clawhub.json at v1.8.2.
- **CI added**: GitHub Actions workflow for Python 3.10/3.11/3.12 + ruff lint.
- **README badges**: CI status badge, Python version badge.
- **Security hardened**: AST-based formula evaluator replaces eval() in Pro tier.

## [1.8.1] - 2026-03-23

### Fixed
- **Version display bug**: `northstar` status command showed v1.5.0 instead of v1.8.0. Fixed.
- **iMessage config key fallback**: `deliver()` now accepts both `recipient` and legacy `imessage_recipient` config keys. Users who manually copied the config example and used `imessage_recipient` would have silently failed to receive briefings. Now both keys work; `recipient` takes priority.
- **Config example**: Added `recipient` alongside `imessage_recipient` in `northstar.json.example` to avoid user confusion.
- **Test coverage**: Added 3 new delivery tests (30 total, was 27). Tests cover `imessage_recipient` fallback, `recipient` priority, and dry-run output.

---

## [1.8.0] - 2026-03-23

### Added
- **GitHub Issue Templates**: Structured templates for license requests (Standard, Pro), bug reports, and feature requests. Users clicking "Get Standard" or "Get Pro" now get pre-filled issue forms with all required info.
- **Landing page pricing CTAs**: Added "Install Free", "Get Standard", and "Get Pro" buttons to the pricing section on the landing page. Each links to the appropriate GitHub issue template.
- **Landing page version bump**: Footer now correctly shows v1.7.0 (was stuck at v1.5.0).

---

## [1.7.0] - 2026-03-23

### Fixed
- **Critical pre-launch fix:** `northstar.run` domain is owned by a third party (unrelated site). Replaced all payment links with GitHub Issues purchase flow. Users open a GitHub issue to request a license key; key is sent within 24 hours. Affects `northstar activate` prompt, `northstar status` upgrade prompt, and `PAYMENT.md`.
- Test updated to verify new purchase URL format.

---

## [1.6.0] - 2026-03-23

### Added
- **`northstar activate` command**: License key activation flow. Run `northstar activate NS-STD-XXXX-XXXX` after purchase to unlock Standard or Pro tier features. Updates config automatically. Validates key prefix format (NS-STD- / NS-PRO-).
- **PAYMENT.md**: Clear purchase and activation documentation. Links to https://northstar.run/standard and https://northstar.run/pro.
- **4 new activation unit tests**: Covers invalid key format (exits 1), empty key shows usage, NS-STD- validates as standard, NS-PRO- validates as pro. Total tests: 27.
- **`status` command now shows current tier.**

### Changed
- Version updated to 1.6.0 throughout.

---

## [1.5.0] - 2026-03-23

### Added
- **Gumroad integration**: Add your Gumroad API access token to get daily sales metrics alongside Stripe. Shows yesterday's Gumroad revenue, WoW change, sales count, MTD pacing, and refund alerts. Full parity with Lemon Squeezy integration.
- **Gumroad in setup wizard**: Step 7 in `northstar setup` now prompts for Gumroad credentials (optional).
- **Gumroad in config example**: `northstar.json.example` now includes `gumroad` block with inline documentation.
- **8 new Gumroad unit tests**: `tests/test_northstar.py` now covers Gumroad revenue display, WoW change, MTD, sales count, refund alerts, and edge cases. Test count: 23 (core) + 25 (pro) = 48 total.

### Changed
- Version strings updated to 1.5.0 throughout
- Product description updated to reflect Gumroad as fourth data source

---


All notable changes to Northstar are documented here.
Format: [Version] - Date - Summary

---

## [1.4.0] - 2026-03-23

### Added
- **Lemon Squeezy integration**: Add your Lemon Squeezy API key to get combined revenue + subscription metrics alongside Stripe. Shows yesterday's LS revenue, active/new/churned subs, payment failures, and MTD pacing. Wired into `cmd_run`, `build_briefing`, and alert system.
- **Lemon Squeezy in setup wizard**: Step 6 in `northstar setup` now prompts for LS credentials (optional). 
- **Lemon Squeezy in config example**: `northstar.json.example` now includes `lemonsqueezy` block with inline documentation.

### Changed
- Version strings updated to 1.4.0 throughout

---

## [1.3.1] - 2026-03-23

### Fixed
- Version string in `northstar run` output was showing v1.2.0 (cosmetic)

---

## [1.3.0] - 2026-03-23

### Added
- **`northstar setup` command**: Interactive setup wizard. Guides users through all configuration steps (tier, delivery channel, credentials, schedule) without manual JSON editing. Generates a valid config file and immediately runs `northstar test` to verify setup. Estimated setup time drops from 10-12 minutes to 4-5 minutes.
- Error message on missing config now suggests `northstar setup` and `northstar demo` as next steps.

### Changed
- Version string updated to 1.3.0
- CLI help text updated to list `setup` as the second recommended command (after `demo`)

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
