# Deal Analysis Template — Portland Housing Co-op

**Template Version:** 1.0
**Last Updated:** 2026-04-08
**Based on:** M1 Decisions (Maven), Capitalization Model (Ledger)

---

## Instructions

Use this template for every property the co-op evaluates. Complete all sections before presenting to Maven for go/no-go. Red flags in any section can be disqualifying — don't hide bad news in the narrative.

---

## SECTION 1: Property Summary

| Field | Value |
|-------|-------|
| **Address** | |
| **Neighborhood** | |
| **Sub-zone / Block Grade** | |
| **List Price** | $ |
| **Listing Type** | (REO / Estate / Code Violation / Pre-Foreclosure / Fixer) |
| **Days on Market** | |
| **MLS / Source** | |
| **Sqft** | |
| **Beds / Baths** | |
| **Lot Size (sqft)** | |
| **Year Built** | |
| **Zoning** | |
| **Stories** | |
| **Garage** | |
| **Condition** | (Excellent / Good / Fair / Poor / Very Poor) |
| **Listing Agent / Contact** | |
| **Analysis Date** | |
| **Analyst** | Reeves |

---

## SECTION 2: Condition Assessment

*(Complete after walkthrough with Harlan)*

### Structural Systems

| System | Condition | Action Required | Est. Cost |
|--------|-----------|-----------------|-----------|
| Foundation | | | $ |
| Framing / Structure | | | $ |
| Roof | | | $ |
| Electrical | | | $ |
| Plumbing | | | $ |
| HVAC | | | $ |
| Windows | | | $ |
| Insulation | | | $ |

### Interior

| Area | Condition | Action Required | Est. Cost |
|------|-----------|-----------------|-----------|
| Kitchen | | | $ |
| Bathrooms | | | $ |
| Flooring | | | $ |
| Walls / Paint | | | $ |
| Built-ins / Trim | | | $ |

### Exterior

| Area | Condition | Action Required | Est. Cost |
|------|-----------|-----------------|-----------|
| Siding / Paint | | | $ |
| Landscaping | | | $ |
| Driveway / Walkways | | | $ |
| Garage / Outbuildings | | | $ |
| Fencing | | | $ |

### Environmental / Hazard Flags

| Issue | Status | Notes |
|-------|--------|-------|
| Lead paint (pre-1978) | | |
| Asbestos (siding/insulation/tile) | | |
| Mold | | |
| Radon | | |
| Underground storage tanks | | |
| Flood zone | | |
| Environmental contamination | | |

---

## SECTION 3: Comparable Sales Analysis

*(Run through `tools/comp-analyzer/`)*

| # | Address | Sale Date | Sale Price | Sqft | Beds/Baths | Condition | Adj. Price |
|---|---------|-----------|-----------|------|-----------|-----------|-----------|
| 1 | | | $ | | | | $ |
| 2 | | | $ | | | | $ |
| 3 | | | $ | | | | $ |
| 4 | | | $ | | | | $ |
| 5 | | | $ | | | | $ |

**Comp Summary:**
- Indicated value range: $______ - $______
- Median adjusted value: $______
- Comp confidence: (High / Medium / Low)
- Notes: ______

---

## SECTION 4: ARV Calculation

*(Run through `tools/arv-calculator/`)*

| Method | Value | Weight | Notes |
|--------|-------|--------|-------|
| Comp-Based | $ | 50% | |
| Price/Sqft | $ | 30% | |
| % of Improvement | $ | 20% | |
| **Weighted ARV** | **$** | | |

**Confidence Range:**
- Low (10th pctile): $______
- Mid (50th pctile): $______
- High (90th pctile): $______

**Confidence Level:** (High / Medium / Low)

---

## SECTION 5: Financial Analysis

### Deal Parameters (M1 Standards)

| Parameter | Threshold | This Deal | Pass? |
|-----------|-----------|-----------|-------|
| Purchase ≤ 65% of ARV | 65% | ____% | |
| ROI ≥ 15% | 15% | ____% | |
| Hold ≤ 6 months | 6 mo | ____ mo | |
| Rehab ≤ 25% of ARV | 25% | ____% | |

### Capital Stack

| Line Item | Amount |
|-----------|--------|
| **Purchase Price** | $ |
| Hard Money Loan (85% LTV) | ($ ) |
| **Co-op Down Payment (15%)** | $ |
| **Rehab Budget** | $ |
| Hard Money Rehab Draw (70%) | ($ ) |
| **Co-op Rehab Cash (30%)** | $ |
| **Total Co-op Cash Required** | **$** |

