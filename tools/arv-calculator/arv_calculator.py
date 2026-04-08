#!/usr/bin/env python3
"""
ARV Calculator — After-Repair Value estimation for Portland Housing Co-op.

Calculates ARV using three independent methods, then produces a weighted
composite estimate with confidence ranges.  Designed to consume comp data
from the companion comp-analyzer tool but works with any JSON that matches
the input schema.

Python 3.9+, no external dependencies.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Constants / Portland-specific defaults
# ---------------------------------------------------------------------------

# Market multipliers by neighborhood tier (percentage-of-improvement method).
# These reflect 2025-2026 Portland rehab ROI observations.
MARKET_MULTIPLIERS: dict[str, float] = {
    "hot":      1.25,   # Inner SE, Alberta Arts, Division, Hawthorne
    "moderate": 1.15,   # Lents, Foster-Powell, Woodstock, St Johns
    "cool":     1.08,   # Outer East, Centennial, Pleasant Valley
}

# Default neighborhood tier when not specified.
DEFAULT_TIER = "moderate"

# Weight allocation across the three methods.
DEFAULT_METHOD_WEIGHTS = {
    "comp_based":               0.50,
    "price_per_sqft":           0.30,
    "percentage_of_improvement": 0.20,
}

# Condition multipliers applied to comps to project post-rehab value.
# Represents the typical discount that a given condition carries relative
# to a fully-renovated property.
CONDITION_DISCOUNTS: dict[str, float] = {
    "excellent": 1.00,
    "good":      0.97,
    "fair":      0.90,
    "poor":      0.80,
    "very_poor": 0.70,
}

# How much comp weight decays per mile of distance from subject.
DISTANCE_DECAY_PER_MILE = 0.15

# How much comp weight decays per year of age difference in sale date.
AGE_DECAY_PER_YEAR = 0.10

# Confidence-range spread as a fraction of the point estimate.
CONFIDENCE_SPREAD = {
    "high":   0.05,   # +/- 5 %
    "medium": 0.10,   # +/- 10 %
    "low":    0.18,   # +/- 18 %
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class SubjectProperty:
    address: str
    neighborhood: str
    sqft: int
    beds: int
    baths: float
    lot_sqft: int
    year_built: int
    condition: str = "poor"
    as_is_value: Optional[float] = None
    neighborhood_tier: str = DEFAULT_TIER
    features: list[str] = field(default_factory=list)


@dataclass
class Comp:
    address: str
    sale_price: float
    sqft: int
    beds: int
    baths: float
    lot_sqft: int
    year_built: int
    condition: str = "good"
    distance_miles: float = 0.5
    days_since_sale: int = 30
    adjusted_price: Optional[float] = None
    adjustments: dict[str, float] = field(default_factory=dict)


@dataclass
class MethodResult:
    name: str
    value: float
    weight: float
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class ARVResult:
    subject_address: str
    methods: list[dict[str, Any]]
    final_arv: float
    confidence_level: str
    confidence_range: dict[str, float]
    rehab_cost: Optional[float]
    estimated_profit_at_65_rule: Optional[float]
    notes: list[str]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _round_price(v: float) -> int:
    """Round to nearest $500 for clean presentation."""
    return int(round(v / 500) * 500)


def _condition_factor(condition: str) -> float:
    return CONDITION_DISCOUNTS.get(condition.lower().replace(" ", "_"), 0.85)


def _comp_weight(comp: Comp) -> float:
    """Compute a 0-1 weight for a comp based on distance and recency."""
    dist_penalty = max(0.0, 1.0 - DISTANCE_DECAY_PER_MILE * comp.distance_miles)
    age_years = comp.days_since_sale / 365.0
    age_penalty = max(0.0, 1.0 - AGE_DECAY_PER_YEAR * age_years)
    return dist_penalty * age_penalty


def _sqft_adjust(comp: Comp, subject: SubjectProperty,
                 ppsf: float) -> float:
    """Dollar adjustment for sqft difference."""
    diff = subject.sqft - comp.sqft
    return diff * ppsf * 0.5  # half-weight — diminishing returns on extra sqft


def _bed_bath_adjust(comp: Comp, subject: SubjectProperty) -> float:
    """Per-bed and per-bath adjustment (post-rehab subject assumed standard)."""
    bed_diff = subject.beds - comp.beds
    bath_diff = subject.baths - comp.baths
    return bed_diff * 8_000 + bath_diff * 12_000


def _lot_adjust(comp: Comp, subject: SubjectProperty) -> float:
    """Lot size adjustment — modest in Portland's urban core."""
    diff = subject.lot_sqft - comp.lot_sqft
    return diff * 3.0  # ~$3/sqft for lot premium


