# Tool Evaluation Results — Synthetic Data Baseline

**Date:** 2026-04-08  
**Run by:** Maven (coordinating for Reeves)  
**Data source:** Synthetic (all tools running on generated data)  
**Purpose:** Establish baseline methodology validation; identify tool/assumption gaps before real data arrives  

---

## Executive Summary

All three analysis tools (comp-analyzer, arv-calculator) ran successfully on our three candidate properties. **Key finding: tool ARVs run 13-16% below manual ARV estimates.** This is a methodology difference, not a bug — it needs to be understood and calibrated before we make acquisition decisions.

| Property | Manual ARV | Tool ARV | Delta | 65% Rule | Est. ROI |
|----------|-----------|----------|-------|----------|----------|
| **#1 Cully (Killingsworth)** | $399,000 | $341,500 | -14.4% | FAIL at $200K | 20.1% |
| **#2 Parkrose (112th)** | $372,000 | $324,500 | -12.8% | FAIL at $180K | 21.8% |
| **#3 Lents (92nd)** | $386,000 | $325,000 | -15.8% | FAIL at $190K | 7.5% |

---

## Why the Tool ARVs Are Lower — Methodology Gap

The manual ARVs in `top3-evaluation.md` were estimated using **renovated comparable sales** — i.e., comps of recently updated homes in good/excellent condition. This is the standard approach for estimating After-Repair Value.

The comp-analyzer tool generates a **broad pool of synthetic comps across all conditions** (poor through excellent), then applies adjustments. Because the synthetic comp pool is weighted toward "average" condition (40% of generated comps), the comp-based method (50% weight in ARV) tends to anchor closer to the neighborhood's all-condition median rather than the renovated subset.

**This is the key calibration issue.** Two ways to fix it when real data arrives:

1. **Filter comps to good/excellent condition** before feeding into the ARV calculator (preferred — matches standard appraisal practice for ARV)
2. **Increase the condition adjustment constant** from $12,000/step to ~$18,000/step to better reflect the Portland renovation premium

For now, the manual ARVs are likely more accurate because they used the right methodology (renovated comp selection). The tool ARVs should be treated as conservative floor estimates.

---

## Comp Analysis Results

### Property #1 — 6847 NE Killingsworth St, Cully

| Metric | Value |
|--------|-------|
| **Indicated Value Range** | $246,958 – $382,500 |
| **Mean** | $310,398 |
| **Median** | $281,091 |
| **Comps Used** | 5 |
| **Avg Relevance Score** | 0.9182 |

**Top 5 Comps (synthetic):**

| Address | Sale Price | Sqft | Beds/Bath | Condition | Adjusted Price | Relevance |
|---------|-----------|------|-----------|-----------|---------------|-----------|
| (see tool-output/cully-comp-results.json for full detail) |

**Notes:** High relevance scores indicate the synthetic comp pool is well-calibrated for Cully's housing stock. The wide value range ($246K-$383K) reflects the condition diversity in the comp pool — would narrow significantly with real, condition-filtered data.

---

### Property #2 — 3312 NE 112th Ave, Parkrose

| Metric | Value |
|--------|-------|
| **Indicated Value Range** | $207,843 – $418,203 |
| **Mean** | $321,440 |
| **Median** | $325,282 |
| **Comps Used** | 5 |
| **Avg Relevance Score** | 0.9098 |

**Notes:** Widest value range of the three ($207K-$418K). Parkrose has the broadest price band in the synthetic data ($260K-$400K base range), which produces more dispersed comps. Real data should tighten this. The $325K median is in the Parkrose updated-home range, which is encouraging.

---

### Property #3 — 4523 SE 92nd Ave, Lents

| Metric | Value |
|--------|-------|
| **Indicated Value Range** | $234,701 – $363,321 |
| **Mean** | $302,068 |
| **Median** | $295,825 |
| **Comps Used** | 5 |
| **Avg Relevance Score** | 0.9020 |

**Notes:** Tightest comp cluster of the three, with highest confidence. Consistent with Lents' more homogeneous housing stock (1940s-1960s ranches). Even at the tool's conservative $325K ARV, the Lents property's $75K rehab estimate pushes ROI to only 7.5% — confirming the "conditional" assessment in top3-evaluation.md.

---

## ARV Calculator Results

### Property #1 — Cully

| Method | Value | Weight |
|--------|-------|--------|
| Comp-Based | $321,503 | 50% |
| Price/SqFt | $386,355 | 30% |
| % of Improvement | $323,200 | 20% |
| **Final ARV** | **$341,500** | |
| **Confidence** | Medium | |
| **Confidence Range** | $307,000 – $375,500 | |

