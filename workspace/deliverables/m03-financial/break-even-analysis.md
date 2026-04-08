# Portland Housing Co-op — Break-Even Analysis

**Author:** Ledger (CFO)
**Date:** 2026-04-08
**Status:** DRAFT — M3 Deliverable
**Interactive version:** `break-even-analysis.py` (run for full sensitivity tables)

---

## 1. Deal-Level Break-Even

**Base deal:** $300K purchase, $75K rehab, 6-month hold, 85% LTV hard money @ 12%

| Metric | Sale Price Required |
|--------|-------------------|
| **Capital return (members get buy-in back)** | ~$420,000 |
| **Break-even (0% profit)** | **$445,000** |
| **10% ROI on $200K equity** | $466,277 |
| **15% ROI on $200K equity (target)** | **$476,915** |
| **20% ROI** | $487,553 |
| **25% ROI** | $498,191 |
| **30% ROI** | $508,830 |

**Translation:** At our standard deal ($300K purchase, $75K rehab), we need to sell for at least **$445K to break even** and **$477K to hit our 15% target**. That means the ARV must be ≥159% of purchase price.

---

## 2. Maximum Purchase Price by ARV (at 15% ROI target)

| ARV | Max Purchase Price | % of ARV |
|-----|-------------------|----------|
| $400,000 | ~$227,000 | 56.8% |
| $425,000 | ~$253,000 | 59.5% |
| $450,000 | ~$278,000 | 61.8% |
| $475,000 | ~$303,000 | 63.8% |
| $500,000 | ~$329,000 | 65.8% |
| $525,000 | ~$354,000 | 67.5% |

**Rule of thumb: Buy at ≤65% of ARV.**

---

## 3. Sensitivity Table: Break-Even Sale Price

Break-even sale price (0% profit) at different purchase × rehab combinations:

| Purchase ↓ / Rehab → | $50,000 | $75,000 | $100,000 |
|----------------------|---------|---------|----------|
| **$200,000** | $318,000 | $345,000 | $371,000 |
| **$250,000** | $381,000 | $408,000 | $435,000 |
| **$300,000** | $418,000 | $445,000 | $472,000 |
| **$350,000** | $456,000 | $483,000 | $510,000 |

*Assumes 85% LTV, 12% rate, 6-month hold, 6% selling commission.*

---

## 4. ROI Sensitivity Matrix

ROI% at purchase $300K for different ARV × rehab combinations:

| Rehab ↓ / ARV → | $425,000 | $450,000 | $475,000 | $500,000 | $525,000 |
|-----------------|----------|----------|----------|----------|----------|
| **$50,000** | 11.2% ⚠ | 24.6% ✓ | 37.9% ✓ | 51.3% ✓ | 64.6% ✓ |
| **$65,000** | 3.4% ⚠ | 16.7% ✓ | 30.1% ✓ | 43.5% ✓ | 56.8% ✓ |
| **$75,000** | -2.2% ✗ | 11.2% ⚠ | 24.6% ✓ | 37.9% ✓ | 51.3% ✓ |
| **$85,000** | -7.8% ✗ | 5.6% ⚠ | 18.9% ✓ | 32.3% ✓ | 45.7% ✓ |
| **$100,000** | -16.2% ✗ | -2.8% ✗ | 10.6% ⚠ | 23.9% ✓ | 37.3% ✓ |

✓ = meets 15% target | ⚠ = positive but below target | ✗ = loss

**Key insight:** At $300K purchase with $75K rehab, we need ARV ≥ $475K. Below that, we don't hit 15%.

---

## 5. Overhead Drag

Annual fixed overhead: **$58,465**

The 10% overhead recovery from each flip reimburses the co-op for operating costs.

| Flips/Year | Overhead per Flip | Min GP to Cover Overhead | Recovery at Conservative GP ($30.7K) |
|-----------|------------------|------------------------|--------------------------------------|
| 1 | $58,465 | $584,650 (impossible) | $3,070 — **$55K shortfall** |
| 2 | $29,233 | $292,325 | $6,140 — **$52K shortfall** |
| 3 | $19,488 | $194,883 | $9,210 — **$49K shortfall** |

**Reality check:** Overhead recovery at 10% of gross profit will NOT cover annual overhead until the co-op is doing 5+ flips/year at significantly higher gross profits. In Year 1, overhead is subsidized by member capital. This is normal for a startup — the co-op is investing in building infrastructure.

**The real overhead break-even:** At moderate GP ($59.8K per flip), 10% recovery = $5,976/flip. Need ~10 flips/year. At aggressive GP ($121K per flip), recovery = $12.1K/flip. Need ~5 flips/year.

---

## 6. Cash Flow Warning

**⚠ CRITICAL FINDING:** With the approved 6-member capitalization of $120,000, the co-op **runs out of cash in month 5-6 of a standard flip** before the sale closes.

```
Month 1 (Acquire):  $120K → $48K   (down payment + acquisition + first month costs)
Month 2 (Rehab):    $48K → $36K
Month 3 (Rehab):    $36K → $21K
Month 4 (Rehab):    $21K → $7K     ⚠ Approaching zero
Month 5 (Rehab):    $7K → -$8K     🚨 SHORTFALL
Month 6 (Rehab):    -$8K → -$20K   🚨 SHORTFALL
Month 7 (Sale):     -$20K → $109K  (sale proceeds arrive)
```

**Options to close the gap:**
1. **Recruit to $200K target** — original plan; need $80K more in member equity
2. **Find a cheaper first deal** — $250K purchase / $50K rehab reduces cash needed
3. **Negotiate better hard money terms** — 90% LTV or 80% rehab coverage
4. **Shorten hold period** — 4 months instead of 6 (aggressive but possible with experienced crew)
5. **Bridge loan or line of credit** — adds cost but closes the gap

**Recommendation:** Do not acquire a property until total member capital is ≥$175K. The $120K from 6 approved members is not sufficient for a $300K/$75K deal.

---

*Run `python3 break-even-analysis.py` for the full interactive version with all sensitivity tables.*

*— Ledger, CFO*
