# OA Cross-Check: Operating Agreement vs. Financial Deliverables
# Portland Housing Cooperative, LLC

**Prepared by:** Statton, Legal Counsel
**Date:** 2026-04-08
**Status:** REVIEW NOTES
**Documents Reviewed:**
- Operating Agreement (Statton, m02-legal/operating-agreement.md)
- Capital Structure (Ledger, m03-financial/capital-structure.md)
- Profit Split Model (Ledger, m03-financial/profit-split-model.md)

---

## Purpose

This memo cross-checks the OA draft against Ledger's M3 financial deliverables to identify inconsistencies between legal terms and financial terms. Each discrepancy is flagged with a severity rating and a suggested resolution.

---

## 1. Trade Rate Multipliers — INCONSISTENT

**Severity: HIGH — Must be reconciled before execution.**

The OA (Section 8.3(b), Exhibit B) and Ledger's Profit Split Model (Section 2) use different Trade Rate multipliers:

| Trade | OA Rate | Ledger Rate | Delta |
|-------|---------|-------------|-------|
| Project Manager / GC | 1.15x | 1.1x | -0.05 |
| Plumbing | 1.2x | 1.3x | +0.1 |
| Electrical | 1.2x | 1.3x | +0.1 |
| HVAC | 1.2x | 1.3x | +0.1 |
| Roofing | 1.1x | 1.2x | +0.1 |
| Carpentry / Framing | 1.0x | 1.2x | +0.2 |
| Painting / Finishing | 1.0x | 1.0x | Match |
| General Labor | 1.0x | 1.0x | Match |
| Operations / Admin | (not listed) | 1.0x | OA omits |

**Impact:** These differences directly affect each member's Labor Share calculation. A carpenter working 400 hours receives a 20% larger weighted-hour allocation under Ledger's rates vs. the OA rates.

**Suggested Resolution:** The Board should adopt a single, agreed Trade Rate schedule. I recommend deferring to the rates that best reflect Portland-area market differentials. Ledger's rates (which give more weight to licensed trades and carpentry) appear more closely aligned with market pricing. The OA rates were drafted conservatively. Options:

- **(A) Adopt Ledger's rates in the OA.** Amend Section 8.3(b) and Exhibit B to match Ledger's schedule. This is my recommendation.
- **(B) Adopt OA rates in Ledger's model.** Update the profit-split-model.md to match the OA. This understates the value of licensed trades.
- **(C) Negotiate a compromise schedule.** The Board sets rates by resolution, and both documents reference the Board-adopted schedule.

**Action Required:** Board vote to adopt final Trade Rate schedule. OA and financial model must use the same numbers.

---

## 2. Labor Advance — 30% Completion Gate — MISSING FROM OA

**Severity: HIGH — Must be added to OA before execution.**

Ledger's Profit Split Model (Section 3, Advance Rule #2) states: "Available after 30% rehab completion. No advances in the first month of work."

The OA (Section 8.4) does not include this 30% completion gate. Section 8.4(a) allows a member to request an advance "during the rehabilitation period" without specifying a minimum completion threshold. Section 8.4(b) references "verified Labor Hours to date" but does not tie eligibility to a percentage of project completion.

**Impact:** Without the completion gate in the OA, a member could theoretically request an advance on Day 1 of a project. The 30% threshold is a risk-management mechanism that ensures meaningful progress before cash leaves the entity.

**Suggested OA Amendment:** Add a new subsection 8.4(b-1) or amend 8.4(b):

> "(b) Labor Advances shall not be available until the Project has reached at least thirty percent (30%) completion of the approved rehabilitation scope of work, as determined by the Project manager or RMI."

Renumber subsequent subsections accordingly.

---

## 3. Involuntary Redemption / Death-Disability Timeline — INCONSISTENT

**Severity: MEDIUM — Should be reconciled.**

| Event | OA Provision | Ledger Provision |
|-------|-------------|-----------------|
| Involuntary transfer (death, disability, bankruptcy) | 120 days (Section 11.3) | 180 days (Capital Structure, Section 2, "Death/disability" and "Involuntary redemption") |
| Expulsion — capital return | Installments over 12 months (Section 5.9(d), referencing 4.7(d)) | 180 days, less outstanding obligations (Capital Structure, Section 2, "Involuntary redemption") |

**Impact:** A member's estate or a bankruptcy trustee will look to the OA for the legally binding timeline. If the financial model assumes 180 days but the OA says 120 days, the Co-op may be legally obligated to pay sooner than Ledger's cash flow projections assume.

**Suggested Resolution:** Align to 180 days. The longer period gives the Co-op more flexibility to manage cash flow, particularly if the event occurs during an Active Project. Amend OA Section 11.3:

> "Payment shall be made within one hundred eighty (180) days or in installments over twelve (12) months, at the Board's election."

---

## 4. Non-Compete Duration — INCONSISTENT WITH M1 BRIEF

**Severity: MEDIUM — Policy decision needed.**

The OA (Section 15.6) specifies a six (6) month post-membership non-compete period. The M2 task brief specifies twelve (12) months. The Member Agreement (as drafted) uses twelve (12) months.

**Impact:** If the OA says 6 months and the Member Agreement says 12 months, there is an internal conflict. The more restrictive provision (12 months) is in the Member Agreement, but a court might look to the OA as the governing document.