def _condition_adjust(comp: Comp) -> float:
    """
    Adjust comp price *upward* if the comp sold in less-than-renovated
    condition, projecting what it would sell for fully renovated.
    """
    factor = _condition_factor(comp.condition)
    if factor >= 1.0:
        return 0.0
    # Invert: if a "fair" comp sold for $X at 0.90 factor, renovated value
    # is X / 0.90.  Adjustment = X/factor - X = X * (1/factor - 1).
    # But we don't have comp.sale_price here in isolation, so we return a
    # multiplier-based adjustment applied later.  For simplicity we treat
    # condition_adjust as a fraction of sale_price.
    return 0.0  # handled via multiplier in comp_based_arv


def _adjust_comp(comp: Comp, subject: SubjectProperty,
                 neighborhood_ppsf: float) -> Comp:
    """Apply adjustments to a single comp and return a copy."""
    adjustments: dict[str, float] = {}

    adjustments["sqft"] = _sqft_adjust(comp, subject, neighborhood_ppsf)
    adjustments["bed_bath"] = _bed_bath_adjust(comp, subject)
    adjustments["lot"] = _lot_adjust(comp, subject)

    # Condition: project comp to renovated-equivalent price.
    cond_factor = _condition_factor(comp.condition)
    renovated_price = comp.sale_price / cond_factor if cond_factor > 0 else comp.sale_price
    adjustments["condition"] = renovated_price - comp.sale_price

    total_adjustment = sum(adjustments.values())
    adjusted_price = comp.sale_price + total_adjustment

    return Comp(
        address=comp.address,
        sale_price=comp.sale_price,
        sqft=comp.sqft,
        beds=comp.beds,
        baths=comp.baths,
        lot_sqft=comp.lot_sqft,
        year_built=comp.year_built,
        condition=comp.condition,
        distance_miles=comp.distance_miles,
        days_since_sale=comp.days_since_sale,
        adjusted_price=round(adjusted_price, 2),
        adjustments={k: round(v, 2) for k, v in adjustments.items()},
    )


# ---------------------------------------------------------------------------
# Method 1 — Comp-Based ARV
# ---------------------------------------------------------------------------

def comp_based_arv(subject: SubjectProperty, comps: list[Comp],
                   neighborhood_ppsf: float) -> MethodResult:
    """Weighted average of adjusted comparable sales."""
    if not comps:
        return MethodResult(
            name="comp_based",
            value=0.0,
            weight=0.0,
            details={"error": "No comps provided"},
        )

    adjusted_comps = [_adjust_comp(c, subject, neighborhood_ppsf) for c in comps]
    weights = [_comp_weight(c) for c in comps]
    total_weight = sum(weights) or 1.0

    weighted_sum = sum(
        (ac.adjusted_price or 0) * w
        for ac, w in zip(adjusted_comps, weights)
    )
    value = weighted_sum / total_weight

    comp_details = []
    for ac, w in zip(adjusted_comps, weights):
        comp_details.append({
            "address": ac.address,
            "sale_price": ac.sale_price,
            "adjusted_price": ac.adjusted_price,
            "weight": round(w, 3),
            "adjustments": ac.adjustments,
        })

    return MethodResult(
        name="comp_based",
        value=round(value, 2),
        weight=DEFAULT_METHOD_WEIGHTS["comp_based"],
        details={
            "comp_count": len(comps),
            "comps": comp_details,
        },
    )


# ---------------------------------------------------------------------------
# Method 2 — Price-per-Square-Foot ARV
# ---------------------------------------------------------------------------

