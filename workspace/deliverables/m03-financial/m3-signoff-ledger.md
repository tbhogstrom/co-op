# M3 Financial Foundation -- Milestone Sign-Off

**Author:** Ledger (CFO)
**Date:** 2026-04-15
**Status:** FINAL
**Milestone:** M3 -- Financial Foundation
**Recommendation:** CLOSE

---

## 1. Deliverable Status

All M3 deliverables are complete. Each document has been drafted, internally reviewed, and cross-checked against the Operating Agreement.

| # | Deliverable | Location | Status |
|---|-------------|----------|--------|
| 1 | Capital Structure | `m03-financial/capital-structure.md` | COMPLETE |
| 2 | Profit Split Model | `m03-financial/profit-split-model.md` | COMPLETE |
| 3 | Break-Even Analysis (narrative) | `m03-financial/break-even-analysis.md` | COMPLETE |
| 4 | Break-Even Analysis (calculator) | `m03-financial/break-even-analysis.py` | COMPLETE |
| 5 | Cash Flow Template | `m03-financial/cash-flow-template.py` | COMPLETE |
| 6 | Labor Tracking Template | `m03-financial/labor-tracking-template.md` | COMPLETE |
| 7 | Member Capital Ledger | `m03-financial/member-capital-ledger.md` | COMPLETE |
| 8 | OA Financial Cross-Check | `m03-financial/oa-financial-crosscheck.md` | COMPLETE |
| 9 | Member Financial Guide | `m03-financial/member-financial-guide.md` | COMPLETE |
| 10 | Minimum Capitalization Analysis | `m03-financial/minimum-capitalization-analysis.md` | COMPLETE |
| 11 | Profit Splitter Tool | `tools/profit-splitter/profit_splitter.py` | COMPLETE |
| 12 | Equity Tracker Tool | `tools/profit-splitter/equity_tracker.py` | COMPLETE |
| 13 | Advance Tracker Tool | `tools/advance-tracker/advance_tracker.py` | COMPLETE |
| 14 | Financial Exhibits A-E (M5) | `m05-membership/financial-exhibits.md` | COMPLETE |

**Total deliverables: 14. Complete: 14. Incomplete: 0.**

---

## 2. Cross-Document Alignment

