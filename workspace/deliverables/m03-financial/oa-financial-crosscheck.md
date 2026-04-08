# Portland Housing Co-op -- OA Financial Cross-Check

**Author:** Ledger (CFO)
**Date:** 2026-04-08
**Status:** DRAFT -- M3 Deliverable
**Documents Compared:**
- Operating Agreement (workspace/deliverables/m02-legal/operating-agreement.md) -- Articles IV and VIII
- Capital Structure (workspace/deliverables/m03-financial/capital-structure.md)
- Profit Split Model (workspace/deliverables/m03-financial/profit-split-model.md)

---

## Summary

The Operating Agreement generally implements the M1-approved financial model correctly. The four-way profit split (20/10/30/40), capital account structure, and advance mechanism are all present and consistent in overall design. However, there are **six discrepancies** in the trade rate multipliers and **four gaps** where the financial model includes provisions that are missing or different in the OA.

**Action needed:** Statton must reconcile the trade multipliers before member execution.

---

## 1. Amounts and Percentages -- ALIGNED

| Item | OA (Art. IV/VIII) | Financial Model | Match? |
|------|-------------------|-----------------|--------|
| Minimum buy-in | $5,000 (Sec 4.2) | $5,000 | YES |
| Maximum buy-in | $50,000 (Sec 4.2) | $50,000 | YES |
| Reserve allocation | 20% (Sec 8.2a) | 20% | YES |
| Overhead recovery | 10% (Sec 8.2b) | 10% | YES |
| Capital share | 30% (Sec 8.2c) | 30% | YES |
| Labor share | 40% (Sec 8.2d) | 40% | YES |
| Max advance | 50% of est. labor share (Sec 8.4a) | 50% | YES |
| Capital share basis | Capital Account at project start (Sec 8.2c) | Capital Account at project start | YES |
| Labor share basis | Weighted Labor Hours (Sec 8.2d) | Weighted Labor Hours | YES |

---

## 2. Trade Rate Multipliers -- DISCREPANCY

This is the most significant finding. The OA (Section 8.3b) and the financial model (profit-split-model.md, labor-tracking-template.md) define **different multipliers** for several trades.

| Trade | OA (Sec 8.3b) | Profit Split Model | Labor Tracking Template | Profit Splitter Code |
|-------|---------------|-------------------|------------------------|---------------------|
| General Labor | 1.0x | 1.0x | 1.0x | 1.0x |
| Painting / Finish | 1.0x | 1.0x | 1.0x | 1.0x |
| **Carpentry / Framing** | **1.0x** | **1.2x** | **1.2x** | **1.2x** |
| **Roofing** | **1.1x** | **1.2x** | **1.2x** | **1.2x** |
| **Plumbing** | **1.2x** | **1.3x** | **1.3x** | **1.3x** |
| **Electrical** | **1.2x** | **1.3x** | **1.3x** | **1.3x** |
| **HVAC** | **1.2x** | **1.3x** | **1.3x** | **1.3x** |
| **Project Management** | **1.15x** | **1.1x** | **1.15x** | **1.15x** |

**Impact:** These differences materially affect member distributions. Using the OA multipliers, a carpenter's hours would be worth 17% less than under the financial model. For Birch with 400 hours of carpentry on a $30,700 GP project, the difference is approximately $400 in labor share.

**Recommendation:** The financial model's multipliers (the higher set) are more reflective of Portland market rate differentials. The OA should be updated to match. Alternatively, if Statton drafted lower multipliers intentionally, the financial model and code must be updated to match the OA. Either way, all four documents must agree.

**Note on PM multiplier:** The profit-split-model.md says 1.1x for Project Management, but both the labor-tracking-template.md and the profit_splitter.py code use 1.15x. The OA also uses 1.15x. Recommend standardizing PM at 1.15x everywhere.

---

## 3. Advance Policy -- PARTIAL GAP

| Rule | OA | Financial Model | Match? |
|------|-----|-----------------|--------|
| Max advance = 50% of est. labor share | Sec 8.4(a): Yes | Yes | YES |
| Based on conservative estimate | Sec 8.4(b): "conservative assumptions" | "conservative estimate only" | YES |
| Board approves each draw | Sec 8.4(c): Partial -- Treasurer can approve up to $3K/mo | Board approves each draw | PARTIAL |
| **30% completion gate** | **NOT IN OA** | **Sec 3, Rule 2: "Available after 30% rehab completion"** | **GAP** |
| Deducted from final distribution | Sec 8.4(d): Yes | Yes | YES |
| Clawback if advance > actual share | Sec 8.4(d): Repay within 60 days | Deducted from capital account; 90 days to repay | PARTIAL |
| Advances are not wages | Sec 8.4(f): Yes | Yes | YES |

**Gaps identified:**

### 3a. 30% Completion Gate -- MISSING FROM OA

The M1 decision explicitly states: "Available after 30% rehab completion." The profit-split-model.md repeats this rule. The advance-tracker.py enforces it. But the OA (Section 8.4) does not mention a completion threshold at all.

