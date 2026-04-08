# Comp Analyzer

Comparable-sales analysis tool for Portland residential properties. Generates
synthetic MLS-style comparable sales, applies standard appraisal adjustments
(sqft, age, condition, lot size, proximity, time), and produces a ranked comp
table with an indicated value range.

No external dependencies -- Python 3.9+ standard library only.

## Quick Start

```bash
# Create a subject property JSON file
cat > subject.json << 'EOF'
{
  "address": "5432 SE 92nd Ave, Portland, OR",
  "neighborhood": "lents",
  "sqft": 1050,
  "beds": 3,
  "baths": 1.0,
  "year_built": 1952,
  "lot_sqft": 5000,
  "condition": "fair"
}
EOF

# Run analysis (output to stdout)
python comp_analyzer.py --input subject.json

# Run with options
python comp_analyzer.py --input subject.json --count 7 --radius 0.75 --output results.json

# Reproducible output with a fixed seed
python comp_analyzer.py --input subject.json --seed 42 --output results.json
```

## CLI Options

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--input` | `-i` | *required* | Path to subject property JSON file |
| `--radius` | `-r` | `0.5` | Search radius in miles |
| `--count` | `-c` | `5` | Number of top comps to return |
| `--output` | `-o` | stdout | Write results to a JSON file |
| `--seed` | `-s` | random | Random seed for reproducible synthetic data |
| `--pool-size` | | `20` | Initial comp pool size before ranking |

## Input JSON Schema

Required fields:

| Field | Type | Example |
|-------|------|---------|
| `address` | string | `"5432 SE 92nd Ave, Portland, OR"` |
| `neighborhood` | string | `"lents"` |
| `sqft` | int | `1050` |
| `beds` | int | `3` |
| `baths` | float | `1.0` |
| `year_built` | int | `1952` |

Optional fields:

| Field | Type | Default | Example |
|-------|------|---------|---------|
| `lot_sqft` | int | `5000` | `5000` |
| `condition` | string | `"average"` | `"fair"` |

## Supported Neighborhoods

Lents, Cully, Foster-Powell, St. Johns, Woodstock, Montavilla, Parkrose.

Each neighborhood is calibrated with realistic Portland price ranges, lot
sizes, year-built distributions, and street names.

## Output Structure

```
{
  "analysis_date": "2026-04-07",
  "subject": { ... },
  "parameters": { "radius_miles", "comps_requested", "comps_generated" },
  "public_records": {
    "assessor": { ... },      // Multnomah County assessor stub
    "portland_maps": { ... }   // PortlandMaps.com stub
  },
  "comps": [
    {
      "address", "sale_date", "sale_price", "sqft", "beds", "baths",
      "lot_sqft", "year_built", "condition", "distance_miles",
      "price_per_sqft",
      "sqft_adjustment", "age_adjustment", "condition_adjustment",
      "lot_adjustment", "bed_adjustment", "bath_adjustment",
      "time_adjustment", "total_adjustment", "adjusted_price",
      "relevance_score"
    },
    ...
  ],
  "summary": {
    "indicated_value_low", "indicated_value_high",
    "indicated_value_mean", "indicated_value_median",
    "comp_count", "avg_relevance_score"
  }
}
```

## Adjustment Methodology

Adjustments follow standard CMA (Comparative Market Analysis) conventions:

- **Square footage**: $150/sqft difference
- **Age**: $600/year difference in year built
- **Condition**: $12,000 per ordinal step (poor/fair/average/good/excellent)
- **Lot size**: $800 per 100 sqft difference
- **Bedrooms**: $10,000 per bedroom difference
- **Bathrooms**: $8,000 per bathroom difference
- **Time**: 0.3%/month market appreciation applied to sale price

Positive adjustment = comp was inferior to subject in that dimension.

Relevance scoring weights: sqft similarity (25%), distance (20%), recency
(15%), age similarity (10%), condition match (10%), bed match (10%), bath
match (10%).

## Data Sources

- **Synthetic MLS**: `SyntheticMLSGenerator` in `data_sources.py` generates
  realistic comp records calibrated to Portland neighborhoods.
- **Multnomah County Assessor**: `MultnomahAssessor` stub returns deterministic
  tax/assessment records. Production version would query the county CAMA
  database.
- **PortlandMaps.com**: `PortlandMapsLookup` stub returns zoning, permit, and
  lien data. Production version would use the PortlandMaps REST API.

## Files

```
comp-analyzer/
  comp_analyzer.py     # CLI tool and adjustment engine
  data_sources.py      # Data fetching: synthetic MLS + real-data stubs
  example_output.json  # Example output for a Lents 3BR/1BA ranch
  README.md            # This file
```
