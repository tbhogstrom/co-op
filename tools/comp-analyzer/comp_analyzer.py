#!/usr/bin/env python3
"""
comp_analyzer.py — Comparable-sales analysis tool for Portland properties.

Generates (or loads) comparable sales for a subject property, applies
standard appraisal-style adjustments, and produces a ranked comp table.

Usage:
    python comp_analyzer.py --input subject.json [--radius 0.5] [--count 5] [--output out.json]
    python comp_analyzer.py --help

Input JSON schema (subject property):
    {
      "address":       "5432 SE 92nd Ave, Portland, OR",
      "neighborhood":  "lents",
      "sqft":          1050,
      "beds":          3,
      "baths":         1.0,
      "year_built":    1952,
      "lot_sqft":      5000,   // optional, default 5000
      "condition":     "fair"  // optional, default "average"
    }

No external dependencies — Python 3.9+ standard library only.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass, asdict
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

from data_sources import (
    CompSale,
    SyntheticMLSGenerator,
    MultnomahAssessor,
    PortlandMapsLookup,
)

# ---------------------------------------------------------------------------
# Adjustment constants
#
# These mirror standard residential appraisal adjustments used in CMA
# (Comparative Market Analysis) reports.  Values are tuned for the Portland
# market as of 2025-2026.
# ---------------------------------------------------------------------------

# Per-sqft adjustment applied to the difference between comp and subject.
SQFT_ADJUSTMENT_PER_SQFT: float = 150.0  # $/sqft difference

# Per-year adjustment for age difference (newer = premium).
AGE_ADJUSTMENT_PER_YEAR: float = 600.0

# Flat adjustments by condition gap (ordinal index difference).
CONDITION_INDEX = {"poor": 0, "fair": 1, "average": 2, "good": 3, "excellent": 4}
CONDITION_ADJUSTMENT_PER_STEP: float = 12_000.0

# Lot-size adjustment per 100 sqft difference.
LOT_ADJUSTMENT_PER_100SQFT: float = 800.0

# Distance penalty — comps farther from subject are less reliable.
# This is used for *relevance scoring* rather than price adjustment.
DISTANCE_PENALTY_PER_MILE: float = 0.15  # 0-1 relevance hit per mile

# Bedroom / bathroom adjustments.
BED_ADJUSTMENT: float = 10_000.0
BATH_ADJUSTMENT: float = 8_000.0

# Time adjustment — appreciation rate per month (Portland trailing avg).
MONTHLY_APPRECIATION: float = 0.003  # ~3.6% annualized


# ---------------------------------------------------------------------------
# Subject property dataclass
# ---------------------------------------------------------------------------

@dataclass
class SubjectProperty:
    address: str
    neighborhood: str
    sqft: int
    beds: int
    baths: float
    year_built: int
    lot_sqft: int = 5000
    condition: str = "average"

    @classmethod
    def from_dict(cls, d: dict) -> "SubjectProperty":
        return cls(
            address=d["address"],
            neighborhood=d["neighborhood"],
            sqft=int(d["sqft"]),
            beds=int(d["beds"]),
            baths=float(d["baths"]),
            year_built=int(d["year_built"]),
            lot_sqft=int(d.get("lot_sqft", 5000)),
            condition=d.get("condition", "average"),
        )


# ---------------------------------------------------------------------------
# Adjustment engine
# ---------------------------------------------------------------------------

@dataclass
class AdjustedComp:
    """A comp with all adjustments calculated."""

    # Original comp fields
    address: str
    sale_date: str
    sale_price: int
    sqft: int
    beds: int
    baths: float
    lot_sqft: int
    year_built: int
    condition: str
    distance_miles: float
    price_per_sqft: float

    # Adjustments (positive = comp was inferior, adds value to reach subject)
    sqft_adjustment: float = 0.0
    age_adjustment: float = 0.0
    condition_adjustment: float = 0.0
    lot_adjustment: float = 0.0
    bed_adjustment: float = 0.0
    bath_adjustment: float = 0.0
    time_adjustment: float = 0.0
    total_adjustment: float = 0.0
    adjusted_price: float = 0.0

    # Relevance score (0-1, higher = more comparable)
    relevance_score: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


def _months_between(d1: date, d2: date) -> float:
    """Approximate months between two dates."""
    return abs((d1 - d2).days) / 30.44


def compute_adjustments(
    subject: SubjectProperty,
    comp: CompSale,
    reference_date: Optional[date] = None,
) -> AdjustedComp:
    """Apply standard CMA adjustments to a single comp relative to subject.

    Adjustment convention: positive adjustment means the comp was *inferior*
    to the subject in that dimension, so we add value to the comp's price to
    estimate what the subject would sell for.
    """
    ref = reference_date or date.today()

    # --- Square footage ---
    sqft_diff = subject.sqft - comp.sqft  # positive if subject is larger
    sqft_adj = sqft_diff * SQFT_ADJUSTMENT_PER_SQFT

    # --- Age / year built ---
    age_diff = comp.year_built - subject.year_built  # positive if comp newer
    age_adj = -age_diff * AGE_ADJUSTMENT_PER_YEAR  # newer comp => subtract

    # --- Condition ---
    subj_idx = CONDITION_INDEX.get(subject.condition.lower(), 2)
    comp_idx = CONDITION_INDEX.get(comp.condition.lower(), 2)
    cond_diff = subj_idx - comp_idx  # positive if subject in better condition
    cond_adj = cond_diff * CONDITION_ADJUSTMENT_PER_STEP

    # --- Lot size ---
    lot_diff = subject.lot_sqft - comp.lot_sqft
    lot_adj = (lot_diff / 100) * LOT_ADJUSTMENT_PER_100SQFT

    # --- Bedrooms / bathrooms ---
    bed_adj = (subject.beds - comp.beds) * BED_ADJUSTMENT
    bath_adj = (subject.baths - comp.baths) * BATH_ADJUSTMENT

    # --- Time (market appreciation since sale) ---
    sale_dt = date.fromisoformat(comp.sale_date)
    months_ago = _months_between(ref, sale_dt)
    time_adj = comp.sale_price * MONTHLY_APPRECIATION * months_ago

    total_adj = sqft_adj + age_adj + cond_adj + lot_adj + bed_adj + bath_adj + time_adj
    adjusted = comp.sale_price + total_adj

    # --- Relevance score ---
    # Composed of distance, sqft similarity, age similarity, recency.
    dist_score = max(0.0, 1.0 - comp.distance_miles * DISTANCE_PENALTY_PER_MILE * 2)
    sqft_score = max(0.0, 1.0 - abs(sqft_diff) / (subject.sqft or 1) * 0.8)
    age_score = max(0.0, 1.0 - abs(age_diff) / 50)
    recency_score = max(0.0, 1.0 - months_ago / 24)
    cond_score = max(0.0, 1.0 - abs(cond_diff) * 0.2)
    bed_score = 1.0 if comp.beds == subject.beds else 0.7
    bath_score = 1.0 if comp.baths == subject.baths else 0.8

    relevance = (
        dist_score * 0.20
        + sqft_score * 0.25
        + age_score * 0.10
        + recency_score * 0.15
        + cond_score * 0.10
        + bed_score * 0.10
        + bath_score * 0.10
    )
    relevance = round(min(1.0, max(0.0, relevance)), 4)

    return AdjustedComp(
        address=comp.address,
        sale_date=comp.sale_date,
        sale_price=comp.sale_price,
        sqft=comp.sqft,
        beds=comp.beds,
        baths=comp.baths,
        lot_sqft=comp.lot_sqft,
        year_built=comp.year_built,
        condition=comp.condition,
        distance_miles=comp.distance_miles,
        price_per_sqft=comp.price_per_sqft,
        sqft_adjustment=round(sqft_adj, 2),
        age_adjustment=round(age_adj, 2),
        condition_adjustment=round(cond_adj, 2),
        lot_adjustment=round(lot_adj, 2),
        bed_adjustment=round(bed_adj, 2),
        bath_adjustment=round(bath_adj, 2),
        time_adjustment=round(time_adj, 2),
        total_adjustment=round(total_adj, 2),
        adjusted_price=round(adjusted, 2),
        relevance_score=relevance,
    )


# ---------------------------------------------------------------------------
# Full analysis pipeline
# ---------------------------------------------------------------------------

def run_analysis(
    subject: SubjectProperty,
    radius_miles: float = 0.5,
    comp_count: int = 5,
    generate_count: int = 20,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    """Run a complete comp analysis for a subject property.

    1. Generate a pool of synthetic comps.
    2. Compute adjustments and relevance for each.
    3. Rank by relevance and return the top *comp_count*.
    4. Calculate summary statistics (indicated value range, mean, median).
    """
    generator = SyntheticMLSGenerator(seed=seed)
    raw_comps = generator.generate_comps(
        neighborhood=subject.neighborhood,
        sqft_target=subject.sqft,
        beds=subject.beds,
        baths=subject.baths,
        radius_miles=radius_miles,
        months_back=12,
        count=generate_count,
    )

    # Adjust each comp
    adjusted: List[AdjustedComp] = [
        compute_adjustments(subject, c) for c in raw_comps
    ]

    # Sort by relevance (descending), take top N
    adjusted.sort(key=lambda a: a.relevance_score, reverse=True)
    top = adjusted[:comp_count]

    # Summary statistics from the top comps
    prices = [c.adjusted_price for c in top]
    mean_price = sum(prices) / len(prices) if prices else 0
    sorted_prices = sorted(prices)
    if len(sorted_prices) % 2 == 1:
        median_price = sorted_prices[len(sorted_prices) // 2]
    else:
        mid = len(sorted_prices) // 2
        median_price = (sorted_prices[mid - 1] + sorted_prices[mid]) / 2

    # Assessor and PortlandMaps lookups
    assessor = MultnomahAssessor().lookup(subject.address)
    portmaps = PortlandMapsLookup().lookup(subject.address)

    result: Dict[str, Any] = {
        "analysis_date": date.today().isoformat(),
        "subject": {
            "address": subject.address,
            "neighborhood": subject.neighborhood,
            "sqft": subject.sqft,
            "beds": subject.beds,
            "baths": subject.baths,
            "year_built": subject.year_built,
            "lot_sqft": subject.lot_sqft,
            "condition": subject.condition,
        },
        "parameters": {
            "radius_miles": radius_miles,
            "comps_requested": comp_count,
            "comps_generated": generate_count,
        },
        "public_records": {
            "assessor": assessor.to_dict(),
            "portland_maps": portmaps.to_dict(),
        },
        "comps": [c.to_dict() for c in top],
        "summary": {
            "indicated_value_low": round(min(prices), 0) if prices else 0,
            "indicated_value_high": round(max(prices), 0) if prices else 0,
            "indicated_value_mean": round(mean_price, 0),
            "indicated_value_median": round(median_price, 0),
            "comp_count": len(top),
            "avg_relevance_score": round(
                sum(c.relevance_score for c in top) / len(top), 4
            ) if top else 0,
        },
    }
    return result


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="comp_analyzer",
        description=(
            "Portland comparable-sales analyzer.  Takes a subject property "
            "description as JSON, generates comparable sales data, applies "
            "standard appraisal adjustments, and produces a ranked comp table."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Example:\n"
            "  python comp_analyzer.py --input subject.json --count 5 --radius 0.5\n"
            "\n"
            "Input JSON format:\n"
            '  {"address": "5432 SE 92nd Ave, Portland, OR",\n'
            '   "neighborhood": "lents", "sqft": 1050, "beds": 3,\n'
            '   "baths": 1.0, "year_built": 1952}\n'
        ),
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to JSON file describing the subject property.",
    )
    parser.add_argument(
        "--radius", "-r",
        type=float,
        default=0.5,
        help="Search radius in miles (default: 0.5).",
    )
    parser.add_argument(
        "--count", "-c",
        type=int,
        default=5,
        help="Number of top comps to return (default: 5).",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Write results to this JSON file (default: stdout).",
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=None,
        help="Random seed for reproducible synthetic data.",
    )
    parser.add_argument(
        "--pool-size",
        type=int,
        default=20,
        help="Size of the initial comp pool before ranking (default: 20).",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Load subject property
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        return 1

    try:
        with open(input_path) as f:
            subject_data = json.load(f)
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON in {input_path}: {exc}", file=sys.stderr)
        return 1

    required = {"address", "neighborhood", "sqft", "beds", "baths", "year_built"}
    missing = required - set(subject_data.keys())
    if missing:
        print(f"Error: missing required fields: {', '.join(sorted(missing))}",
              file=sys.stderr)
        return 1

    subject = SubjectProperty.from_dict(subject_data)

    # Run analysis
    try:
        result = run_analysis(
            subject=subject,
            radius_miles=args.radius,
            comp_count=args.count,
            generate_count=args.pool_size,
            seed=args.seed,
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    # Output
    output_json = json.dumps(result, indent=2)
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as f:
            f.write(output_json + "\n")
        print(f"Results written to {out_path}", file=sys.stderr)
    else:
        print(output_json)

    return 0


if __name__ == "__main__":
    sys.exit(main())
