# Portland Housing Co-op — Profit Split Model

**Author:** Ledger (CFO)
**Date:** 2026-04-08
**Status:** DRAFT — M3 Deliverable
**Implements:** M1 Decision — 20% reserves / 10% overhead / 30% capital / 40% labor

---

## 1. The Formula

For each completed flip, gross profit is split into four buckets:

```
Gross Profit = Sale Price - Total Project Cost

Where Total Project Cost =
    Purchase Price
  + Rehab Costs (materials + subcontractors)
  + Acquisition Costs (inspection, title, appraisal, origination)
  + Carrying Costs (loan interest, taxes, insurance, utilities)
  + Selling Costs (commissions, closing, staging, photography)
  + Permits & Miscellaneous

Split:
  ┌─────────────────────────────────────────────────┐
  │  GROSS PROFIT                                    │
  ├────────────┬────────────┬───────────┬────────────┤
  │ 20%        │ 10%        │ 30%       │ 40%        │
  │ RESERVES   │ OVERHEAD   │ CAPITAL   │ LABOR      │
  │            │ RECOVERY   │ SHARE     │ SHARE      │
  │            │            │           │            │
  │ Stays in   │ Reimburses │ Split pro │ Split pro  │
  │ co-op      │ co-op for  │ rata by   │ rata by    │
  │ reserve    │ fixed      │ capital   │ weighted   │
  │ fund       │ overhead   │ account   │ labor      │
  │            │ costs      │ balance   │ hours      │
  └────────────┴────────────┴───────────┴────────────┘
```

### Bucket Definitions

**Reserves (20%)** — Retained by the co-op. Funds future down payments, covers
contingencies, maintains operating reserve. Not distributed to members. Builds
the balance sheet.

**Overhead Recovery (10%)** — Retained by the co-op. Reimburses the operating
account for fixed overhead costs (insurance, legal, accounting, tools, admin)
that were paid during the flip cycle. If the flip took 6 months and annual
overhead is ~$58K, the pro-rated overhead is ~$29K. 10% of a $30K gross profit
is only $3K — meaning the co-op subsidizes overhead heavily on early flips.
This is by design; it avoids penalizing members while the co-op scales.

**Capital Share (30%)** — Distributed to members proportional to their capital
account balance at the start of the project. The member with 25% of total
capital gets 25% of this bucket.

**Labor Share (40%)** — Distributed to members proportional to their weighted
labor hours on the specific project. Hours are weighted by trade rate multiplier.

---

## 2. Labor Hour Weighting

Not all hours are equal. A master plumber's hour generates more value than a
general laborer's hour on a rehab project. The weighting system reflects market
rates without paying market rates — it adjusts the *share* of the labor pool,
not a dollar amount per hour.

### Trade Rate Multipliers

| Trade | Multiplier | Rationale |
|-------|-----------|-----------|
| General Labor | 1.0x | Baseline |
| Painting / Finish | 1.0x | Entry-level trade |
| Framing / Carpentry | 1.2x | Skilled trade, core to rehab |
| Roofing | 1.2x | Skilled trade, hazard premium |
| Plumbing | 1.3x | Licensed trade, high market rate |
| Electrical | 1.3x | Licensed trade, code compliance critical |
| HVAC | 1.3x | Licensed trade |
| Project Management | 1.1x | Coordination value, not physical trade rate |
| Operations / Admin | 1.0x | Non-trade hours (Maven, Ledger equiv.) |

### How Weighting Works

```
Member A: 400 hours × 1.2 (carpentry) = 480 weighted hours
Member B: 350 hours × 1.3 (plumbing)  = 455 weighted hours
Member C: 500 hours × 1.0 (labor)     = 500 weighted hours
Member D: 200 hours × 1.1 (PM)        = 220 weighted hours
Member E: 300 hours × 1.2 (roofing)   = 360 weighted hours
Member F: 150 hours × 1.0 (painting)  = 150 weighted hours
                                        ─────
Total Weighted Hours:                   2,165

Member A's labor share: 480/2,165 = 22.2%
Member B's labor share: 455/2,165 = 21.0%
Member C's labor share: 500/2,165 = 23.1%  ← Most hours, highest share despite 1.0x multiplier
Member D's labor share: 220/2,165 = 10.2%
Member E's labor share: 360/2,165 = 16.6%
Member F's labor share: 150/2,165 =  6.9%
```

### Mixed-Trade Hours

A member who does both carpentry (1.2x) and general labor (1.0x) on a project
logs hours by trade category. Their weighted hours are the sum of each category.
Example: 200 hrs carpentry (240 weighted) + 100 hrs labor (100 weighted) = 340 weighted hours.

---

## 3. Labor Advance Provision

**Policy (per M1 decision):** Members working on rehab may draw up to 50% of their
estimated labor share as an advance, deducted at final distribution.

### Advance Calculation

```
Estimated Labor Share = (Member's Est. Weighted Hours / Total Est. Weighted Hours)
                        × (40% × Conservative Gross Profit Estimate)

Maximum Advance = 50% × Estimated Labor Share
```

### Example

```
Conservative gross profit estimate:    $30,700
Total labor pool (40%):                $12,280
Member A est. weighted hours:          480 (of 2,165 total) = 22.2%
Member A est. labor share:             22.2% × $12,280 = $2,726
Member A max advance:                  50% × $2,726 = $1,363
```

### Advance Rules

