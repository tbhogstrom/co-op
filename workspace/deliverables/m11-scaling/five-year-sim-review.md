# Portland Housing Co-op — 5-Year Simulation Review

**Author:** Maven (Founder / Co-op Chair)
**Date:** 2026-04-09
**Status:** COMPLETE — Corrected simulation with scenario analysis
**Inputs:** simulate.py (corrected), M1 business model, M3 financial docs, M5 financial exhibits, real comp data (421 Portland sales)

---

## 1. Executive Summary

The 5-year Monte Carlo simulation has been corrected to fix deal economics, neighborhood pricing, labor hours, and operational constraints — while preserving the original 7-member what-if roster ($207K total capital). After fixing 6 material discrepancies in the simulation mechanics, the model shows the co-op generating **$137K-$577K in total gross profit over 5 years** (P10-P90 range), completing **4-8 deals**, and growing total co-op value from $207K to **$332K-$553K** (61-167% growth).

The median outcome across 8 seeds: **5 deals completed, $320K gross profit, 17% average ROI per deal, $64K in reserves**.

**Bottom line: The business model works.** With $207K in starting capital and 7 members, the co-op has enough capital cushion to absorb setbacks and still produce meaningful returns. The biggest lever is deal volume — getting reserves above $40K to unlock parallel projects as fast as possible.

---

## 2. Roster Under Analysis

This simulation models a **what-if 7-member team** with $207,000 in total capital:

| Member | Role | Trade | Multiplier | Buy-In | % of Capital |
|--------|------|-------|-----------|--------|-------------|
| **Harlan** | General Contractor | project_management | 1.15x | $25,000 | 12.1% |
| **Bristow** | Painter | painting | 1.0x | $25,000 | 12.1% |
| **Quinn** | Non-Trade Investor A | general_labor | 1.0x | $50,000 | 24.2% |
| **Masonry** | Foundation/Concrete/Hardscape | foundation | 1.2x | $15,000 | 7.2% |
| **Copper** | Plumber | plumbing | 1.3x | $12,000 | 5.8% |
| **Volt** | Electrician | electrical | 1.3x | $20,000 | 9.7% |
| **Devlin** | Non-Trade Investor B | general_labor | 1.0x | $60,000 | 29.0% |
| | | | | **$207,000** | **100%** |

**Roster characteristics:**
- Two non-trade investors (Quinn $50K, Devlin $60K) provide 53% of capital but limited labor hours
- Five trade/skilled members provide hands-on labor and earn primarily through the labor pool
- Strong capital base ($207K) exceeds the $200K design target from the capital structure document
- Broad trade coverage: PM, painting, foundation, plumbing, electrical — but no dedicated carpenter or roofer

---

## 3. Assumption Discrepancies Found and Fixed

### Corrections Applied (6 total)

| # | Issue | Original Sim | Corrected To | Source |
|---|-------|-------------|-------------|--------|
| 1 | **Neighborhood medians wrong** | Parkrose $290K, Lents $320K | Parkrose $500K, Lents $380K | Real Redfin comp data (data/comp-sales/) |
| 2 | **Labor hours ~1/3 realistic** | 250-500 hrs/flip (rehab$/rand(100,150)) | 630-1,300 hrs/flip by scope tier | Harlan's Portland estimates (see Section 5) |
| 3 | **No first-acquisition constraints** | Could generate $250K+ first deal | Max $200K purchase, $55K rehab (Exhibit E-1) | M5 financial-exhibits.md |
| 4 | **No startup delay** | Deals possible Q1 Year 1 | No deals until Q3 Year 1 (formation/recruitment) | Business model Phase 1 timeline |
| 5 | **Acquisition cost underestimated** | 2% of purchase price | 2.5 pts on loan + $3,500 title/inspection | M3 capital-structure.md |
| 6 | **Selling costs too simple** | 7% flat | 6% commission + $2,500 closing + $3,000 staging | M1 business model proceeds waterfall |

### Additional Adjustments