**Risk:** Without the completion gate in the OA, a member could legally demand an advance on Day 1 of a project, before any rehab work has been verified. The board could deny it under Section 8.4(e) (cash flow), but the specific 30% gate should be codified.

**Recommendation:** Add to Section 8.4, new subsection (b-1): "No Labor Advance shall be made until the Project has reached at least thirty percent (30%) completion, as certified by the Project Manager or Responsible Managing Individual."

### 3b. Clawback Timeline Discrepancy

The OA gives 60 days for repayment of over-draws (Sec 8.4(d)). The financial model (profit-split-model.md, Sec 3, Rule 6) says: "If capital account insufficient, member has 90 days to repay." These should be aligned.

**Recommendation:** Standardize on 60 days (the OA term), and update the financial model to match.

### 3c. Advance Approval Authority

The OA (Sec 8.4c) gives the Treasurer authority to approve advances up to $3,000/month without a full board vote. The financial model (profit-split-model.md) says "Board approves each draw" without mentioning the Treasurer delegation.

**Impact:** This is not a conflict -- the OA is more specific and adds a practical delegation. The financial model and advance tracker should note this distinction. The advance tracker's `board_approval_ref` field should accept "Treasurer Approval" for draws under $3K/mo.

---

## 4. Capital Withdrawal -- MINOR DIFFERENCES

| Item | OA (Sec 4.7) | Capital Structure | Match? |
|------|-------------|-------------------|--------|
| 90-day written notice | Yes | Yes | YES |
| Not during active projects | Yes (deferred to 30 days after sale) | Yes ("Not permitted during active projects") | YES |
| Minimum reserve protection | Yes ($20,000) | Yes (3 months overhead ~$14,600) | PARTIAL |
| Payment timeline | 60 days, or 12-month installments | 90 days lump sum | PARTIAL |
| **Involuntary redemption** | **120 days or 12-month installments (Sec 11.3)** | **180 days (capital-structure.md)** | **DISCREPANCY** |
| **Death/disability** | **120 days or 12-month installments (Sec 11.3)** | **180 days (capital-structure.md)** | **DISCREPANCY** |

**Recommendation:** The OA terms (120 days / 12-month installment option) are more detailed and protect the co-op's cash flow better. Update the capital-structure.md to match the OA's terms.

---

## 5. Loss Allocation -- ALIGNED

| Item | OA (Sec 8.6) | Financial Model | Match? |
|------|-------------|-----------------|--------|
| Loss allocated pro rata by capital | Yes | Yes | YES |
| No capital account below zero | Yes | Yes | YES |
| No obligation for additional contributions | Yes | Yes (implicit) | YES |
| Advances become debt to co-op | Sec 8.4(d): Yes, 60-day repayment | Yes | YES |

---

## 6. Tax Provisions -- ALIGNED

| Item | OA (Sec 8.7-8.8) | Financial Model | Match? |
|------|------------------|-----------------|--------|
| IRC 704(b) compliance | Yes | Yes (implicit) | YES |
| K-1 within 75 days of year-end | Yes (Sec 8.7) | Yes | YES |
| No withholding from distributions | Yes (Sec 8.8) | Yes | YES |
| Members responsible for own taxes | Yes (Sec 8.8) | Yes | YES |

---

## 7. Terminology -- ALIGNED

The OA uses legally precise terms that map cleanly to the financial model:

| OA Term | Financial Model Term | Consistent? |
|---------|---------------------|-------------|
| Gross Profit (Sec 1.13) | Gross Profit | YES |
| Capital Account (Sec 1.5) | Capital Account | YES |
| Capital Share (Sec 1.7) | Capital Share | YES |
| Labor Share (Sec 1.16) | Labor Share | YES |
| Labor Advance (Sec 1.14) | Labor Advance | YES |
| Weighted Labor Hours (Sec 1.29) | Weighted Labor Hours | YES |
| Trade Rate (Sec 1.26) | Trade Rate Multiplier | YES |
| Distributable Profit (Sec 1.10) | Gross Profit (used interchangeably) | MINOR |

**Note:** The OA defines "Distributable Profit" (Sec 1.10) separately from "Gross Profit" (Sec 1.13). The financial model uses only "Gross Profit." In practice these appear equivalent (both are Sale Price minus Total Project Cost), but Statton should confirm "Distributable Profit" is not defined differently elsewhere or intended to exclude certain items.

---

## Action Items for Statton

1. **CRITICAL:** Reconcile trade rate multipliers between OA Section 8.3(b) and financial model. One set must be chosen and all documents updated.
2. **IMPORTANT:** Add 30% completion gate to OA Section 8.4 (new subsection).
3. **MINOR:** Align clawback timeline (60 vs 90 days).
4. **MINOR:** Update capital-structure.md involuntary redemption timeline to match OA (120 days).
5. **MINOR:** Standardize PM multiplier at 1.15x in profit-split-model.md.
6. **MINOR:** Confirm "Distributable Profit" and "Gross Profit" are equivalent terms in the OA.

---

*-- Ledger, CFO*