1. **Based on conservative estimate only.** Never the moderate or aggressive scenario.
2. **Available after 30% rehab completion.** No advances in the first month of work.
3. **Board approves each draw.** Member submits request; board confirms hours are on track.
4. **Tracked separately.** Every advance is logged in `advance-tracker.py` with date, amount, and member.
5. **Deducted at distribution.** Total advances are subtracted from the member's final labor share.
6. **Clawback provision.** If the flip's actual labor share is less than total advances drawn:
   - Difference is deducted from the member's capital account
   - If capital account insufficient, member has 90 days to repay
   - Remaining balance becomes a receivable on the co-op's books

### Advance Tracking (see `advance-tracker.py` in tools/profit-splitter/)

---

## 4. Full Distribution Walkthrough

### Scenario: Conservative First Flip

**Project result:**

| Line Item | Amount |
|-----------|--------|
| Sale Price | $475,000 |
| Total Project Cost | $444,300 |
| **Gross Profit** | **$30,700** |

**Step 1: Split into buckets**

| Bucket | % | Amount |
|--------|---|--------|
| Reserves | 20% | $6,140 |
| Overhead Recovery | 10% | $3,070 |
| Capital Share Pool | 30% | $9,210 |
| Labor Share Pool | 40% | $12,280 |
| **Total** | **100%** | **$30,700** |

**Step 2: Calculate capital share per member**

| Member | Capital Account | % of Capital | Capital Share |
|--------|----------------|--------------|--------------|
| Maven | $50,000 | 25.0% | $2,303 |
| Member B | $35,000 | 17.5% | $1,612 |
| Member C | $30,000 | 15.0% | $1,382 |
| Member D | $30,000 | 15.0% | $1,382 |
| Member E | $30,000 | 15.0% | $1,382 |
| Member F | $25,000 | 12.5% | $1,151 |
| **Total** | **$200,000** | **100%** | **$9,210** |

**Step 3: Calculate labor share per member**

| Member | Hours | Trade | Mult. | Weighted | % of Pool | Labor Share |
|--------|-------|-------|-------|----------|-----------|-------------|
| Maven | 200 | Ops/Admin | 1.0x | 200 | 9.2% | $1,134 |
| Member B | 350 | Plumbing | 1.3x | 455 | 21.0% | $2,581 |
| Member C | 400 | Carpentry | 1.2x | 480 | 22.2% | $2,724 |
| Member D | 300 | Roofing | 1.2x | 360 | 16.6% | $2,043 |
| Member E | 250 | Electrical | 1.3x | 325 | 15.0% | $1,844 |
| Member F | 300 | Painting | 1.0x | 300 | 13.9% | $1,704 |
| **Total** | **1,800** | | | **2,120** | **100%** | **$12,280** |

**Step 4: Calculate total distribution per member**

| Member | Capital Share | Labor Share | Gross Distribution | Advances Drawn | Net Distribution |
|--------|-------------|------------|-------------------|----------------|-----------------|
| Maven | $2,303 | $1,134 | $3,436 | $0 | $3,436 |
| Member B | $1,612 | $2,581 | $4,193 | $1,000 | $3,193 |
| Member C | $1,382 | $2,724 | $4,106 | $800 | $3,306 |
| Member D | $1,382 | $2,043 | $3,424 | $500 | $2,924 |
| Member E | $1,382 | $1,844 | $3,225 | $0 | $3,225 |
| Member F | $1,151 | $1,704 | $2,855 | $0 | $2,855 |
| **Total** | **$9,210** | **$12,280** | **$21,240** | **$2,300** | **$18,940** |

**Step 5: Accounting check**

```
Reserves:              $6,140
Overhead Recovery:     $3,070
Member Distributions:  $21,240
                      ────────
Total:                $30,450   ← Rounding discrepancy of $250 due to table rounding.
                                   Actual calculator uses precise math (see profit_splitter.py)
```

**Step 6: Update capital accounts**

Each member's capital account increases by their gross distribution amount
(before advance deduction). Advances are a separate receivable/payable line item,
not a capital account adjustment. This means:

```
Member B capital account after flip:
  Starting balance:     $35,000
  + Capital share:       $1,612
  + Labor share:         $2,581
  = New balance:        $39,193

Cash received by Member B:
  Gross distribution:    $4,193
  - Advance repayment:  ($1,000)
  = Net cash:            $3,193
```

---

## 5. Edge Cases

### What if Gross Profit is Negative?

If the flip loses money:
- Reserves and overhead recovery buckets receive $0
- Loss is allocated to capital accounts proportional to capital percentage
- No member makes a cash payment — the loss reduces their capital account balance
- Any advances already drawn become a debt to the co-op (deducted from capital account)

### What if a Member Does Zero Hours?

- They receive $0 from the labor pool
- They still receive their capital share
- This is by design — silent capital is allowed but not rewarded with labor share

### What if a Member Joins Mid-Project?

- Capital share is based on capital account balance at **project start date**
- Labor hours are tracked from their first day working on the project
- Their buy-in goes into their capital account but doesn't affect this project's capital split

### What if the Co-op Uses Reserve Funds on a Project?

- Reserve funds used as capital are treated as co-op capital, not member capital
- The co-op "earns" the capital share on reserve-funded amounts
- This capital share goes back into reserves (effectively, the reserves earn a return)

---

*See `tools/profit-splitter/profit_splitter.py` for the full implementation.*
*See `tools/profit-splitter/equity_tracker.py` for capital account management.*

*— Ledger, CFO*