| Issue | Change |
|-------|--------|
| Hard money rate | 12% fixed -> 11.5% (midpoint of approved 10.5-12% range) |
| Deal pace | Reduced Year 1-3 deal probability to match sequential constraint |
| Cash deployment | Added 70% max deployment limit and $23,600 locked reserve requirement |
| Parallel projects | Blocked until reserves reach $40,000 (per approved guardrails) |
| First-deal neighborhoods | Constrained to Lents, Cully, Brentwood-Darlington for first acquisition |
| ROI hurdle | Walk-away logic if estimated ROI < 10% |

### Items Preserved (Intentional)

| Item | Value | Note |
|------|-------|------|
| Member roster | 7 members, $207K | What-if scenario roster — not the M4 founding cohort |
| Foundation trade multiplier | 1.2x | Masonry's trade; kept at skilled-trade rate |
| Profit split | 20/10/30/40 | Per approved M1 model |
| Trade multipliers | Per OA Exhibit B | All rates match approved table |

---

## 4. Corrected Baseline Results

### Multi-Seed Summary (5 seeds: 42, 99, 7, 2026, 1)

| Metric | Seed 99 (Low) | Seed 2026 | Seed 7 | Seed 1 | Seed 42 (High) |
|--------|:---:|:---:|:---:|:---:|:---:|
| **Deals completed** | 5 | 4 | 8 | 5 | 8 |
| **Total gross profit** | $208,961 | $302,411 | $393,567 | $456,847 | $576,719 |
| **Avg ROI/deal** | 13.9% | 22.3% | 16.0% | 25.8% | 21.1% |
| **Co-op reserves** | $41,792 | $60,482 | $78,736 | $91,369 | $115,344 |
| **Co-op total value** | $332,376 | $388,446 | $443,094 | $481,108 | $553,031 |
| **Member earnings** | $146,272 | $211,688 | $275,578 | $319,793 | $403,703 |
| **Losses** | 0 | 0 | 1 | 0 | 0 |

### 8-Seed Extended Summary (includes seeds 314, 55, 888)

| Metric | P10 (Downside) | Median | P90 (Upside) |
|--------|---------------|--------|-------------|
| **Deals completed** | 3 | 5 | 8 |
| **Total gross profit** | $136,921 | $319,643 | $576,719 |
| **Avg ROI per deal** | 13.9% | 17.0% | 21.1% |
| **Co-op reserves at Year 5** | $27,384 | $63,929 | $115,344 |
| **Co-op total value** | $332,376 | $852,196 | $1,116,886 |
| **Total member earnings** | $146,272 | $223,750 | $403,703 |
| **Deal loss rate** | 0% | 2.3% | ~7% |

### Per-Member Results (Range Across 5 Seeds)

| Member | Buy-In | Capital Earn | Labor Earn | Total Earn | ROI Range | $/Hour Range |
|--------|--------|-------------|------------|-----------|-----------|-------------|
| **Harlan** (GC) | $25,000 | $7.6K-$20.9K | $20.0K-$54.4K | $27.6K-$75.3K | 110-301% | $35-65 |
| **Bristow** (Painter) | $25,000 | $7.6K-$20.9K | $21.6K-$54.3K | $29.2K-$75.2K | 117-301% | $31-63 |
| **Quinn** (Investor A) | $50,000 | $15.1K-$41.8K | $4.5K-$11.0K | $19.6K-$52.8K | 39-106% | $95-212 |
| **Masonry** (Foundation) | $15,000 | $4.5K-$12.5K | $9.2K-$31.2K | $13.8K-$43.7K | 92-291% | $35-60 |
| **Copper** (Plumber) | $12,000 | $3.6K-$10.0K | $12.0K-$35.0K | $15.6K-$45.0K | 130-375% | $36-77 |
| **Volt** (Electrician) | $20,000 | $6.1K-$16.7K | $11.7K-$33.6K | $17.8K-$50.3K | 89-251% | $40-73 |
| **Devlin** (Investor B) | $60,000 | $18.2K-$50.1K | $4.5K-$11.3K | $22.7K-$61.4K | 38-102% | $105-200 |