### Carrying Costs (Monthly)

| Item | Monthly | Hold Period Total |
|------|---------|-------------------|
| Hard Money Interest (11% on loan) | $ | $ |
| Property Tax | $ | $ |
| Insurance (Builder's Risk) | $ | $ |
| Utilities | $ | $ |
| Permits / Misc | $ | $ |
| **Total Monthly Carry** | **$** | **$** |

### Projected P&L

| Line Item | Conservative | Moderate | Aggressive |
|-----------|-------------|----------|-----------|
| **Sale Price (ARV)** | $ | $ | $ |
| Less: Seller Closing (7%) | ($ ) | ($ ) | ($ ) |
| Less: Hard Money Payoff | ($ ) | ($ ) | ($ ) |
| **Net Proceeds** | $ | $ | $ |
| Less: Purchase Price | ($ ) | ($ ) | ($ ) |
| Less: Buyer Closing (4%) | ($ ) | ($ ) | ($ ) |
| Less: Rehab Cost | ($ ) | ($ ) | ($ ) |
| Less: Carrying Costs | ($ ) | ($ ) | ($ ) |
| **Gross Profit** | **$** | **$** | **$** |

### Profit Distribution (per M1 formula)

| Bucket | % of Gross | Conservative | Moderate |
|--------|-----------|-------------|----------|
| Reserves | 20% | $ | $ |
| Overhead Recovery | 10% | $ | $ |
| Capital Share | 30% | $ | $ |
| Labor Share | 40% | $ | $ |
| **Total** | **100%** | **$** | **$** |

### Return Metrics

| Metric | Conservative | Moderate | Aggressive |
|--------|-------------|----------|-----------|
| Gross Profit | $ | $ | $ |
| Gross Margin (%) | % | % | % |
| ROI (profit / total investment) | % | % | % |
| Cash-on-Cash Return | % | % | % |
| Annualized ROI | % | % | % |

---

## SECTION 6: Risk Assessment

### Deal-Level Risk Matrix

| Risk | Probability | Impact | Score | Mitigation |
|------|------------|--------|-------|------------|
| Rehab exceeds budget | | | | |
| Structural surprises | | | | |
| Environmental hazard | | | | |
| Title complications | | | | |
| Extended hold period | | | | |
| ARV overestimation | | | | |
| Market softening during hold | | | | |
| Permit delays | | | | |

### Kill Criteria Check

| Criterion | Status | Notes |
|-----------|--------|-------|
| Foundation issues > $15K? | | |
| Environmental hazards without clear remediation? | | |
| Zoning limiting resale value? | | |
| Title issues not resolvable in 30 days? | | |
| Co-op cash required > 70% of available? | | |

---

## SECTION 7: Deal Score

*(Run through `tools/deal-scorer/`)*

| Component | Score | Threshold | Pass? |
|-----------|-------|-----------|-------|
| Neighborhood Score | /100 | ≥ 65 | |
| Property Score | /100 | ≥ 65 | |
| **Combined Score** | **/100** | **≥ 65** | |
| Projected ROI | % | ≥ 15% | |

**Deal Rating:** (GO / CONDITIONAL / NO-GO)

---

## SECTION 8: Recommendation

### Summary
*(1-2 paragraph assessment: Is this a deal? Why or why not?)*

### Offer Strategy
- **Recommended offer price:** $______
- **Walk-away price:** $______
- **Negotiation notes:** ______

### Required Next Steps (if GO)
- [ ] Harlan: Detailed scope of work and rehab estimate
- [ ] Statton: Title search and lien check
- [ ] Ledger: Verify capital availability and cash flow projection
- [ ] Maven: Board vote to proceed

### Timeline
| Milestone | Target Date |
|-----------|-------------|
| Offer submitted | |
| Inspection | |
| Close | |
| Rehab start | |
| Rehab complete | |
| List for sale | |
| Expected close (exit) | |

---

**Sign-off:**

| Role | Name | Approve? | Date |
|------|------|----------|------|
| Analyst | Reeves | | |
| Construction | Harlan | | |
| CFO | Ledger | | |
| Legal | Statton | | |
| Founder | Maven | | |

---

*This template implements M1 deal standards: purchase ≤65% ARV, ≥15% ROI, ≤6mo hold, rehab ≤25% ARV. All properties must pass all four thresholds AND achieve a combined deal score ≥65 to receive a GO recommendation.*
