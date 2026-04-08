"""Schema normalization, validation, and data merging for the pipeline."""

import re
from datetime import datetime
from typing import Optional

_POOR_KEYWORDS = {"tear-down", "condemned", "uninhabitable", "fire damage", "major structural"}
_FAIR_KEYWORDS = {"as-is", "fixer", "estate sale", "needs work", "handyman", "distressed",
                  "investor special", "tlc", "deferred maintenance"}
_GOOD_KEYWORDS = {"updated", "renovated", "remodeled", "move-in ready", "turnkey"}

VALID_CONDITIONS = {"poor", "fair", "average", "good", "excellent"}


def _parse_price(val: str) -> int:
    cleaned = re.sub(r'[^\d.]', '', str(val))
    return int(float(cleaned)) if cleaned else 0


def _parse_int(val) -> int:
    if isinstance(val, (int, float)):
        return int(val)
    cleaned = re.sub(r'[^\d.]', '', str(val))
    return int(float(cleaned)) if cleaned else 0


def _parse_float(val) -> float:
    if isinstance(val, (int, float)):
        return float(val)
    cleaned = re.sub(r'[^\d.]', '', str(val))
    return float(cleaned) if cleaned else 0.0


def _parse_date(val: str) -> str:
    val = val.strip()
    for fmt in ("%B %d, %Y", "%b %d, %Y", "%B-%d-%Y", "%b-%d-%Y", "%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(val, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return val


def _infer_condition(description: str) -> str:
    if not description:
        return "average"
    lower = description.lower()
    if any(kw in lower for kw in _POOR_KEYWORDS):
        return "poor"
    if any(kw in lower for kw in _FAIR_KEYWORDS):
        return "fair"
    if any(kw in lower for kw in _GOOD_KEYWORDS):
        return "good"
    return "average"


def normalize_redfin_row(row: dict, neighborhood: str) -> dict:
    address_parts = [
        row.get("ADDRESS", ""),
        row.get("CITY", "Portland"),
        row.get("STATE OR PROVINCE", "OR"),
    ]
    address = f"{address_parts[0]}, {address_parts[1]}, {address_parts[2]}"

    description = ""
    for key in ("HOG_DESCRIPTION", "DESCRIPTION", "REMARKS"):
        if key in row and row[key] and not str(row[key]).startswith("http"):
            description = row[key]
            break

    sale_price = _parse_price(row.get("PRICE", row.get("LAST SALE PRICE", "0")))
    sqft = _parse_int(row.get("SQUARE FEET", row.get("SQFT", "0")))
    price_per_sqft = round(sale_price / sqft, 2) if sqft > 0 else 0.0

    return {
        "address": address,
        "sale_date": _parse_date(row.get("SOLD DATE", row.get("LAST SALE DATE", ""))),
        "sale_price": sale_price,
        "sqft": sqft,
        "beds": _parse_int(row.get("BEDS", "0")),
        "baths": _parse_float(row.get("BATHS", "0")),
        "lot_sqft": _parse_int(row.get("LOT SIZE", row.get("LOT SIZE (SQFT)", "0"))),
        "year_built": _parse_int(row.get("YEAR BUILT", "0")),
        "condition": _infer_condition(description),
        "neighborhood": neighborhood,
        "price_per_sqft": price_per_sqft,
    }


def validate_comp_record(record: dict) -> list[str]:
    errors = []
    required = ["address", "sale_date", "sale_price", "sqft", "beds", "baths",
                 "lot_sqft", "year_built", "condition", "neighborhood"]
    for field in required:
        if field not in record:
            errors.append(f"Missing required field: {field}")

    if record.get("sale_price", 0) <= 0:
        errors.append(f"Invalid sale_price: {record.get('sale_price')}")
    if record.get("sqft", 0) <= 0:
        errors.append(f"Invalid sqft: {record.get('sqft')}")
    if record.get("beds", 0) <= 0:
        errors.append(f"Invalid beds: {record.get('beds')}")
    if record.get("baths", 0) <= 0:
        errors.append(f"Invalid baths: {record.get('baths')}")
    if record.get("year_built", 0) < 1800:
        errors.append(f"Invalid year_built: {record.get('year_built')}")

    condition = record.get("condition", "")
    if condition and condition not in VALID_CONDITIONS:
        errors.append(f"Invalid condition: {condition}")

    sale_date = record.get("sale_date", "")
    if sale_date and not re.match(r'^\d{4}-\d{2}-\d{2}$', sale_date):
        errors.append(f"Invalid sale_date format (expected YYYY-MM-DD): {sale_date}")

    return errors


def merge_redfin_assessor(redfin: dict, assessor: dict) -> dict:
    merged = dict(redfin)
    if merged.get("lot_sqft", 0) == 0 and assessor.get("lot_sqft", 0) > 0:
        merged["lot_sqft"] = assessor["lot_sqft"]
    for field in ("assessed_value", "market_value", "zoning", "property_id", "annual_tax"):
        if field in assessor:
            merged[field] = assessor[field]
    return merged