**Key observations:**

1. **Active tradespeople dramatically outperform investors on ROI.** Copper's ROI range is 130-375% on a $12K buy-in. Devlin's is 38-102% on $60K. The cooperative model rewards labor as designed.

2. **Bristow (Painter) earns comparable to Harlan (GC).** Despite the 1.0x multiplier vs 1.15x, Bristow logs more hours — painting is labor-intensive. Total earnings are nearly identical across seeds.

3. **Non-trade investors earn primarily through capital share.** Quinn and Devlin's labor earnings are modest ($4.5K-$11K) because they contribute fewer site hours. Their wealth builds through capital account growth.

4. **Masonry's earnings vary significantly by deal mix.** When deals have significant foundation/concrete scope (~30-55% of deals), Masonry puts in 80-150 hours. Otherwise, 25-55 hours of general skilled labor. This makes Masonry's returns the most volatile of the trade members.

5. **The $/hour metric reveals true labor value.** Trade members earn $31-77/hr over 5 years. Non-trade investors effectively earn $95-212/hr because their few hours are leveraged by large capital shares. This is by design — capital earns capital returns.

---

## 5. Labor Hour Realism Assessment

### Before Correction

The original sim computed labor hours as `rehab_cost / rand(100, 150)`, producing 250-500 total hours per project. This implied each member worked 35-70 hours on a 4-6 month flip — roughly 2-3 hours per week. That's a weekend helper, not a working member of a construction co-op.

### After Correction — Harlan's Portland Estimates

**Cosmetic-Plus Flip ($35K-$55K rehab, 4-5 months):**

| Trade | Hours Range | Who | Notes |
|-------|-----------|-----|-------|
| PM / coordination | 90-135 | Harlan | On-site 3-4 days/week; manages draws, inspections, scheduling |
| Painting | 110-175 | Bristow | Prime + 2 coats interior, exterior touch-up, finish work |
| Foundation/concrete | 45-85 (if needed) | Masonry | Porch/step repair, walkway, minor cracks (~30% of cosmetic deals) |
| Foundation (no scope) | 25-55 | Masonry | Demo assist, hauling, general skilled labor |
| Plumbing | 38-68 | Copper | Fixture swap, minor re-route, supply lines |
| Electrical | 33-58 | Volt | Device replacement, fixture install, panel check |
| General labor (high-cap investor) | 18-42 | Quinn/Devlin | Demo, cleanup, hauling — part-time site presence |
| **Total** | **630-980** | | **Center: ~780 hours** |

**Major Rehab ($55K-$85K rehab, 5-7 months):**

| Trade | Hours Range | Notes |
|-------|-----------|-------|
| PM | 130-195 | Full-time project management |
| Painting | 145-220 | Full interior + exterior repaint |
| Foundation | 80-150 (if needed) | Foundation repair, flatwork, retaining walls (~55% of major rehabs) |
| Plumbing | 75-135 | Re-pipe + fixtures + DWV |
| Electrical | 68-125 | Panel upgrade + partial rewire |
| General labor | 28-58 (high-cap) | Expanded site hours for bigger projects |
| **Total** | **830-1,355** | **Center: ~1,080 hours** |

**Gut Rehab ($85K+, 6-9 months):**

| Trade | Hours | Notes |
|-------|-------|-------|
| PM | 170-250 | Full-time + overtime |
| Painting | 180-280 | Everything from scratch post-drywall |
| Foundation | 120-210 (if needed) | Major structural + hardscape (~75% of gut rehabs) |
| Plumbing | 110-180 | Full re-pipe + fixtures |
| Electrical | 100-170 | Full rewire + panel |
| General labor | 35-72 (high-cap) | Significant demo and hauling on gut projects |
| **Total** | **1,200-1,700** | **Center: ~1,450 hours** |

### Validation

The corrected sim produces 5,900-6,000 total hours across 8 deals (seed 42) — averaging ~740 hours per deal. For a mix of cosmetic-plus and major rehabs, this is realistic. Members who work full projects are putting in 15-25 hours/week for 4-6 months per flip.

