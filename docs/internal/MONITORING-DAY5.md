# Day 5 Launch Monitoring Plan
*Written by Eli | Day 3 (Session 4) | March 22, 2026*

---

## Launch Day: Monday March 24, 2026

### Timeline

| Time (ET) | Action |
|-----------|--------|
| 8:00 AM | Dave posts LinkedIn (Man and Machine series) |
| 8:00-10:00 AM | Peak LinkedIn engagement window. Monitor for comments. |
| 10:00 AM | Check ClawHub install count (baseline). |
| 12:00 PM | First midday check: any installs? Any issues filed on GitHub? |
| 6:00 PM | End-of-day check: installs, GitHub stars, LinkedIn impressions. |
| 9:00 PM | Log Day 5 results in memory/2026-03-24.md |

---

## What to Monitor

### ClawHub
- Install count for `northstar` (free + paid)
- Any user-submitted issues or comments on listing

### GitHub
- Stars on `northstar-skill`
- Issues opened
- Any forks (secondary signal of developer interest)

### LinkedIn (Dave relays)
- Post impressions
- Engagement rate (likes, comments, reposts)
- DMs asking about Northstar specifically

### Revenue
- Any $19/month Stripe subscriptions from ClawHub billing
- This is the only scoreboard that matters

---

## Success Thresholds (Day 5 Only)

| Signal | Great | Okay | Concerning |
|--------|-------|------|------------|
| ClawHub installs | >20 | 5-20 | <5 |
| GitHub stars | >15 | 5-15 | <5 |
| LinkedIn impressions | >3,000 | 1,000-3,000 | <1,000 |
| Paid conversions | >0 | 0 (wait for Day 7) | Still 0 on Day 7 |

**Important:** 0 paid conversions on Day 5 is NOT a failure. The sales cycle for a $19/month tool is typically 3-7 days (evaluate, try, decide). Day 7 is the first real signal.

---

## Issues to Watch For

### Technical
- Install fails: check install.sh path assumptions
- Config template unclear: monitor for GitHub issues mentioning "config"
- Stripe package install fails on macOS Homebrew Python: known issue, fix is in INSTALL.md
- iMessage delivery broken: AppleScript quoting issue (fixed in v1.1 but watch for edge cases)

### Product
- Feature request patterns: what are people asking for in comments/issues?
- Confusion points: anything in INSTALL.md that generates questions = docs failure

### Distribution
- If LinkedIn impressions are low (<1,000): Dave's post timing or hook may have missed
- If installs are 0 after 24 hours: ClawHub listing may not be visible yet, or search ranking issue

---

## Response Playbook

### If installs > 0 but 0 paid after 3 days
1. Check if anyone opened GitHub issues (feature gaps?)
2. Email follow-up to anyone who commented on LinkedIn post (ask 3 questions)
3. Consider: is the $19/month price right? Too high, too low, or irrelevant to the actual barrier?

### If nobody installs at all (0 after 24 hours)
1. Verify ClawHub listing is published and searchable
2. Check if Dave's LinkedIn post link is correct
3. Consider: is ClawHub the wrong channel? Direct outreach to Dave's network?

### If someone files a critical bug
1. Fix immediately. Ship as patch commit.
2. Respond in GitHub issues within the same session.
3. Flag to Dave (board update) if it breaks core functionality.

---

## Customer Zero Protocol (First Paying Customer)

When first paid subscriber appears:
1. Note their name/handle
2. Do NOT spam them
3. Send exactly one personal message: "Thanks for trying Northstar. Three quick questions: [1] What was the moment you decided to pay? [2] What almost stopped you? [3] What would make you upgrade to Pro?"
4. Log their answers in `memory/customer-zero.md`
5. Build the thing they said almost stopped them

This is the most valuable research we will ever get. Don't waste it.

---

## Week 1 End State (Day 7, March 26)

By Day 7, Dave posts a LinkedIn update. Two versions prewritten in LINKEDIN-POST.md:
- Version A: Revenue > $0 - honest progress post
- Version B: Revenue = $0 - honest learning post

Both are interesting. The experiment is the story. Don't spin.

---

*"The experiment is live. Now we see what's real."*
*- Eli | Day 3 | March 22, 2026*
