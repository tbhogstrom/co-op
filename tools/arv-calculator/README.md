# ARV Calculator

Estimates the After-Repair Value (ARV) for distressed Portland properties using three independent methods, then produces a weighted composite with confidence ranges.

## Methods

1. **Comp-Based ARV** (50% weight) — Weighted average of adjusted comparable sales. Closer, more recent comps carry more weight. Each comp is adjusted for sqft, bed/bath count, lot size, and condition to project a renovated-equivalent price.

2. **Price-per-Square-Foot ARV** (30% weight) — Neighborhood median $/sqft for renovated homes multiplied by subject sqft, with adjustments for lot size and property features (garage, basement, ADU potential).

3. **Percentage-of-Improvement ARV** (20% weight) — As-is value plus rehab cost times a market multiplier (1.08-1.25 depending on neighborhood tier: hot, moderate, cool).

The final ARV is the weighted average of all active methods, reported with a confidence range (low/mid/high) and confidence level (high/medium/low) based on comp count and inter-method variance.

## Requirements

Python 3.9+. No external dependencies.

## Usage

```bash
python arv_calculator.py --input property_data.json
python arv_calculator.py --input property_data.json --rehab-cost 75000
python arv_calculator.py --input property_data.json --output result.json
```

### CLI Flags

| Flag | Description |
|------|-------------|
| `--input`, `-i` | Path to input JSON file (required) |
| `--rehab-cost`, `-r` | Rehab cost in dollars (overrides value in input JSON) |
| `--output`, `-o` | Path to write output JSON (prints to stdout if omitted) |

## Input JSON Format

```json
{
  "subject": {
    "address": "7824 SE Woodstock Blvd, Portland, OR 97206",
    "neighborhood": "Lents",
    "sqft": 1050,
    "beds": 3,
    "baths": 1,
    "lot_sqft": 5000,
    "year_built": 1952,
    "condition": "poor",
    "as_is_value": 245000,
    "neighborhood_tier": "moderate",
    "features": ["unfinished basement"]
  },
  "comps": [
    {
      "address": "8012 SE Reedway St, Portland, OR 97206",
      "sale_price": 385000,
      "sqft": 1120,
      "beds": 3,
      "baths": 1,
      "lot_sqft": 4800,
      "year_built": 1948,
      "condition": "good",
      "distance_miles": 0.3,
      "days_since_sale": 45
    }
  ],
  "rehab_cost": 75000,
  "neighborhood_median_ppsf_renovated": 310
}
```

### Subject Fields

| Field | Required | Description |
|-------|----------|-------------|
| `address` | yes | Property address |
| `neighborhood` | no | Neighborhood name |
| `sqft` | yes | Living area square footage |
| `beds` | yes | Bedroom count |
| `baths` | yes | Bathroom count (supports 1.5, 2.5, etc.) |
| `lot_sqft` | no | Lot size in sqft (default: 5000) |
| `year_built` | no | Year built |
| `condition` | no | Current condition: excellent/good/fair/poor/very_poor |
| `as_is_value` | no | Current market value as-is (estimated from comps if omitted) |
| `neighborhood_tier` | no | hot/moderate/cool — affects improvement multiplier |
| `features` | no | List of features: "garage", "basement", "adu", "corner", etc. |

### Comp Fields

| Field | Required | Description |
|-------|----------|-------------|
| `address` | yes | Comp address |
| `sale_price` | yes | Sale price |
| `sqft` | yes | Square footage |
| `beds` | yes | Bedrooms |
| `baths` | yes | Bathrooms |
| `lot_sqft` | no | Lot size (default: 5000) |
| `condition` | no | Condition at time of sale |
| `distance_miles` | no | Distance from subject (default: 0.5) |
| `days_since_sale` | no | Days since sale closed (default: 60) |

## Example

See `example_output.json` for full output from a Lents 1952 ranch (1050 sqft, 3BR/1BA, $75K rehab). The tool produced:

- **Comp-Based ARV**: $380,852 (5 comps, weighted by proximity and recency)
- **Price-per-Sqft ARV**: $343,500 (310 $/sqft median, $18K basement bonus)
- **Improvement ARV**: $331,250 ($245K as-is + $75K rehab at 1.15x multiplier)
- **Final Weighted ARV**: $359,500
- **Confidence**: High (range: $341,500 - $377,500)
- **70% Rule Max Offer**: $177,000

## Integration

Designed to consume comp data from the companion `comp-analyzer` tool. The comps array in the input JSON matches the comp-analyzer output format.