The OA financial cross-check (deliverable #8) identified six trade-rate discrepancies and four gaps. All have been resolved. The current state of alignment is confirmed below.

### 2a. PM Rate: 1.15x -- ALIGNED EVERYWHERE

| Document | PM Multiplier | Status |
|----------|--------------|--------|
| Operating Agreement (Exhibit B, Amendment #1) | 1.15x | ALIGNED |
| Profit Split Model (`profit-split-model.md`) | 1.15x | ALIGNED |
| Labor Tracking Template (`labor-tracking-template.md`, code `PM`) | 1.15x | ALIGNED |
| Profit Splitter Tool (`profit_splitter.py`, line 45) | 1.15x | ALIGNED |
| Advance Tracker Tool (`advance_tracker.py`, line 49) | 1.15x | ALIGNED |
| Financial Exhibits (Exhibit B-2) | 1.15x | ALIGNED |

The cross-check originally flagged profit-split-model.md at 1.1x for PM. This has been standardized to 1.15x across all documents and code.

### 2b. Clawback Period: 60 Days -- ALIGNED EVERYWHERE

| Document | Clawback Period | Status |
|----------|----------------|--------|
| Operating Agreement (Section 8.4(d)) | 60 days | ALIGNED |
| Profit Split Model (`profit-split-model.md`, Section 3, Rule 6) | 60 days | ALIGNED |
| Financial Exhibits (Exhibit C-4(b)) | 60 days | ALIGNED |

The cross-check originally flagged profit-split-model.md at 90 days. This has been corrected to 60 days.

### 2c. Involuntary Redemption: 120 Days / 12-Month Installments -- ALIGNED EVERYWHERE

| Document | Involuntary Redemption Terms | Status |
|----------|------------------------------|--------|
| Operating Agreement (Section 11.3) | 120 days lump sum OR 12-month installments, Board's election | ALIGNED |
| Capital Structure (`capital-structure.md`, Section 2) | 120 days lump sum OR 12-month installment plan, co-op's election | ALIGNED |
| Financial Exhibits (Exhibit D-2, D-3) | 120 days lump sum OR 12-month installments, Board's election | ALIGNED |

The cross-check originally flagged capital-structure.md at 180 days. This has been corrected to 120 days / 12-month installment option.

### 2d. Trade Rate Multipliers: All 9 Classifications -- ALIGNED EVERYWHERE

| Trade Classification | OA Exhibit B | Profit Split Model | Labor Tracking | Profit Splitter | Financial Exhibits |
|---------------------|-------------|-------------------|---------------|----------------|-------------------|
| General Labor | 1.0x | 1.0x | 1.0x | 1.0x | 1.0x |
| Painting / Finish | 1.0x | 1.0x | 1.0x | 1.0x | 1.0x |
| Framing / Carpentry | 1.2x | 1.2x | 1.2x | 1.2x | 1.2x |
| Roofing | 1.2x | 1.2x | 1.2x | 1.2x | 1.2x |
| Plumbing | 1.3x | 1.3x | 1.3x | 1.3x | 1.3x |
| Electrical | 1.3x | 1.3x | 1.3x | 1.3x | 1.3x |
| HVAC | 1.3x | 1.3x | 1.3x | 1.3x | 1.3x |
| Project Management | 1.15x | 1.15x | 1.15x | 1.15x | 1.15x |
| Operations / Admin | 1.0x | 1.0x | 1.0x | 1.0x | 1.0x |

The cross-check originally identified six discrepancies between the OA and the financial model (Carpentry, Roofing, Plumbing, Electrical, HVAC, PM). The OA has been updated (Amendment #1) to adopt the financial model's multipliers. All nine classifications now match across all documents and code.

### 2e. Dual-Signature Threshold: $2,500 -- ALIGNED

| Document | Dual-Sig Threshold | Status |
|----------|-------------------|--------|
| Operating Agreement (Section 9.4) | $2,500 | ALIGNED |
| Capital Structure (`capital-structure.md`, Section 6) | $2,500 | ALIGNED |

---

## 3. Capitalization Position

### Projected Capitalization

| Metric | Value | Source |
|--------|-------|--------|
| Projected member equity (moderate scenario) | $115,000 | Founding cohort dashboard / M4 recruitment projections |
| Target capitalization | $200,000 | Capital structure (6-member, full-share configuration) |
| Shortfall vs. target | ($85,000) | |
| Viable at projected level | YES, with guardrails | Minimum capitalization analysis |

### Per-Flip Equity Requirements (85% LTV Hard Money)

| Purchase Price | Equity Needed (incl. reserves) | Surplus at $115K |
|---------------|-------------------------------|-----------------|
| $180,000 | $75,700 | $39,300 (51.9%) |
| $220,000 | $83,300 | $31,700 (38.1%) |
| $260,000 | $90,900 | $24,100 (26.5%) |

### Assessment

$115K is sufficient to fund one acquisition at any price point in our target range ($180K-$260K). The surplus provides a meaningful buffer for the lower end of the range and a thin but workable buffer at the upper end. The co-op is limited to sequential flips (one at a time) at this capitalization level, with a maximum of two flips in Year 1.

---

## 4. First-Year Financial Guardrails

These guardrails are codified in Financial Exhibits (Exhibit E) and are binding constraints on Board action, amendable only by Supermajority Vote.

| Guardrail | Limit | Rationale |
|-----------|-------|-----------|
| **Maximum purchase price (first acquisition)** | $200,000 | Ensures adequate equity cushion; targets Lents/Parkrose price range |
| **Maximum rehab budget (first flip)** | $55,000 | Limits scope to cosmetic-plus; avoids structural risk on first project |
| **Locked reserves before first closing** | $23,600 | $14,600 operating reserve (3 months overhead) + $9,000 project contingency (15% of $60K rehab) |
| **Parallel project threshold** | $40,000 reserve balance | No second acquisition until reserves reach $40K |
| **Change order limit** | $2,500 without Board approval; 15% of rehab budget ($8,250) maximum without Supermajority Vote | Scope control on first flip |
| **Inspection contingency** | $2,000 budgeted for comprehensive inspection | Walk away if discoveries push rehab above $55K |

### Reserve Structure (Pre-Acquisition)

```
Locked Reserves: $23,600
  Operating Reserve (3 months overhead):      $14,600
  Project Contingency (15% of rehab budget):  $ 9,000

Replenishment Rule:
  If reserves drawn below $23,600, allocation increases
  from 20% to 25% of next project's Gross Profit until restored.
```

---

## 5. Risks and Open Items

### Resolved During M3

| Item | Resolution |
|------|-----------|
| Trade rate discrepancies (6 trades between OA and financial model) | OA updated via Amendment #1 to adopt financial model multipliers |
| PM multiplier inconsistency (1.1x vs. 1.15x) | Standardized at 1.15x everywhere |
| Clawback period inconsistency (60 vs. 90 days) | Standardized at 60 days per OA |
| Involuntary redemption period inconsistency (120 vs. 180 days) | Standardized at 120 days / 12-month installments per OA |
| 30% completion gate missing from OA | Added to OA Section 8.4, new subsection (b-1), per Amendment #2 |
| Advance approval authority (Treasurer delegation) not in financial model | Financial Exhibits (Exhibit C-3) now documents Treasurer approval up to $3K/month |

### Remaining Risks (Carry Forward)

| # | Risk | Severity | Mitigation | Owner |
|---|------|----------|------------|-------|
| 1 | **Capitalization shortfall.** $115K projected vs. $200K target. One bad flip with no cushion could strain the co-op. | MEDIUM | Guardrails (above); continued recruitment during first flip cycle; conservative first acquisition. | Maven (recruitment) / Ledger (guardrail enforcement) |
| 2 | **Catastrophic rehab discovery on first flip.** A $20K-$40K surprise at $115K capitalization would exhaust surplus. | MEDIUM | $2,000 comprehensive inspection budget; $200K purchase ceiling; $55K rehab ceiling; walk-away discipline. | Maven (acquisition) / Harlan (scope) |
| 3 | **Member departure during active project.** At $115K, the co-op may lack liquidity to honor a capital return while a project is in progress. | LOW-MEDIUM | OA provisions: 90-day notice, no withdrawal during active projects, $20K minimum reserve gate, deferral to 30 days post-sale. | Statton (OA enforcement) |
| 4 | **Self-employment tax burden on members.** SE tax (~15.3%) significantly reduces take-home on distributions. | LOW | Statton to evaluate PTE election and S-corp conversion at scale. Flagged in capital-structure.md Section 8. | Statton (tax planning) |
| 5 | **Personal guarantee exposure on hard money.** Lender may require personal guarantees from managing member(s). | LOW | Statton to advise on limiting guarantees. Noted in capital-structure.md Section 4. | Statton (legal) |

### Open Items (Non-Blocking for M3 Closure)

| # | Item | Target Milestone | Owner |
|---|------|-----------------|-------|
| 1 | Finalize actual member names and buy-in amounts in capital table | M4 (Recruitment) | Maven |
| 2 | Evaluate Oregon PTE election for tax optimization | M4/M5 | Statton |
| 3 | Evaluate S-corp election feasibility at scale | Post-Year 1 | Statton |
| 4 | Confirm "Distributable Profit" vs. "Gross Profit" terminology equivalence in OA | M5 (Member Agreement) | Statton |
| 5 | Select time-tracking implementation (spreadsheet vs. Clockify/Toggl) | Pre-first-flip | Maven / Ledger |
| 6 | Establish banking relationships (operating, reserve, project trust accounts) | M4 (post-entity formation) | Ledger |

---

## 6. Sign-Off

All M3 deliverables have been drafted, reviewed, and cross-checked. The capital structure, profit-split model, break-even analysis, cash flow template, labor tracking system, advance tracker, member financial guide, and minimum capitalization analysis are complete and internally consistent. All cross-document discrepancies identified during the OA financial cross-check have been resolved. Financial Exhibits A-E for the Member Agreement (M5 deliverable) have been completed ahead of schedule.

The co-op's projected capitalization of $115,000 is viable for a first acquisition in the $180K-$200K range with the guardrails established in this milestone. The financial model is conservative, the tools are built, and the governance framework is aligned between the Operating Agreement and all financial documents.

Remaining risks are identified, rated, and have documented mitigations. No remaining risk is blocking. Open items are assigned to future milestones with clear owners.

**As CFO, I confirm M3 Financial Foundation is complete and recommend closure.**

---

*-- Ledger, CFO*
*Portland Housing Co-op*
*April 15, 2026*
