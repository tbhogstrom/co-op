# Deal Scorer

Neighborhood and property scoring tool for the Portland Housing Co-op. Evaluates investment potential of Portland neighborhoods and individual distressed properties using a weighted rubric.

## Requirements

Python 3.9+. No external dependencies (standard library only).

## Files

| File | Purpose |
|---|---|
| `deal_scorer.py` | CLI entry point — scores neighborhoods or properties |
| `scoring_rubric.py` | Weighted criteria definitions and interpolation logic |
| `example_output.json` | Sample input/output for Lents neighborhood and a SE 92nd Ave property |

## Usage

### Score a neighborhood

```bash
python deal_scorer.py --mode neighborhood --input lents_neighborhood.json
```

### Score a property

```bash
python deal_scorer.py --mode property --input 9234_se_92nd.json
```

### Write JSON output

```bash
python deal_scorer.py --mode property --input 9234_se_92nd.json --output scored_result.json
```

### View help

```bash
python deal_scorer.py --help
```

## Input Format

### Neighborhood JSON

```json
{
  "name": "Lents",
  "city": "Portland",
  "state": "OR",
  "zip_codes": ["97266", "97236"],
  "median_home_price_ratio": 0.72,
  "appreciation_3yr_pct": 6.8,
  "days_on_market_avg": 38,
  "distressed_density_pct": 5.2,
  "crime_rate_trend": 1.5,
  "transit_score": 62,
  "school_rating": 4.5,
  "development_pipeline_score": 55,
  "walkability_score": 52
}
```

### Property JSON

```json
{
  "address": "9234 SE 92nd Ave",
  "city": "Portland",
  "state": "OR",
  "zip_code": "97266",
  "neighborhood": "Lents",
  "property_type": "Single Family",
  "year_built": 1948,
  "sqft": 1180,
  "lot_sqft": 5200,
  "bedrooms": 3,
  "bathrooms": 1,
  "purchase_price": 185000,
  "arv": 385000,
  "estimated_rehab_cost": 85000,
  "holding_cost_monthly": 1800,
  "holding_period_months": 5,
  "closing_cost_pct": 8.0,
  "price_arv_spread_pct": 51.9,
  "rehab_cost_arv_pct": 22.1,
  "structural_condition": 55,
  "lot_zoning_upside": 40,
  "comp_volume": 6,
  "title_cleanliness": 85,
  "neighborhood_score": 66.4
}
```

## Scoring Rubric

### Neighborhood Score (0-100)

| Criterion | Weight | Direction |
|---|---|---|
| Median home price vs metro | 0.15 | Lower = better |
| 3-year price appreciation | 0.20 | Higher = better |
| Days on market average | 0.10 | Lower = better |
| Distressed property density | 0.15 | Higher = better |
| Crime rate trend | 0.10 | Improving = better |
| Transit access score | 0.10 | Higher = better |
| School rating | 0.05 | Higher = better |
| Development pipeline | 0.10 | More = better |
| Walkability / amenities | 0.05 | Higher = better |

### Property Score (0-100)

| Criterion | Weight | Direction |
|---|---|---|
| Purchase price vs ARV spread | 0.25 | Higher = better |
| Rehab cost as % of ARV | 0.20 | Lower = better |
| Structural condition | 0.15 | Better = lower risk |
| Lot size & zoning upside | 0.10 | Higher = better |
| Comparable sales volume | 0.10 | More = better |
| Title cleanliness | 0.10 | Cleaner = better |
| Neighborhood score | 0.10 | Higher = better |

### Thresholds

- **Deal Threshold**: Combined score must be >= 65 to pursue
- **Return Threshold**: Projected ROI must be >= 15% to pursue

## Ratings

- **Neighborhood**: STRONG (75+), MODERATE (65-74), MARGINAL (50-64), WEAK (<50)
- **Property**: GO (meets both thresholds), CONDITIONAL (meets one), NO-GO (meets neither)
