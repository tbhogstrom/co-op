#!/usr/bin/env python3
"""
scoring_rubric.py — Weighted scoring criteria for the Portland Housing Co-op deal scorer.

Defines two scoring rubrics:
  1. Neighborhood Score (0-100): evaluates a neighborhood's investment potential
  2. Property Score (0-100): evaluates an individual distressed property as a deal

All weights sum to 1.0 within each rubric. Each criterion is scored 0-100 individually,
then multiplied by its weight to produce the weighted contribution. The final score is
the sum of all weighted contributions.
"""

from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------

# Minimum combined score (neighborhood + property average) to pursue a deal.
# A combined score below this means the deal is too risky or the upside is
# insufficient for the co-op's goals.
DEAL_THRESHOLD: float = 65.0

# Minimum projected ROI (%) to pursue. Even a high-scoring deal isn't worth
# it if the projected return doesn't clear this bar after carrying costs.
RETURN_THRESHOLD: float = 15.0

# ---------------------------------------------------------------------------
# Neighborhood Scoring Rubric
# ---------------------------------------------------------------------------

# Each entry: (criterion_key, display_name, weight, direction, description)
#   direction: "lower_better" or "higher_better"
#   This tells the scorer which way to map raw values onto the 0-100 scale.

NEIGHBORHOOD_CRITERIA: List[Dict] = [
    {
        "key": "median_home_price_ratio",
        "name": "Median Home Price vs Metro",
        "weight": 0.15,
        "direction": "lower_better",
        "description": (
            "Ratio of neighborhood median home price to Portland metro median. "
            "Lower ratio = more affordable entry point for the co-op."
        ),
        # Scoring bands: ratio -> score
        # 0.50 or below = 100, 1.20 or above = 0
        "bands": [
            (0.50, 100),
            (0.60, 90),
            (0.70, 80),
            (0.80, 70),
            (0.90, 55),
            (1.00, 40),
            (1.10, 20),
            (1.20, 0),
        ],
    },
    {
        "key": "appreciation_3yr_pct",
        "name": "3-Year Price Appreciation (%)",
        "weight": 0.20,
        "direction": "higher_better",
        "description": (
            "Annualized price appreciation over the past 3 years. "
            "Higher appreciation = better exit environment."
        ),
        "bands": [
            (-5.0, 0),
            (0.0, 20),
            (3.0, 40),
            (5.0, 55),
            (8.0, 70),
            (12.0, 85),
            (15.0, 100),
        ],
    },
    {
        "key": "days_on_market_avg",
        "name": "Average Days on Market",
        "weight": 0.10,
        "direction": "lower_better",
        "description": (
            "Average DOM for comparable listings. "
            "Lower DOM = faster liquidity, less carrying cost risk."
        ),
        "bands": [
            (10, 100),
            (20, 90),
            (30, 75),
            (45, 60),
            (60, 45),
            (90, 25),
            (120, 10),
            (180, 0),
        ],
    },
    {
        "key": "distressed_density_pct",
        "name": "Distressed Property Density (%)",
        "weight": 0.15,
        "direction": "higher_better",
        "description": (
            "Percentage of properties classified as distressed (foreclosure, "
            "pre-foreclosure, code violations, tax delinquent). Higher density = "
            "more deal flow and negotiating leverage."
        ),
        "bands": [
            (0.0, 0),
            (1.0, 15),
            (2.0, 30),
            (4.0, 50),
            (6.0, 70),
            (8.0, 85),
            (10.0, 95),
            (15.0, 100),
        ],
    },
    {
        "key": "crime_rate_trend",
        "name": "Crime Rate Trend",
        "weight": 0.10,
        "direction": "higher_better",
        "description": (
            "Year-over-year change in crime rate, expressed as improvement. "
            "Positive value = crime decreasing = neighborhood improving. "
            "Scale: -10 (worsening fast) to +10 (improving fast)."
        ),
        "bands": [
            (-10, 0),
            (-5, 15),
            (0, 40),
            (3, 60),
            (5, 75),
            (8, 90),
            (10, 100),
        ],
    },
    {
        "key": "transit_score",
        "name": "Transit Access Score",
        "weight": 0.10,
        "direction": "higher_better",
        "description": (
            "Transit accessibility on a 0-100 scale (TriMet coverage, MAX light "
            "rail proximity, bus frequency). Portland-specific."
        ),
        "bands": [
            (0, 0),
            (20, 20),
            (40, 40),
            (60, 60),
            (80, 80),
            (100, 100),
        ],
    },
    {
        "key": "school_rating",
        "name": "School Rating",
        "weight": 0.05,
        "direction": "higher_better",
        "description": (
            "Average school rating (1-10 scale) for the neighborhood. "
            "Higher = better resale appeal to families."
        ),
        "bands": [
            (1, 0),
            (3, 20),
            (5, 45),
            (7, 70),
            (8, 85),
            (10, 100),
        ],
    },
    {
        "key": "development_pipeline_score",
        "name": "Development Pipeline / Investment",
        "weight": 0.10,
        "direction": "higher_better",
        "description": (
            "Score (0-100) reflecting planned or in-progress development: "
            "new construction, commercial investment, infrastructure projects, "
            "zoning changes. More activity = stronger future appreciation."
        ),
        "bands": [
            (0, 0),
            (20, 20),
            (40, 40),
            (60, 60),
            (80, 80),
            (100, 100),
        ],
    },
    {
        "key": "walkability_score",
        "name": "Walkability / Amenities",
        "weight": 0.05,
        "direction": "higher_better",
        "description": (
            "Walk score equivalent (0-100). Proximity to grocery, restaurants, "
            "parks, and daily-need services."
        ),
        "bands": [
            (0, 0),
            (20, 20),
            (40, 40),
            (60, 60),
            (80, 80),
            (100, 100),
        ],
    },
]