def price_per_sqft_arv(subject: SubjectProperty,
                       neighborhood_ppsf: float) -> MethodResult:
    """Neighborhood median $/sqft for renovated homes x subject sqft."""
    base_value = neighborhood_ppsf * subject.sqft

    # Lot size adjustment: compare to a "typical" Portland lot (5,000 sqft).
    typical_lot = 5000
    lot_factor = 1.0 + (subject.lot_sqft - typical_lot) / typical_lot * 0.05

    # Feature bonus (garage, ADU potential, corner lot, etc.)
    feature_bonus = 0.0
    feature_notes: dict[str, float] = {}
    for feat in subject.features:
        fl = feat.lower()
        if "garage" in fl:
            bonus = 12_000
        elif "adu" in fl:
            bonus = 25_000
        elif "corner" in fl:
            bonus = 5_000
        elif "basement" in fl and "finish" in fl:
            bonus = 18_000
        elif "basement" in fl:
            bonus = 8_000
        else:
            bonus = 0
        feature_bonus += bonus
        if bonus:
            feature_notes[feat] = bonus

    value = base_value * lot_factor + feature_bonus

    return MethodResult(
        name="price_per_sqft",
        value=round(value, 2),
        weight=DEFAULT_METHOD_WEIGHTS["price_per_sqft"],
        details={
            "neighborhood_median_ppsf": neighborhood_ppsf,
            "subject_sqft": subject.sqft,
            "base_value": round(base_value, 2),
            "lot_factor": round(lot_factor, 4),
            "feature_bonus": feature_bonus,
            "feature_notes": feature_notes,
        },
    )


# ---------------------------------------------------------------------------
# Method 3 — Percentage-of-Improvement ARV
# ---------------------------------------------------------------------------

def percentage_of_improvement_arv(subject: SubjectProperty,
                                  rehab_cost: float) -> MethodResult:
    """as-is value + rehab cost * market multiplier."""
    as_is = subject.as_is_value
    if as_is is None:
        # Estimate as-is from condition factor and a rough baseline.
        # Fallback: we can't compute this without some anchor.
        return MethodResult(
            name="percentage_of_improvement",
            value=0.0,
            weight=0.0,
            details={"error": "as_is_value not provided on subject"},
        )

    tier = subject.neighborhood_tier.lower()
    multiplier = MARKET_MULTIPLIERS.get(tier, MARKET_MULTIPLIERS[DEFAULT_TIER])

    value = as_is + rehab_cost * multiplier

    return MethodResult(
        name="percentage_of_improvement",
        value=round(value, 2),
        weight=DEFAULT_METHOD_WEIGHTS["percentage_of_improvement"],
        details={
            "as_is_value": as_is,
            "rehab_cost": rehab_cost,
            "neighborhood_tier": tier,
            "market_multiplier": multiplier,
            "formula": f"{as_is} + {rehab_cost} * {multiplier}",
        },
    )


# ---------------------------------------------------------------------------
# Confidence assessment
# ---------------------------------------------------------------------------

def _assess_confidence(methods: list[MethodResult],
                       comp_count: int) -> str:
    """Return 'high', 'medium', or 'low'."""
    active = [m for m in methods if m.value > 0]
    if len(active) < 2 or comp_count < 2:
        return "low"

    values = [m.value for m in active]
    mean_v = statistics.mean(values)
    if mean_v == 0:
        return "low"

    cv = statistics.stdev(values) / mean_v if len(values) > 1 else 0
    if comp_count >= 4 and cv < 0.08:
        return "high"
    if comp_count >= 3 and cv < 0.15:
        return "medium"
    return "low"


def _confidence_range(arv: float, confidence: str) -> dict[str, int]:
    spread = CONFIDENCE_SPREAD.get(confidence, 0.15)
    return {
        "low":  _round_price(arv * (1 - spread)),
        "mid":  _round_price(arv),
        "high": _round_price(arv * (1 + spread)),
    }


# ---------------------------------------------------------------------------
# Main calculation
# ---------------------------------------------------------------------------

