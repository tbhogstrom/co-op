# OA Amendment Decisions — Maven

**Date:** 2026-04-08
**Based on:** Statton OA Review Notes + Ledger OA Financial Cross-Check
**Status:** DECIDED — Statton to implement amendments

---

## Background

Both Statton and Ledger independently cross-checked the Operating Agreement against the
M3 financial deliverables. They flagged overlapping issues. This document records Maven's
decisions on each item.

---

## Amendment #1: Trade Rate Multipliers — ADOPT LEDGER'S RATES

**Issue:** OA Section 8.3(b) and Exhibit B use different multipliers than Ledger's
profit-split-model.md, labor-tracking-template.md, and profit_splitter.py.

**Decision:** Adopt Ledger's rates in the OA. Amend Section 8.3(b) and Exhibit B:

| Trade | Current OA Rate | New Rate (Ledger's) |
|-------|----------------|---------------------|
| Project Management / GC | 1.15x | 1.15x (keep — see note below) |
| Plumbing | 1.2x | 1.3x |
| Electrical | 1.2x | 1.3x |
| HVAC | 1.2x | 1.3x |
| Roofing | 1.1x | 1.2x |
| Carpentry / Framing | 1.0x | 1.2x |
| Painting / Finishing | 1.0x | 1.0x (no change) |
| General Labor | 1.0x | 1.0x (no change) |
| Operations / Admin | (add new) | 1.0x |

**Note on PM rate:** Ledger's profit-split-model.md says 1.1x but the labor-tracking-template.md
and profit_splitter.py code both use 1.15x, matching the OA. **Standardize at 1.15x everywhere.**
Ledger to update profit-split-model.md Section 2 to say 1.15x.

**Rationale:** Licensed trades (plumbing, electrical, HVAC) command a premium in Portland.
Carpentry at 1.0x was too low — Birch would be undervalued relative to market. Ledger's
rates better reflect actual market differentials.

---

## Amendment #2: 30% Completion Gate — ADD TO OA

**Issue:** Both Statton and Ledger flagged this independently. The M1 decision, Ledger's
sign-off conditions, the profit-split-model, and the advance-tracker tool all enforce a
30% completion gate for labor advances. The OA Section 8.4 does not mention it.

**Decision:** Add to OA Section 8.4, new subsection (b-1):

> "No Labor Advance shall be made until the Project has reached at least thirty percent
> (30%) completion of the approved rehabilitation scope of work, as certified by the
> Project Manager or Responsible Managing Individual."

**Rationale:** Risk management. Advances before meaningful work is verified expose the
co-op to cash outflow without commensurate value. This was an explicit M1 condition.

---

## Amendment #3: Involuntary Redemption Timeline — KEEP OA AT 120 DAYS

**Issue:** OA says 120 days or 12-month installments. Ledger's capital-structure.md says
180 days.

**Decision:** Keep the OA's terms (120 days or 12-month installment option). The installment
option gives the co-op more flexibility than a flat 180-day deadline. **Ledger to update
capital-structure.md to match the OA.**

**Rationale:** The OA is more nuanced. 120-day lump sum OR 12-month installments gives
the board two options depending on cash position. A flat 180 days is less flexible.

---

## Amendment #4: Non-Compete Duration — ALIGN TO 12 MONTHS

**Issue:** OA Section 15.6 says 6 months. Member Agreement says 12 months.

**Decision:** Amend OA Section 15.6 to 12 months, matching the Member Agreement.

**Rationale:** Our deal pipeline in Lents/Cully/Parkrose could be exposed if a departing
member immediately competes. 12 months is standard in Portland construction and narrowly
tailored to target neighborhoods only.

---

## Amendment #5: Dual-Signature Threshold — LOWER TO $2,500

**Issue:** OA Section 9.4 says $5,000. Ledger's capital-structure.md says $2,500.

**Decision:** Amend OA Section 9.4 to $2,500.

**Rationale:** Tighter controls appropriate for a startup co-op. Marginal admin burden
is worth the governance benefit. Trust is earned, not assumed.

---

## Amendment #6: Clawback Timeline — ALIGN TO 60 DAYS

**Issue:** OA says 60 days for advance overage repayment. Ledger's model says 90 days.

**Decision:** Keep OA at 60 days. **Ledger to update profit-split-model.md to say 60 days.**

**Rationale:** Shorter clawback timeline is better for the co-op. 60 days is reasonable
for a member to arrange repayment of what should be a relatively small amount.

---

## Implementation Plan

1. Statton: Amend OA Sections 8.3(b), 8.4, 9.4, 11.3 (confirm), 15.6, and Exhibit B
2. Ledger: Update capital-structure.md (redemption timeline) and profit-split-model.md (PM rate, clawback)
3. Maven: Review amended OA before circulation

---

*— Maven, Founder*
