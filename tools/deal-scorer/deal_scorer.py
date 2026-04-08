#!/usr/bin/env python3
"""
deal_scorer.py — CLI tool for scoring Portland neighborhoods and distressed properties.

Part of the Portland Housing Co-op analysis toolkit. Uses the weighted scoring
rubric defined in scoring_rubric.py to evaluate:

  1. Neighborhoods: rates investment potential based on market dynamics, trend
     data, infrastructure, and livability factors.
  2. Properties: rates individual distressed properties as deal candidates based
     on financials, condition, and market confidence.

Usage:
    python deal_scorer.py --mode neighborhood --input data.json [--output result.json]
    python deal_scorer.py --mode property --input data.json [--output result.json]

Input JSON schemas are documented in the README and example_output.json.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import rubric from the same directory
sys.path.insert(0, str(Path(__file__).parent))
from scoring_rubric import (
    DEAL_THRESHOLD,
    NEIGHBORHOOD_CRITERIA,
    PROPERTY_CRITERIA,
    RETURN_THRESHOLD,
    interpolate_score,
)


# ---------------------------------------------------------------------------
# Metro baseline for ratio calculations (Portland metro Q1 2026)
# ---------------------------------------------------------------------------
METRO_MEDIAN_HOME_PRICE: float = 485000.0


# ---------------------------------------------------------------------------
# Data Normalization
# ---------------------------------------------------------------------------


def normalize_neighborhood_data(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map a neighborhood JSON file (nested structure from data/portland-neighborhoods/)
    into the flat key format expected by the scoring rubric.

    The neighborhood files have a nested structure:
        market_data.median_home_price, characteristics.walkability_score, etc.
    The rubric expects flat keys:
        median_home_price_ratio, walkability_score, etc.

    This function bridges the two schemas.
    """
    result: Dict[str, Any] = {}

    # Preserve metadata fields
    for key in ("name", "city", "state", "zip_codes", "quadrant"):
        if key in raw:
            result[key] = raw[key]

    md = raw.get("market_data", {})
    ch = raw.get("characteristics", {})

    # 1. median_home_price_ratio: neighborhood / metro
    if "median_home_price" in md:
        result["median_home_price_ratio"] = md["median_home_price"] / METRO_MEDIAN_HOME_PRICE

    # 2. appreciation_3yr_pct
    if "price_change_3yr_pct" in md:
        result["appreciation_3yr_pct"] = md["price_change_3yr_pct"]

    # 3. days_on_market_avg
    if "avg_days_on_market" in md:
        result["days_on_market_avg"] = md["avg_days_on_market"]

    # 4. distressed_density_pct
    if "distressed_listing_pct" in md:
        result["distressed_density_pct"] = md["distressed_listing_pct"]

    # 5. crime_rate_trend — parse from text description
    #    Expect strings like "Improving — down 8% YoY" -> +8
    #    or "Stable" -> 0, "Worsening — up 5% YoY" -> -5
    crime_text = ch.get("crime_trend", "")
    result["crime_rate_trend"] = _parse_crime_trend(crime_text)

    # 6. transit_score — derive from transit_access text
    #    MAX light rail access = 70-80, bus only = 40-60, poor = 20-30
    transit_text = ch.get("transit_access", "")
    result["transit_score"] = _parse_transit_score(transit_text)

    # 7. school_rating — direct from characteristics
    if "school_rating_avg" in ch:
        result["school_rating"] = ch["school_rating_avg"]

    # 8. development_pipeline_score — derive from text
    pipeline_text = ch.get("development_pipeline", "")
    result["development_pipeline_score"] = _parse_pipeline_score(pipeline_text)

    # 9. walkability_score — direct from characteristics
    if "walkability_score" in ch:
        result["walkability_score"] = ch["walkability_score"]

    return result


def _parse_crime_trend(text: str) -> float:
    """Parse crime trend text into a numeric score (-10 to +10).
    Positive = improving (crime decreasing). Negative = worsening."""
    text_lower = text.lower()
    if not text_lower:
        return 0.0

    # Try to extract a percentage
    import re
    pct_match = re.search(r'(\d+(?:\.\d+)?)\s*%', text_lower)
    pct_val = float(pct_match.group(1)) if pct_match else 5.0

    if "improving" in text_lower or "down" in text_lower or "decreasing" in text_lower:
        return min(pct_val, 10.0)
    elif "worsening" in text_lower or "up" in text_lower or "increasing" in text_lower:
        return -min(pct_val, 10.0)
    elif "stable" in text_lower:
        if "slight" in text_lower and "improv" in text_lower:
            return 2.0
        return 0.0
    return 0.0


