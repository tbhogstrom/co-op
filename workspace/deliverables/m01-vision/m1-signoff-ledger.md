# M1 — CFO Sign-Off

**Author:** Ledger (CFO)
**Date:** 2026-04-08
**Status:** APPROVED — M1 may close

---

## Decision Review

| Decision | Maven's Call | Ledger's Assessment | Status |
|----------|-------------|-------------------|--------|
| Capitalization target: $200,000 | Adopted Ledger's number | Validated across 3 scenarios. Buffer is adequate. | ✅ APPROVED |
| Founding members: 6 | Reduced from 8 | Works. Average buy-in increases to ~$33K. Concentration risk is slightly higher but manageable. | ✅ APPROVED |
| Profit split: 20/10/30/40 | Adopted Ledger's formula | Formula is transparent, auditable, and correctly incentivizes labor. | ✅ APPROVED |
| Buy-in: $5K min, $50K max | Aligned with Ledger's tiers | $5K floor keeps admin manageable. $50K cap prevents ownership concentration. | ✅ APPROVED |
| No payment plans for founders | Maven's decision | Simplifies capitalization timeline. Full $200K available at formation. Good call. | ✅ APPROVED |
| Maven commits $50K | Tier A | Founder sets the standard. 25% of total capital. Strong signal to other recruits. | ✅ APPROVED |
| Entity: Cooperative LLC (ORS Ch. 63) | Maven + Statton | Pragmatic choice — gets cooperative governance with LLC flexibility. Tax treatment as pass-through works for our structure. | ✅ APPROVED |
| Timeline to first distribution: 12-14 months | Maven's estimate | Consistent with my model: 2-3 months formation + 5-6 months rehab + 2-3 months sale + 1 month accounting. Realistic. | ✅ APPROVED |

## Labor Advance Provision — Approved with Conditions

**Decision:** Members working full-time on rehab may draw up to 50% of their estimated labor share as an advance, deducted at distribution.

**Financial impact analysis:**

Conservative scenario (gross profit $30,700):
- Total labor pool: 40% × $30,700 = $12,280
- Maximum total advances (50%): $6,140
- If 4 of 6 members draw advances: ~$4,600 additional cash out during rehab
- Impact on lowest cash balance: drops from ~$263K to ~$258K — **negligible**

**Risk:** If the flip underperforms and the labor pool shrinks, advances already paid may exceed a member's actual labor share. Example: if gross profit comes in at $15,000 instead of $30,700, the labor pool is only $6,000 total. A member who drew $2,000 in advances against an expected $3,000 share now has an actual share of $1,500 — the co-op overpaid by $500.

**Conditions for approval:**
1. Advances are capped at 50% of the *conservative-scenario* labor share estimate, not the moderate or aggressive estimate
2. Advances are a personal obligation — if a member's actual share is less than their total advances, the difference is deducted from their capital account
3. No advances until rehab is ≥30% complete (reduces risk of paying for work that doesn't generate profit)
4. Board must approve each advance draw
5. I will build a tracking mechanism as part of M3 (see `advance-tracker.py`)

**Status:** ✅ APPROVED WITH CONDITIONS ABOVE

---

## M1 Closure Confirmation

All M1 financial parameters are compatible with the operating cost model and business model
previously delivered. No changes needed to existing M1 deliverables — the model already
uses $200K capitalization and the 20/10/30/40 split formula.

**M1 is clear to close from the CFO's desk.**

**M3 is now unblocked.** Starting immediately on:
- Capital structure design
- Profit-split calculator (tools/profit-splitter/)
- Break-even analysis
- Cash flow template with labor advance tracking
- Member capital account templates
- Labor-hour tracking template

— Ledger, CFO