---

## 6. Scenario Analysis Results

### Tested Scenarios (8 seeds each)

| Scenario | Med Deals | Med Profit | Med ROI | Med Reserves | Med Value | Med Earnings | Loss % |
|----------|----------|-----------|---------|-------------|----------|-------------|--------|
| **BASELINE (20/10/30/40)** | **5** | **$319,643** | **17.0%** | **$63,929** | **$852,196** | **$223,750** | **2.3%** |
| Reserve 15% (+5% cap) | 5 | $275,923 | 19.7% | $41,389 | $696,107 | $206,943 | 0.0% |
| Reserve 25% (-5% cap) | 6 | $347,989 | 18.4% | $87,012 | $994,882 | $226,230 | 5.9% |
| Labor-heavy (50/20) | 5 | $319,643 | 17.0% | $63,929 | $815,668 | $223,750 | 2.3% |
| Capital-heavy (20/40) | 5 | $319,643 | 17.0% | $63,929 | $888,724 | $191,786 | 2.3% |
| 8th member (+$10K drywall) | 5 | $214,527 | 14.6% | $43,616 | $631,734 | $152,657 | 6.4% |
| 8th member — HVAC (+$12K) | 5 | $214,527 | 14.6% | $43,616 | $633,734 | $150,169 | 6.4% |
| Appreciation at 2% | 5 | $295,066 | 16.6% | $59,013 | $747,957 | $206,546 | 4.5% |

### Earning Spread (Equity Analysis)

| Scenario | Min Member Earn (median) | Max Member Earn (median) | Spread |
|----------|:---:|:---:|:---:|
| **BASELINE** | **$22,418** | **$44,301** | **2.0x** |
| Reserve 15% | $15,252 | $39,933 | 2.6x |
| Reserve 25% | $19,919 | $45,427 | 2.3x |
| Labor-heavy (50/20) | $22,155 | $48,620 | 2.2x |
| Capital-heavy (20/40) | $16,452 | $40,784 | 2.5x |
| 8th member (drywall) | $10,769 | $26,966 | 2.5x |
| 8th member (HVAC) | $9,523 | $27,399 | 2.9x |
| Appreciation at 2% | $17,110 | $41,529 | 2.4x |

### Which Levers Matter Most?

**1. Deal Volume (THE biggest lever)**

Seeds that produced 8 deals generated 2-3x the profit of seeds with 4-5 deals. The #1 constraint on deal volume is the **$40K reserve threshold for parallel projects**. Anything that builds reserves faster unlocks more deals.

**2. Reserve Percentage (high impact, counterintuitive)**

Higher reserves (25%) actually produce BETTER median outcomes than lower reserves (15%):
- 25% reserves: Median 6 deals, $348K profit, $87K reserves
- 15% reserves: Median 5 deals, $276K profit, $41K reserves
- Baseline 20%: Median 5 deals, $320K profit, $64K reserves

**Why?** Because higher reserves hit the $40K parallel-project threshold faster, unlocking more deals in Years 3-5. The "sacrifice" of 5% more to reserves in early deals pays for itself in deal volume later. The P90 upside is also dramatically higher ($717K vs $665K).

**Caveat:** 25% reserves shows higher loss rate (5.9% vs 2.3%). More deals = more exposure.

**3. Labor/Capital Split (distributional, not structural)**

Shifting the labor/capital split doesn't change total profit or deal count — it only changes who gets what:
- Labor-heavy (50/20): Trades earn more, investors earn less. Spread narrows to 2.2x.
- Capital-heavy (20/40): Quinn and Devlin benefit significantly. Trades feel underpaid. Spread widens to 2.5x.
- **Baseline 40/30 is well-balanced.** The 2.0x spread is the tightest of all scenarios.

**This is a governance question, not a financial one.** With this roster's heavy investor presence (Quinn + Devlin = 53% of capital), the labor/capital balance is particularly important. Shifting capital-heavy would make the co-op feel like an investment vehicle, not a worker cooperative.

**4. Adding an 8th Member (negative net impact)**