**Suggested Resolution:** Align both documents. My recommendation is twelve (12) months, which provides better protection for the Co-op's target-market deal pipeline. Amend OA Section 15.6 introductory clause:

> "During the term of a Member's membership and for a period of twelve (12) months following voluntary withdrawal or expulsion:"

---

## 5. Dual-Signature Threshold for Disbursements — INCONSISTENT

**Severity: LOW — Operational, but should be consistent.**

| Document | Threshold |
|----------|-----------|
| OA Section 9.4 | $5,000 (two authorized signers required) |
| Ledger Capital Structure, Section 6 | $2,500 (dual signature on all disbursements) |

**Impact:** The lower threshold ($2,500) provides tighter financial controls. The higher threshold ($5,000) reduces administrative burden.

**Suggested Resolution:** Adopt Ledger's $2,500 threshold in the OA. Tighter controls are appropriate for a startup co-op where trust is being established. Amend OA Section 9.4:

> "Withdrawals over Two Thousand Five Hundred Dollars ($2,500) shall require two (2) authorized signers."

---

## 6. Profit Split Formula — CONSISTENT

**Confirmed aligned.** Both the OA (Section 8.2) and Ledger's Profit Split Model (Section 1) use the same four-bucket formula:

| Bucket | OA | Ledger | Status |
|--------|-----|--------|--------|
| Reserves | 20% | 20% | Match |
| Overhead Recovery | 10% | 10% | Match |
| Capital Share | 30% | 30% | Match |
| Labor Share | 40% | 40% | Match |

The formulas for calculating Capital Share (pro rata by capital account balance at project start) and Labor Share (pro rata by weighted labor hours) are consistent across both documents.

---

## 7. Capital Account Rules — CONSISTENT

**Confirmed aligned.** Key terms match:

| Term | OA | Ledger | Status |
|------|-----|--------|--------|
| Minimum buy-in | $5,000 (Section 4.2) | $5,000 | Match |
| Maximum buy-in | $50,000 (Section 4.2) | $50,000 | Match |
| Payment plans (founders) | Not available (Section 4.2) | Not available | Match |
| No interest on capital | Section 4.5 | Confirmed | Match |
| Withdrawal notice | 90 days (Section 4.7(a)) | 90 days | Match |
| No withdrawal during Active Projects | Section 4.7(b) | Confirmed | Match |
| Non-transferable | Section 11.1 | Confirmed | Match |
| One vote per member | Section 6.1 | Confirmed | Match |

---

## 8. Buy-In Tiers — CONSISTENT

**Confirmed aligned.** The OA (Section 4.2) defines three tiers matching the M1 decision:

| Tier | Range | Status |
|------|-------|--------|
| Tier A — Full Share | $25,000-$50,000 | Match |
| Tier B — Working Share | $10,000-$24,999 | Match |
| Tier C — Sweat Equity Entry | $5,000 | Match |

---

## 9. Loss Allocation — CONSISTENT

Both documents allocate losses proportionally based on capital account balances. Neither requires additional capital contributions on account of losses. Match.

---

## 10. Labor Advance Clawback — CONSISTENT

Both the OA (Section 8.4(d)) and Ledger (Section 3, Advance Rule #6) specify the same clawback mechanism: excess advances are deducted from the member's capital account, with a 90-day repayment period if the capital account is insufficient. Match.

---

## 11. Operations/Admin Trade Classification — MINOR GAP IN OA

**Severity: LOW**

Ledger's Profit Split Model includes "Operations / Admin" as a trade classification at 1.0x (for Maven, Ledger equivalents performing non-trade hours). The OA's Trade Rate Schedule (Section 8.3(b), Exhibit B) does not explicitly list an "Operations / Admin" category, though "General Labor" at 1.0x would cover it functionally.

**Suggested Resolution:** Add "Operations / Administration" at 1.0x to the OA Trade Rate Schedule for clarity. This ensures that non-trade contributions (bookkeeping, deal sourcing, permit coordination) are explicitly recognized and tracked.

---

## Summary of Required Actions

| # | Issue | Severity | Action |
|---|-------|----------|--------|
| 1 | Trade Rate multipliers differ | HIGH | Board adopts single schedule; amend OA Section 8.3(b) and Exhibit B |
| 2 | 30% completion gate missing from OA | HIGH | Add to OA Section 8.4 |
| 3 | Involuntary redemption timeline (120 vs. 180 days) | MEDIUM | Amend OA Section 11.3 to 180 days |
| 4 | Non-compete duration (6 vs. 12 months) | MEDIUM | Amend OA Section 15.6 to 12 months |
| 5 | Dual-signature threshold ($5K vs. $2.5K) | LOW | Amend OA Section 9.4 to $2,500 |
| 6 | Operations/Admin trade not in OA | LOW | Add to OA Trade Rate Schedule |

Items 1 and 2 should be resolved before the OA is circulated for member signatures. Items 3-6 should be resolved before execution but are not blocking for the review cycle.

---

## Limitations

This review memorandum is a draft prepared as part of a simulation exercise. It is not legal advice. It does not create an attorney-client relationship. All cross-references to ORS, IRC, and specific document sections should be verified against the final versions of those documents.