def calculate_arv(data: dict[str, Any]) -> dict[str, Any]:
    """
    Main entry point.  Accepts a dict matching the input JSON schema and
    returns a full ARV result dict.
    """
    # Parse subject
    s = data["subject"]
    subject = SubjectProperty(
        address=s["address"],
        neighborhood=s.get("neighborhood", "Unknown"),
        sqft=s["sqft"],
        beds=s["beds"],
        baths=s["baths"],
        lot_sqft=s.get("lot_sqft", 5000),
        year_built=s.get("year_built", 1950),
        condition=s.get("condition", "poor"),
        as_is_value=s.get("as_is_value"),
        neighborhood_tier=s.get("neighborhood_tier", DEFAULT_TIER),
        features=s.get("features", []),
    )

    # Parse comps
    comps: list[Comp] = []
    for c in data.get("comps", []):
        comps.append(Comp(
            address=c["address"],
            sale_price=c["sale_price"],
            sqft=c["sqft"],
            beds=c["beds"],
            baths=c["baths"],
            lot_sqft=c.get("lot_sqft", 5000),
            year_built=c.get("year_built", 1950),
            condition=c.get("condition", "good"),
            distance_miles=c.get("distance_miles", 0.5),
            days_since_sale=c.get("days_since_sale", 60),
        ))

    rehab_cost: float = data.get("rehab_cost", 0)
    neighborhood_ppsf: float = data.get("neighborhood_median_ppsf_renovated", 0)

    # If no ppsf provided, try to derive from comps.
    if neighborhood_ppsf == 0 and comps:
        ppsf_values = [c.sale_price / c.sqft for c in comps if c.sqft > 0]
        if ppsf_values:
            # Adjust upward for condition — comps may not all be renovated.
            raw_median = statistics.median(ppsf_values)
            avg_cond_factor = statistics.mean(
                [_condition_factor(c.condition) for c in comps]
            )
            neighborhood_ppsf = round(raw_median / avg_cond_factor, 2)

    # If as_is_value not provided, estimate from condition factor and comps.
    if subject.as_is_value is None and comps and neighborhood_ppsf > 0:
        renovated_est = neighborhood_ppsf * subject.sqft
        subject.as_is_value = round(
            renovated_est * _condition_factor(subject.condition), 2
        )

    notes: list[str] = []

    # --- Run the three methods ---
    m1 = comp_based_arv(subject, comps, neighborhood_ppsf)
    m2 = price_per_sqft_arv(subject, neighborhood_ppsf)

    if rehab_cost > 0:
        m3 = percentage_of_improvement_arv(subject, rehab_cost)
    else:
        m3 = MethodResult(
            name="percentage_of_improvement", value=0.0, weight=0.0,
            details={"error": "rehab_cost not provided"},
        )

    methods = [m1, m2, m3]

    # Re-normalise weights for active methods.
    active = [m for m in methods if m.value > 0]
    total_w = sum(m.weight for m in active) or 1.0
    for m in active:
        m.weight = round(m.weight / total_w, 4)

    # Weighted composite.
    final_arv = sum(m.value * m.weight for m in active) if active else 0.0
    final_arv = round(final_arv, 2)

    confidence = _assess_confidence(methods, len(comps))
    crange = _confidence_range(final_arv, confidence)

    # 65% rule profit estimate (M1 decision: purchase ≤65% ARV).
    profit_65 = None
    if rehab_cost > 0 and final_arv > 0:
        max_offer = final_arv * 0.65 - rehab_cost
        profit_65 = _round_price(max_offer)
        notes.append(
            f"65% rule max offer: ${profit_65:,} "
            f"(ARV ${_round_price(final_arv):,} x 0.65 - "
            f"rehab ${rehab_cost:,.0f})"
        )

    if confidence == "low":
        notes.append(
            "Low confidence — consider gathering more comps or "
            "verifying neighborhood $/sqft data."
        )

    result = ARVResult(
        subject_address=subject.address,
        methods=[asdict(m) for m in methods],
        final_arv=_round_price(final_arv),
        confidence_level=confidence,
        confidence_range=crange,
        rehab_cost=rehab_cost if rehab_cost > 0 else None,
        estimated_profit_at_65_rule=profit_65,
        notes=notes,
    )

    return asdict(result)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "ARV Calculator — estimate After-Repair Value for a Portland "
            "property using comp-based, $/sqft, and improvement-percentage "
            "methods."
        ),
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to input JSON file (subject property + comps).",
    )
    parser.add_argument(
        "--rehab-cost", "-r",
        type=float,
        default=None,
        help=(
            "Estimated rehab cost in dollars.  Overrides rehab_cost in the "
            "input JSON if both are present."
        ),
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Path to write output JSON.  If omitted, prints to stdout.",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    with open(input_path, "r") as f:
        data = json.load(f)

    if args.rehab_cost is not None:
        data["rehab_cost"] = args.rehab_cost

    result = calculate_arv(data)
    output_json = json.dumps(result, indent=2)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as f:
            f.write(output_json + "\n")
        print(f"ARV result written to {out_path}")
    else:
        print(output_json)


if __name__ == "__main__":
    main()