# ---------------------------------------------------------------------------
# Property Scoring Rubric
# ---------------------------------------------------------------------------

PROPERTY_CRITERIA: List[Dict] = [
    {
        "key": "price_arv_spread_pct",
        "name": "Purchase Price vs ARV Spread (%)",
        "weight": 0.25,
        "direction": "higher_better",
        "description": (
            "Spread between purchase price and ARV as a percentage of ARV. "
            "E.g., buy at $200k with ARV $400k = 50% spread. "
            "Higher spread = more room for profit."
        ),
        "bands": [
            (0, 0),
            (10, 15),
            (20, 30),
            (30, 50),
            (40, 70),
            (50, 85),
            (60, 95),
            (70, 100),
        ],
    },
    {
        "key": "rehab_cost_arv_pct",
        "name": "Rehab Cost as % of ARV",
        "weight": 0.20,
        "direction": "lower_better",
        "description": (
            "Estimated total rehab cost divided by ARV. Lower = less capital at "
            "risk and higher margin. Target under 25% for a strong deal."
        ),
        "bands": [
            (5, 100),
            (10, 90),
            (15, 80),
            (20, 65),
            (25, 50),
            (30, 35),
            (40, 15),
            (50, 0),
        ],
    },
    {
        "key": "structural_condition",
        "name": "Structural Condition",
        "weight": 0.15,
        "direction": "higher_better",
        "description": (
            "Assessment of structural integrity on 0-100 scale. "
            "100 = solid structure needing only cosmetic work. "
            "0 = major structural issues (foundation, framing, roof failure)."
        ),
        "bands": [
            (0, 0),
            (20, 15),
            (40, 35),
            (60, 55),
            (70, 70),
            (80, 85),
            (90, 95),
            (100, 100),
        ],
    },
    {
        "key": "lot_zoning_upside",
        "name": "Lot Size & Zoning Upside",
        "weight": 0.10,
        "direction": "higher_better",
        "description": (
            "Score (0-100) reflecting potential for ADU, lot split, or zoning "
            "variance. Larger lots in multi-family zones score highest."
        ),
        "bands": [
            (0, 0),
            (20, 20),
            (40, 40),
            (60, 60),
            (80, 80),
            (100, 100),
        ],
    },
    {
        "key": "comp_volume",
        "name": "Comparable Sales Volume",
        "weight": 0.10,
        "direction": "higher_better",
        "description": (
            "Number of relevant comparable sales within 0.5 miles in the last "
            "6 months. More comps = higher confidence in ARV. "
            "Target: 5+ comps for strong confidence."
        ),
        "bands": [
            (0, 0),
            (1, 20),
            (2, 35),
            (3, 50),
            (5, 70),
            (8, 85),
            (12, 95),
            (15, 100),
        ],
    },
    {
        "key": "title_cleanliness",
        "name": "Title Cleanliness",
        "weight": 0.10,
        "direction": "higher_better",
        "description": (
            "Score (0-100) reflecting title status. 100 = clear title. "
            "Deductions for liens, judgments, back taxes, clouded title, "
            "or probate complications."
        ),
        "bands": [
            (0, 0),
            (20, 10),
            (40, 25),
            (60, 50),
            (80, 75),
            (90, 90),
            (100, 100),
        ],
    },
    {
        "key": "neighborhood_score",
        "name": "Neighborhood Score",
        "weight": 0.10,
        "direction": "higher_better",
        "description": (
            "The neighborhood's overall score from the neighborhood rubric. "
            "This ties the property evaluation back to location fundamentals."
        ),
        "bands": [
            (0, 0),
            (20, 20),
            (40, 40),
            (60, 60),
            (80, 80),
            (100, 100),
        ],
    },
]