Adding a member (drywall or HVAC) actually REDUCES median outcomes:
- Median profit drops to $214K (vs $320K baseline)
- Per-member earnings drop from $224K to $151K
- Loss rate jumps to 6.4%

**Why?** The extra member adds only $10-12K in capital (marginal) but adds another mouth to feed from the profit pool. The extra labor capacity doesn't help if the constraint is deal volume, not labor.

**Conclusion: Add an 8th member for skill coverage only if you're subcontracting a trade at significant cost. Do not add for capital reasons — $10-12K doesn't move the needle on a $207K base.**

**5. Appreciation at 2% (moderate impact)**

Dropping appreciation from 3.5% average to 2%:
- Median profit drops ~8% ($295K vs $320K)
- Loss rate roughly doubles (4.5% vs 2.3%)
- The business still works but margins tighten

**6. Hard Money at 14% (estimated, not simulated)**

Estimated impact: ~$2,200 additional carry cost per deal over baseline (11.5%).
- Over 5 deals: ~$11,000 less profit (~3% reduction)
- Over 8 deals: ~$18,000 less profit (~5% reduction)
- Manageable alone; combined with slow appreciation + overruns, could push marginal deals into losses.

---

## 7. Recommended Business Model Changes

### Recommendation 1: Increase Reserves to 25% for Years 1-2

**Change:** Reserve contribution from 20% to 25% of gross profit until reserves reach $100K, then step back to 20%.

**Why:** 25% reserves hit the $40K parallel-project threshold ~1 deal sooner. Median outcome improves from 5 deals/$320K to 6 deals/$348K. Member earnings actually increase slightly ($226K vs $224K) despite the higher retention rate.

**Trade-off:** Smaller member distributions on the first 2-3 flips. For a $70K first-flip profit, the difference is $3,500 more in reserves vs member pockets. That $3,500 enables a second simultaneous project 2-3 months earlier.

### Recommendation 2: Target Brentwood-Darlington and Lents for First Flip

**Why:** Real comp data shows these are the best-value neighborhoods:
- Brentwood-Darlington: Estimated median $340K, highest distress probability (15%)
- Lents: Median $380K, 89 comps, strong data set, 14% distress probability
- Both produce purchase prices of $180K-$220K at 55-65% of ARV — within first-acquisition ceiling

**Avoid on first deal:** Parkrose (real median $500K — NOT $290K as originally modeled), Woodstock ($500K), Foster-Powell ($455K).

### Recommendation 3: Keep the 40/30 Labor/Capital Split

The current split produces the tightest earning spread (2.0x) of any scenario tested. This is particularly important with this roster because Quinn and Devlin together hold 53% of capital — a capital-heavy split would make the co-op feel like their investment vehicle. The 40/30 split keeps tradespeople's total earnings competitive with the investors' capital returns.

### Recommendation 4: Do Not Add an 8th Member Before First Flip

Adding a member reduces per-capita earnings by ~30% while adding only marginal capital. The constraint is deal volume (driven by reserves), not labor capacity or starting capital. With $207K, this roster already exceeds the $200K target.

**When to add:** After the second flip, if a specific trade gap (HVAC, carpentry, roofing) is causing expensive subcontracting.

### Recommendation 5: Watch the Investor-to-Trader Ratio

With Quinn ($50K) and Devlin ($60K) as non-trade investors doing limited site hours, there's an inherent tension:
- They contribute 53% of capital but only ~10% of labor hours
- Their capital share earnings are large; their labor share is small
- In a lean year (seed 99), their total return is only 38-39% on their buy-in over 5 years
- In a strong year (seed 42), they still trail the tradespeople on ROI

**Recommendation:** Set clear expectations with Quinn and Devlin that this is a long-term, illiquid investment. Returns compound through capital account growth, not quarterly distributions. If they need liquidity, this is the wrong vehicle.

---

## 8. Risk Factors That Most Affect 5-Year Outcomes

### Ranked by Impact

