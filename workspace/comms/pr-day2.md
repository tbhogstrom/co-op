# PR: Day 2 — M2/M3/M4 Deliverables

**Run from your machine after pushing the maven branch:**

```bash
git push -u origin maven

gh pr create --base main --head maven \
  --title "Day 2: M2/M3/M4 deliverables — legal, financial, recruitment" \
  --body "$(cat <<'PREOF'
## Summary

M1 (Vision & Strategy) is closed. Three agents ran in parallel to produce M2, M3, and M4 deliverables:

- **Statton (M2 Legal):** Member agreement, CCB application checklist, tax structure memo, OA cross-check (6 issues found)
- **Ledger (M3 Financial):** Advance tracker tool, labor tracker tool, OA financial cross-check, member financial guide
- **Calloway (M4 Recruitment):** Interview reports for 3 candidates (Birch 87, Slate 84, Copper 97), electrician search (3 leads), founding cohort dashboard, candidate info packet

Maven reviewed all deliverables, reconciled the two independent OA cross-checks, and made 6 amendment decisions.

## Key Findings

- **OA inconsistencies found independently by both Statton and Ledger** — trade rate multipliers mismatch (5/8 categories) and 30% advance completion gate missing. Both HIGH severity. Decisions logged.
- **Capitalization gap** — realistic projection is $115K from 6 members, not $200K target. Ledger to confirm minimum viable with hard money leverage.
- **Copper is the anchor candidate** (97/100). Birch conditional on EPA RRP renewal. Slate needs OA + founders' meeting.

## Files (30 changed, +4,394 lines)

### New deliverables (14 files)
- `m02-legal/` — member-agreement, ccb-application-checklist, tax-structure-memo, oa-review-notes, oa-amendment-decisions
- `m03-financial/` — oa-financial-crosscheck, member-financial-guide
- `m04-recruitment/` — interview-birch, interview-slate, interview-copper, candidate-electrician-search, founding-cohort-status, candidate-info-packet
- `workspace/comms/` — maven-status-2026-04-08

### New tools (2 packages)
- `tools/advance-tracker/` — Python, enforces all M1 advance policy rules
- `tools/labor-tracker/` — Python, weighted hours, profit-splitter integration

### Modified
- `workspace/project-board.md` — full refresh with new artifacts, decisions, blockers
- `.scion/` — removed default_harness_config from templates (Hub not available)

## Test plan

- [ ] Verify all 16 new files are present and non-empty
- [ ] Spot-check OA cross-checks (oa-review-notes.md vs oa-financial-crosscheck.md) for consistency
- [ ] Run `python tools/advance-tracker/advance_tracker.py --help` and `python tools/labor-tracker/labor_tracker.py --help`
- [ ] Confirm project-board.md reflects current state accurately
- [ ] Review oa-amendment-decisions.md for completeness

🤖 Generated with [Claude Code](https://claude.com/claude-code)
PREOF
)"
```