def _parse_transit_score(text: str) -> float:
    """Parse transit access text into a 0-100 score."""
    text_lower = text.lower()
    if not text_lower:
        return 30.0

    score = 30.0  # baseline

    # MAX light rail access is a big bonus
    if "max" in text_lower:
        score += 30.0
    # Frequent bus service
    if "frequent" in text_lower:
        score += 15.0
    elif "bus" in text_lower:
        score += 10.0
    # Quality descriptors
    if "good" in text_lower or "strong" in text_lower:
        score += 10.0
    elif "limited" in text_lower or "poor" in text_lower:
        score -= 10.0
    elif "moderate" in text_lower:
        score += 5.0
    # Nearby but not direct
    if "nearby" in text_lower or "near" in text_lower:
        score += 5.0

    return min(max(score, 0.0), 100.0)


def _parse_pipeline_score(text: str) -> float:
    """Parse development pipeline text into a 0-100 score."""
    text_lower = text.lower()
    if not text_lower:
        return 30.0

    score = 30.0  # baseline

    # Count indicators of development activity
    indicators = [
        "redevelopment", "mixed-use", "new construction", "investment",
        "improvement", "initiative", "corridor", "transit", "parks",
        "commercial", "infill", "housing", "renovation", "revitalization"
    ]
    matches = sum(1 for ind in indicators if ind in text_lower)
    score += matches * 8.0

    # Cap at 100
    return min(score, 100.0)


# ---------------------------------------------------------------------------
# Scoring Engine
# ---------------------------------------------------------------------------