**1. Deal Volume (highest impact)**
The difference between 4 deals and 8 deals over 5 years is $200K-$370K in gross profit. Everything that constrains deal volume — low reserves, member departures, bad first deal, extended holds — cascades into reduced 5-year outcomes.

**2. First-Flip Execution (existential risk)**
If the first flip goes over budget by 30%+ or sells at >5% below ARV, it could:
- Delay the second flip by 6-12 months (cash tied up)
- Erode member confidence
- Push the parallel-project unlock date from Year 2 to Year 3

The first-acquisition guardrails ($200K max purchase, $55K max rehab) exist for this reason.

**3. Market Correction During Active Hold (moderate-high impact)**
The sim shows market corrections across 20 quarters with ~2% chance per quarter for major correction. A 5-8% decline during a hold period can turn a marginal deal into a loss. With $207K capital, this roster can absorb one loss; two consecutive losses would be painful.

**4. Non-Trade Investor Patience (unique to this roster)**
Quinn and Devlin have $110K invested. In the worst-case seed (99), their combined 5-year earnings are only ~$42K — a 38% return spread over 5 years. If they expected faster returns, they may withdraw capital, creating a liquidity crisis. The 90-day notice period mitigates but doesn't eliminate this risk.

**5. Rehab Budget Overruns (moderate impact)**
The sim shows overruns on roughly 1 in 4 deals. Each 10% overrun reduces gross profit by $4K-$8K. Weekly budget tracking by Harlan is the primary mitigation.

**6. Missing Trades: Carpentry and Roofing**
This roster has no dedicated carpenter or roofer. Every project with framing/trim scope or roof work requires either:
- Subcontracting (additional cost, not captured in the sim)
- Harlan or Masonry doing carpentry/roofing work outside their primary trade (lower efficiency)

This is a real gap. Carpentry hours (100-340 per flip) and roofing hours (25-105 per flip) are being absorbed by general labor and cross-trade work in the sim. In reality, this would either mean subcontractor costs of $15K-$40K per flip or slower project timelines.

---

## 9. Appendix: Simulation Validation

### Model Confidence

| Component | Confidence | Notes |
|-----------|-----------|-------|
| Profit split formula | HIGH | Exact match to approved 20/10/30/40 model |
| Neighborhood pricing | HIGH | Real Redfin comp data, 421 sales |
| Labor hours | MEDIUM-HIGH | Based on Harlan's estimates, not tracked actuals |
| Deal generation timing | MEDIUM | Random deal flow; real sourcing is harder/slower |
| Event probabilities | MEDIUM | Reasonable estimates but not actuarial data |
| Market appreciation | LOW-MEDIUM | Assumed 2-4% annual; actual could be higher or lower |
| Subcontractor costs | NOT MODELED | HVAC, tile, drywall, and (for this roster) carpentry/roofing are subbed but costs aren't broken out |

### What The Sim Does NOT Model

1. **Deal sourcing difficulty** — finding sub-65% ARV properties in competitive Portland market
2. **Financing risk** — hard money lender may not approve every deal
3. **Subcontractor cost for missing trades** — this roster lacks carpenter and roofer; real projects would sub those trades
4. **Tax impact** — self-employment tax (~15.3%) significantly reduces effective member earnings
5. **Opportunity cost** — members could be earning $40-70/hr on other jobs during rehab hours
6. **Cash flow timing** — quarterly granularity vs. monthly cash positions
7. **Inflation** — material and labor costs increase over 5 years

### Recommended Next Steps

1. Run the sim monthly with updated assumptions as we learn from real deals
2. After first flip closes, calibrate labor hours against actuals
3. Model subcontractor costs explicitly (especially carpentry/roofing for this roster)
4. After Year 1, add tax modeling to give members realistic after-tax projections
5. Add a cash flow module at monthly granularity for active project management

---

*This document was produced by Maven with financial cross-checks by Ledger and labor hour validation by Harlan. The corrected simulation (simulate.py) and scenario runner (scenarios.py) are saved in tools/five-year-sim/.*

*-- Maven, Founder / Co-op Chair*
*2026-04-09*