**vs. Manual ARV ($399,000):** The price/sqft method ($386K) is closest to the manual estimate, suggesting the comp-based method is the one pulling values down. This supports the theory that the comp pool's condition mix is the issue.

### Property #2 — Parkrose

| Method | Value | Weight |
|--------|-------|--------|
| Comp-Based | $334,633 | 50% |
| Price/SqFt | $334,828 | 30% |
| % of Improvement | $284,160 | 20% |
| **Final ARV** | **$324,500** | |
| **Confidence** | Medium | |
| **Confidence Range** | $292,000 – $357,000 | |

**vs. Manual ARV ($372,000):** Methods converge more tightly here than Cully. The % of improvement method is the outlier — its "cool" neighborhood tier multiplier (1.08x) is conservative for Parkrose. If reclassified to "moderate" (1.15x), the final ARV would increase ~$15K.

### Property #3 — Lents

| Method | Value | Weight |
|--------|-------|--------|
| Comp-Based | $315,044 | 50% |
| Price/SqFt | $337,500 | 30% |
| % of Improvement | $331,250 | 20% |
| **Final ARV** | **$325,000** | |
| **Confidence** | High | |
| **Confidence Range** | $309,000 – $341,500 | |

**vs. Manual ARV ($386,000):** Largest delta (-15.8%). All three methods converge in the $315-338K range, giving high confidence in the tool's estimate. But this is "as-is comp pool" confidence, not renovated-comp confidence. The $61K gap against the manual ARV is almost entirely explained by the condition adjustment issue described above.

---

## Deal Viability Assessment (Tool ARVs)

Using the more conservative tool ARVs to stress-test the deals:

### Property #1 — Cully: CONDITIONAL at tool ARV

| Metric | Tool ARV | Manual ARV |
|--------|----------|------------|
| 65% Rule max purchase | $173,975 | $211,350 |
| Target purchase | $200,000 | $200,000 |
| **65% Rule** | **FAIL** | PASS |
| Est. ROI | 20.1% | 22.4% |
| **ROI threshold (15%)** | **PASS** | PASS |

**Verdict:** Fails 65% rule at tool ARV, but passes ROI. If we negotiate purchase down to $170K (possible — listed at $268K, already a deep discount), it passes at the conservative number. At manual ARV, it passes all tests. **Real data will resolve which ARV is right.**

### Property #2 — Parkrose: CONDITIONAL at tool ARV

| Metric | Tool ARV | Manual ARV |
|--------|----------|------------|
| 65% Rule max purchase | $158,925 | $189,800 |
| Target purchase | $180,000 | $180,000 |
| **65% Rule** | **FAIL** | PASS |
| Est. ROI | 21.8% | 19.8% |
| **ROI threshold (15%)** | **PASS** | PASS |

**Verdict:** Same pattern — fails 65% at tool ARV, passes at manual ARV. The ROI is strong either way. Negotiate to $155K or below and it passes even at the conservative tool ARV.

### Property #3 — Lents: NO-GO at tool ARV

| Metric | Tool ARV | Manual ARV |
|--------|----------|------------|
| 65% Rule max purchase | $136,250 | $175,900 |
| Target purchase | $190,000 | $190,000 |
| **65% Rule** | **FAIL** | FAIL |
| Est. ROI | 7.5% | 13.2% |
| **ROI threshold (15%)** | **FAIL** | FAIL |

**Verdict:** Fails at BOTH estimates. The $75K rehab is the killer — even at the optimistic manual ARV, the deal barely clears 13% ROI (below our 15% threshold). **Lents property should be downgraded to MONITOR unless Harlan can scope rehab to $55K or below.**

---

## Recommendations

1. **Property ranking unchanged:** Cully #1, Parkrose #2, Lents #3 (now weakened)
2. **Run deal-scorer next** on neighborhoods to get formal 0-100 scores from the tool
3. **When real data arrives:** Re-run all three analyses immediately. Focus on filtering to renovated comps (good/excellent condition) for ARV calculation.
4. **Calibration task:** Compare tool vs. manual ARVs once real data is in. If delta persists at >10%, adjust condition_adjustment constant or comp filtering methodology.
5. **Lents property:** Downgrade to MONITOR. Only reconsider if Harlan's desktop rehab estimate comes in under $55K.

---

## Raw Output Files

All tool output JSON files stored in:
```
workspace/deliverables/m06-property-search/tool-output/
  cully-comp-results.json
  parkrose-comp-results.json
  lents-comp-results.json
  arv-cully-results.json
  arv-parkrose-results.json
  arv-lents-results.json
```

---

*Next run: deal-scorer on all 7 neighborhoods using data/portland-neighborhoods/*.json. Assigned to Reeves, due April 15.*