def score_neighborhood(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Score a neighborhood using the neighborhood rubric.

    Args:
        data: Dictionary with keys matching NEIGHBORHOOD_CRITERIA[*]["key"],
              plus metadata fields (name, zip_code, etc.)

    Returns:
        Scored result dict with overall score, breakdown, and recommendation.
    """
    breakdown: List[Dict[str, Any]] = []
    total_score: float = 0.0
    missing_criteria: List[str] = []

    for criterion in NEIGHBORHOOD_CRITERIA:
        key = criterion["key"]
        raw_value = data.get(key)

        if raw_value is None:
            missing_criteria.append(key)
            breakdown.append({
                "criterion": criterion["name"],
                "key": key,
                "weight": criterion["weight"],
                "raw_value": None,
                "criterion_score": 0.0,
                "weighted_score": 0.0,
                "note": "MISSING — scored as 0",
            })
            continue

        raw_value = float(raw_value)
        criterion_score = interpolate_score(raw_value, criterion["bands"])
        weighted_score = criterion_score * criterion["weight"]
        total_score += weighted_score

        breakdown.append({
            "criterion": criterion["name"],
            "key": key,
            "weight": criterion["weight"],
            "raw_value": raw_value,
            "criterion_score": round(criterion_score, 1),
            "weighted_score": round(weighted_score, 2),
        })

    # Build the recommendation
    total_score = round(total_score, 1)
    if total_score >= 75:
        rating = "STRONG"
        recommendation = "High-priority target neighborhood. Active deal sourcing recommended."
    elif total_score >= DEAL_THRESHOLD:
        rating = "MODERATE"
        recommendation = "Viable neighborhood. Selective deal sourcing — only pursue strong individual properties."
    elif total_score >= 50:
        rating = "MARGINAL"
        recommendation = "Below threshold. Monitor for improvement but do not actively source deals."
    else:
        rating = "WEAK"
        recommendation = "Not recommended for investment at this time."

    result = {
        "type": "neighborhood_score",
        "timestamp": datetime.now().isoformat(),
        "neighborhood": {
            "name": data.get("name", "Unknown"),
            "city": data.get("city", "Portland"),
            "state": data.get("state", "OR"),
            "zip_codes": data.get("zip_codes", []),
        },
        "overall_score": total_score,
        "rating": rating,
        "recommendation": recommendation,
        "deal_threshold": DEAL_THRESHOLD,
        "breakdown": breakdown,
    }

    if missing_criteria:
        result["warnings"] = [
            f"Missing data for: {', '.join(missing_criteria)}. "
            "Scores for missing criteria default to 0."
        ]

    return result


def score_property(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Score an individual property using the property rubric.

    Args:
        data: Dictionary with keys matching PROPERTY_CRITERIA[*]["key"],
              plus metadata fields (address, purchase_price, arv, etc.)

    Returns:
        Scored result dict with overall score, financials, breakdown,
        and go/no-go recommendation.
    """
    breakdown: List[Dict[str, Any]] = []
    total_score: float = 0.0
    missing_criteria: List[str] = []

    for criterion in PROPERTY_CRITERIA:
        key = criterion["key"]
        raw_value = data.get(key)

        if raw_value is None:
            missing_criteria.append(key)
            breakdown.append({
                "criterion": criterion["name"],
                "key": key,
                "weight": criterion["weight"],
                "raw_value": None,
                "criterion_score": 0.0,
                "weighted_score": 0.0,
                "note": "MISSING — scored as 0",
            })
            continue

        raw_value = float(raw_value)
        criterion_score = interpolate_score(raw_value, criterion["bands"])
        weighted_score = criterion_score * criterion["weight"]
        total_score += weighted_score

        breakdown.append({
            "criterion": criterion["name"],
            "key": key,
            "weight": criterion["weight"],
            "raw_value": raw_value,
            "criterion_score": round(criterion_score, 1),
            "weighted_score": round(weighted_score, 2),
        })

    total_score = round(total_score, 1)

    # Calculate projected financials if data is available
    financials = _compute_financials(data)

    # Determine go/no-go
    projected_roi = financials.get("projected_roi_pct")
    meets_score = total_score >= DEAL_THRESHOLD
    meets_return = projected_roi is not None and projected_roi >= RETURN_THRESHOLD

    if meets_score and meets_return:
        rating = "GO"
        recommendation = (
            f"Deal meets both thresholds (score {total_score} >= {DEAL_THRESHOLD}, "
            f"ROI {projected_roi:.1f}% >= {RETURN_THRESHOLD}%). Proceed to due diligence."
        )
    elif meets_score and projected_roi is not None:
        rating = "CONDITIONAL"
        recommendation = (
            f"Score passes ({total_score} >= {DEAL_THRESHOLD}) but projected ROI "
            f"({projected_roi:.1f}%) is below {RETURN_THRESHOLD}% threshold. "
            "Re-evaluate rehab scope or negotiate lower purchase price."
        )
    elif meets_return:
        rating = "CONDITIONAL"
        recommendation = (
            f"ROI passes ({projected_roi:.1f}% >= {RETURN_THRESHOLD}%) but score "
            f"({total_score}) is below {DEAL_THRESHOLD} threshold. "
            "Investigate risk factors driving the low score."
        )
    else:
        rating = "NO-GO"
        recommendation = "Does not meet thresholds. Pass on this property."

    result = {
        "type": "property_score",
        "timestamp": datetime.now().isoformat(),
        "property": {
            "address": data.get("address", "Unknown"),
            "city": data.get("city", "Portland"),
            "state": data.get("state", "OR"),
            "zip_code": data.get("zip_code", ""),
            "neighborhood": data.get("neighborhood", ""),
            "property_type": data.get("property_type", ""),
            "year_built": data.get("year_built"),
            "sqft": data.get("sqft"),
            "lot_sqft": data.get("lot_sqft"),
            "bedrooms": data.get("bedrooms"),
            "bathrooms": data.get("bathrooms"),
        },
        "overall_score": total_score,
        "rating": rating,
        "recommendation": recommendation,
        "deal_threshold": DEAL_THRESHOLD,
        "return_threshold": RETURN_THRESHOLD,
        "financials": financials,
        "breakdown": breakdown,
    }

    if missing_criteria:
        result["warnings"] = [
            f"Missing data for: {', '.join(missing_criteria)}. "
            "Scores for missing criteria default to 0."
        ]

    return result


def _compute_financials(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute projected deal financials from property data.

    Expects optional keys: purchase_price, arv, estimated_rehab_cost,
    holding_cost_monthly, holding_period_months, closing_cost_pct.
    """
    purchase_price = data.get("purchase_price")
    arv = data.get("arv")
    rehab_cost = data.get("estimated_rehab_cost")
    holding_monthly = data.get("holding_cost_monthly", 0)
    holding_months = data.get("holding_period_months", 6)
    closing_pct = data.get("closing_cost_pct", 8.0)  # buy + sell closing costs

    financials: Dict[str, Any] = {}

    if purchase_price is not None:
        financials["purchase_price"] = purchase_price
    if arv is not None:
        financials["arv"] = arv
    if rehab_cost is not None:
        financials["estimated_rehab_cost"] = rehab_cost

    if purchase_price is not None and arv is not None:
        spread = arv - purchase_price
        spread_pct = (spread / arv) * 100 if arv > 0 else 0
        financials["spread"] = round(spread)
        financials["spread_pct"] = round(spread_pct, 1)

    if all(v is not None for v in [purchase_price, arv, rehab_cost]):
        holding_total = holding_monthly * holding_months
        closing_total = (purchase_price + arv) * (closing_pct / 100) / 2
        # Simplified: avg of buy-side and sell-side closing
        total_investment = purchase_price + rehab_cost + holding_total + closing_total
        projected_profit = arv - total_investment
        projected_roi = (projected_profit / total_investment) * 100 if total_investment > 0 else 0

        financials["holding_costs"] = round(holding_total)
        financials["estimated_closing_costs"] = round(closing_total)
        financials["total_investment"] = round(total_investment)
        financials["projected_profit"] = round(projected_profit)
        financials["projected_roi_pct"] = round(projected_roi, 1)

    return financials


# ---------------------------------------------------------------------------
# CLI Formatting
# ---------------------------------------------------------------------------


def format_neighborhood_result(result: Dict[str, Any]) -> str:
    """Format a neighborhood scoring result for terminal display."""
    lines: List[str] = []
    n = result["neighborhood"]

    lines.append("=" * 70)
    lines.append(f"  NEIGHBORHOOD SCORE: {n['name']}, {n['city']}, {n['state']}")
    if n.get("zip_codes"):
        lines.append(f"  ZIP Codes: {', '.join(str(z) for z in n['zip_codes'])}")
    lines.append(f"  Scored: {result['timestamp']}")
    lines.append("=" * 70)
    lines.append("")

    # Overall
    score = result["overall_score"]
    bar = _score_bar(score)
    lines.append(f"  OVERALL SCORE:  {score:5.1f} / 100  {bar}  [{result['rating']}]")
    lines.append(f"  Deal Threshold: {result['deal_threshold']}")
    lines.append("")
    lines.append(f"  Recommendation: {result['recommendation']}")
    lines.append("")

    # Breakdown table
    lines.append("  CRITERION BREAKDOWN:")
    lines.append("  " + "-" * 66)
    lines.append(f"  {'Criterion':<35} {'Raw':>8} {'Score':>6} {'Wt':>5} {'Wtd':>6}")
    lines.append("  " + "-" * 66)

    for b in result["breakdown"]:
        raw_str = f"{b['raw_value']}" if b["raw_value"] is not None else "N/A"
        lines.append(
            f"  {b['criterion']:<35} {raw_str:>8} {b['criterion_score']:>6.1f} "
            f"{b['weight']:>5.2f} {b['weighted_score']:>6.2f}"
        )

    lines.append("  " + "-" * 66)
    lines.append("")

    if result.get("warnings"):
        for w in result["warnings"]:
            lines.append(f"  WARNING: {w}")
        lines.append("")

    lines.append("=" * 70)
    return "\n".join(lines)


def format_property_result(result: Dict[str, Any]) -> str:
    """Format a property scoring result for terminal display."""
    lines: List[str] = []
    p = result["property"]

    lines.append("=" * 70)
    lines.append(f"  PROPERTY SCORE: {p['address']}")
    lines.append(f"  {p.get('neighborhood', '')}, {p['city']}, {p['state']} {p.get('zip_code', '')}")
    if p.get("property_type"):
        details = []
        if p.get("property_type"):
            details.append(p["property_type"])
        if p.get("year_built"):
            details.append(f"Built {p['year_built']}")
        if p.get("sqft"):
            details.append(f"{p['sqft']:,} sqft")
        if p.get("bedrooms") and p.get("bathrooms"):
            details.append(f"{p['bedrooms']}bd/{p['bathrooms']}ba")
        if p.get("lot_sqft"):
            details.append(f"Lot: {p['lot_sqft']:,} sqft")
        lines.append(f"  {' | '.join(details)}")
    lines.append(f"  Scored: {result['timestamp']}")
    lines.append("=" * 70)
    lines.append("")

    # Overall
    score = result["overall_score"]
    bar = _score_bar(score)
    lines.append(f"  OVERALL SCORE:  {score:5.1f} / 100  {bar}  [{result['rating']}]")
    lines.append(f"  Deal Threshold: {result['deal_threshold']}  |  Return Threshold: {result['return_threshold']}%")
    lines.append("")
    lines.append(f"  Recommendation: {result['recommendation']}")
    lines.append("")

    # Financials
    fin = result.get("financials", {})
    if fin:
        lines.append("  PROJECTED FINANCIALS:")
        lines.append("  " + "-" * 40)
        if "purchase_price" in fin:
            lines.append(f"    Purchase Price:     ${fin['purchase_price']:>12,}")
        if "estimated_rehab_cost" in fin:
            lines.append(f"    Rehab Cost:         ${fin['estimated_rehab_cost']:>12,}")
        if "holding_costs" in fin:
            lines.append(f"    Holding Costs:      ${fin['holding_costs']:>12,}")
        if "estimated_closing_costs" in fin:
            lines.append(f"    Closing Costs:      ${fin['estimated_closing_costs']:>12,}")
        if "total_investment" in fin:
            lines.append(f"    Total Investment:   ${fin['total_investment']:>12,}")
        lines.append("  " + "-" * 40)
        if "arv" in fin:
            lines.append(f"    ARV (After Repair): ${fin['arv']:>12,}")
        if "projected_profit" in fin:
            lines.append(f"    Projected Profit:   ${fin['projected_profit']:>12,}")
        if "projected_roi_pct" in fin:
            lines.append(f"    Projected ROI:      {fin['projected_roi_pct']:>12.1f}%")
        lines.append("")

    # Breakdown table
    lines.append("  CRITERION BREAKDOWN:")
    lines.append("  " + "-" * 66)
    lines.append(f"  {'Criterion':<35} {'Raw':>8} {'Score':>6} {'Wt':>5} {'Wtd':>6}")
    lines.append("  " + "-" * 66)

    for b in result["breakdown"]:
        raw_str = f"{b['raw_value']}" if b["raw_value"] is not None else "N/A"
        lines.append(
            f"  {b['criterion']:<35} {raw_str:>8} {b['criterion_score']:>6.1f} "
            f"{b['weight']:>5.2f} {b['weighted_score']:>6.2f}"
        )

    lines.append("  " + "-" * 66)
    lines.append("")

    if result.get("warnings"):
        for w in result["warnings"]:
            lines.append(f"  WARNING: {w}")
        lines.append("")

    lines.append("=" * 70)
    return "\n".join(lines)


def _score_bar(score: float, width: int = 20) -> str:
    """Generate a simple ASCII progress bar for a 0-100 score."""
    filled = int(round(score / 100 * width))
    return "[" + "#" * filled + "." * (width - filled) + "]"


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="deal_scorer",
        description=(
            "Portland Housing Co-op Deal Scorer — evaluate neighborhoods and "
            "distressed properties for investment potential."
        ),
        epilog=(
            "Examples:\n"
            "  python deal_scorer.py --mode neighborhood --input lents.json\n"
            "  python deal_scorer.py --mode property --input 9200_se_92nd.json --output scored.json\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--mode",
        required=True,
        choices=["neighborhood", "property"],
        help="Scoring mode: 'neighborhood' or 'property'.",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input JSON file with the data to score.",
    )
    parser.add_argument(
        "--output",
        required=False,
        default=None,
        help="Optional path to write the scored result as JSON.",
    )

    args = parser.parse_args()

    # Load input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(input_path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {input_path}: {e}", file=sys.stderr)
        sys.exit(1)

    # Score
    if args.mode == "neighborhood":
        # Normalize nested neighborhood JSON into flat scorer format
        scorer_data = normalize_neighborhood_data(data)
        result = score_neighborhood(scorer_data)
        formatted = format_neighborhood_result(result)
    else:
        result = score_property(data)
        formatted = format_property_result(result)

    # Display formatted output to stdout
    print(formatted)

    # Optionally write JSON
    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\nJSON result written to: {output_path}")


if __name__ == "__main__":
    main()