def interpolate_score(value: float, bands: List[Tuple[float, int]]) -> float:
    """
    Given a raw value and a list of (threshold, score) bands, return an
    interpolated score between 0 and 100.

    Bands must be sorted by threshold in ascending order. Values below the
    first band get the first band's score; values above the last band get
    the last band's score. Values between bands are linearly interpolated.
    """
    if not bands:
        return 0.0

    # Clamp to boundaries
    if value <= bands[0][0]:
        return float(bands[0][1])
    if value >= bands[-1][0]:
        return float(bands[-1][1])

    # Find the two surrounding bands and interpolate
    for i in range(len(bands) - 1):
        lower_val, lower_score = bands[i]
        upper_val, upper_score = bands[i + 1]
        if lower_val <= value <= upper_val:
            # Linear interpolation
            ratio = (value - lower_val) / (upper_val - lower_val)
            return lower_score + ratio * (upper_score - lower_score)

    # Fallback (should not reach here)
    return float(bands[-1][1])


def validate_rubric() -> bool:
    """Validate that all rubric weights sum to 1.0 (within float tolerance)."""
    n_total = sum(c["weight"] for c in NEIGHBORHOOD_CRITERIA)
    p_total = sum(c["weight"] for c in PROPERTY_CRITERIA)

    n_ok = abs(n_total - 1.0) < 0.001
    p_ok = abs(p_total - 1.0) < 0.001

    if not n_ok:
        print(f"WARNING: Neighborhood weights sum to {n_total:.4f}, expected 1.0")
    if not p_ok:
        print(f"WARNING: Property weights sum to {p_total:.4f}, expected 1.0")

    return n_ok and p_ok


if __name__ == "__main__":
    # Quick self-check
    valid = validate_rubric()
    print(f"Rubric validation: {'PASS' if valid else 'FAIL'}")

    print(f"\nDeal threshold (combined score): {DEAL_THRESHOLD}")
    print(f"Return threshold (projected ROI %): {RETURN_THRESHOLD}%")

    print("\n--- Neighborhood Criteria ---")
    for c in NEIGHBORHOOD_CRITERIA:
        print(f"  {c['weight']:.2f}  {c['name']}")

    print("\n--- Property Criteria ---")
    for c in PROPERTY_CRITERIA:
        print(f"  {c['weight']:.2f}  {c['name']}")
