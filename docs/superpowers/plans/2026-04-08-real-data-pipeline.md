# Real Data Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace synthetic data generation with a real data pipeline that fetches, normalizes, and loads actual Portland market data from public sources.

**Architecture:** Modular fetcher/loader package under `tools/data-pipeline/`. Each external source gets its own fetcher module. Three loader classes replace the stubs in `data_sources.py`. A CLI orchestrator runs fetchers in dependency order. Existing analysis tools (`comp_analyzer`, `arv_calculator`, `deal_scorer`) require no changes — they consume the same dataclass interfaces.

**Tech Stack:** Python 3.9+, requests, pandas. Census Bureau Geocoding API (free, no key). Redfin CSV download URLs. Multnomah County bulk data download. PortlandMaps REST API (no auth). Portland Police open data portal.

**Spec:** `docs/superpowers/specs/2026-04-08-real-data-pipeline-design.md`

---

### Task 1: Project scaffold and config

**Files:**
- Create: `tools/data-pipeline/__init__.py`
- Create: `tools/data-pipeline/config.py`
- Create: `tools/data-pipeline/fetchers/__init__.py`
- Create: `tools/data-pipeline/loaders/__init__.py`
- Create: `requirements.txt` (project root)
- Create: `tests/data-pipeline/__init__.py`
- Create: `tests/data-pipeline/test_config.py`

- [ ] **Step 1: Write the failing test for config**

```python
# tests/data-pipeline/test_config.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'data-pipeline'))

from config import NEIGHBORHOODS, DATA_DIR, COMP_SALES_DIR, ASSESSOR_DIR, PORTLANDMAPS_DIR

def test_neighborhoods_has_seven_entries():
    assert len(NEIGHBORHOODS) == 7

def test_each_neighborhood_has_required_fields():
    required = {"name", "slug", "zip_codes", "redfin_region_url_params"}
    for slug, info in NEIGHBORHOODS.items():
        missing = required - set(info.keys())
        assert not missing, f"{slug} missing: {missing}"

def test_data_dirs_are_paths():
    from pathlib import Path
    assert isinstance(DATA_DIR, Path)
    assert isinstance(COMP_SALES_DIR, Path)
    assert isinstance(ASSESSOR_DIR, Path)
    assert isinstance(PORTLANDMAPS_DIR, Path)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd C:/Users/tfalcon/co-op && python -m pytest tests/data-pipeline/test_config.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: Create package structure and config**

```python
# tools/data-pipeline/__init__.py
"""Real data pipeline for Portland Housing Co-op analysis tools."""
```

```python
# tools/data-pipeline/fetchers/__init__.py
"""Data fetchers for external sources."""
```

```python
# tools/data-pipeline/loaders/__init__.py
"""Data loaders replacing synthetic stubs in data_sources.py."""
```

```python
# tools/data-pipeline/config.py
"""Pipeline configuration — neighborhoods, URLs, paths, rate limits."""

from pathlib import Path

# Project root (co-op/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
COMP_SALES_DIR = DATA_DIR / "comp-sales"
ASSESSOR_DIR = DATA_DIR / "assessor"
ASSESSOR_BY_NEIGHBORHOOD_DIR = ASSESSOR_DIR / "multnomah-by-neighborhood"
PORTLANDMAPS_DIR = DATA_DIR / "portlandmaps"
NEIGHBORHOOD_DIR = DATA_DIR / "portland-neighborhoods"
LISTINGS_DIR = DATA_DIR / "property-listings"

# Rate limiting (seconds between requests)
RATE_LIMITS = {
    "redfin": 3.0,
    "portlandmaps": 1.0,
    "census_geocoder": 1.0,
    "portland_police": 1.0,
}

# Comp search parameters
COMP_DATE_RANGE_MONTHS = 12
COMP_PRICE_MIN = 180_000
COMP_PRICE_MAX = 600_000
COMP_SQFT_MIN = 700
COMP_SQFT_MAX = 2_000

# 7 target neighborhoods with Redfin search parameters
NEIGHBORHOODS = {
    "lents": {
        "name": "Lents",
        "slug": "lents",
        "zip_codes": ["97266"],
        "redfin_region_url_params": {
            "region_id": 399,
            "region_type": 2,
            "market": "portland",
        },
    },
    "cully": {
        "name": "Cully",
        "slug": "cully",
        "zip_codes": ["97218", "97213"],
        "redfin_region_url_params": {
            "region_id": 6786,
            "region_type": 2,
            "market": "portland",
        },
    },
    "foster-powell": {
        "name": "Foster-Powell",
        "slug": "foster-powell",
        "zip_codes": ["97206"],
        "redfin_region_url_params": {
            "region_id": 8541,
            "region_type": 2,
            "market": "portland",
        },
    },
    "st-johns": {
        "name": "St. Johns",
        "slug": "st-johns",
        "zip_codes": ["97203"],
        "redfin_region_url_params": {
            "region_id": 1065,
            "region_type": 2,
            "market": "portland",
        },
    },
    "woodstock": {
        "name": "Woodstock",
        "slug": "woodstock",
        "zip_codes": ["97202", "97206"],
        "redfin_region_url_params": {
            "region_id": 1194,
            "region_type": 2,
            "market": "portland",
        },
    },
    "montavilla": {
        "name": "Montavilla",
        "slug": "montavilla",
        "zip_codes": ["97216", "97220"],
        "redfin_region_url_params": {
            "region_id": 8590,
            "region_type": 2,
            "market": "portland",
        },
    },
    "parkrose": {
        "name": "Parkrose",
        "slug": "parkrose",
        "zip_codes": ["97220", "97230"],
        "redfin_region_url_params": {
            "region_id": 8613,
            "region_type": 2,
            "market": "portland",
        },
    },
}

# Redfin CSV download base URL
REDFIN_DOWNLOAD_BASE = "https://www.redfin.com/stingray/api/gis-csv"

# Multnomah County assessor bulk data
ASSESSOR_BULK_URL = "https://www.multco.us/assessment-taxation/data-download"

# PortlandMaps API
PORTLANDMAPS_API_BASE = "https://www.portlandmaps.com/api"

# Census Bureau Geocoding API
CENSUS_GEOCODER_URL = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"

# Portland Police open data
PORTLAND_POLICE_DATA_URL = "https://public.tableau.com/views/PPBOpenData/CrimeData"
```

```
# requirements.txt
requests>=2.31.0
pandas>=2.0.0
```

- [ ] **Step 4: Create test __init__.py and run tests**

```python
# tests/data-pipeline/__init__.py
```

Run: `cd C:/Users/tfalcon/co-op && python -m pytest tests/data-pipeline/test_config.py -v`
Expected: PASS — all 3 tests pass

- [ ] **Step 5: Commit**

```bash
git add tools/data-pipeline/ tests/data-pipeline/ requirements.txt
git commit -m "feat(data-pipeline): scaffold project structure and config"
```

---

### Task 2: Geocoding module

**Files:**
- Create: `tools/data-pipeline/geocoding.py`
- Create: `tests/data-pipeline/test_geocoding.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/data-pipeline/test_geocoding.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'data-pipeline'))

from geocoding import haversine, normalize_address

def test_haversine_known_distance():
    # Portland City Hall to PDX Airport is ~9.5 miles
    portland_hall = (45.5152, -122.6784)
    pdx_airport = (45.5898, -122.5951)
    dist = haversine(*portland_hall, *pdx_airport)
    assert 8.0 < dist < 11.0, f"Expected ~9.5 miles, got {dist}"

def test_haversine_same_point():
    dist = haversine(45.5, -122.6, 45.5, -122.6)
    assert dist == 0.0

def test_haversine_returns_miles():
    # ~69 miles per degree of latitude
    dist = haversine(45.0, -122.0, 46.0, -122.0)
    assert 68.0 < dist < 70.0

def test_normalize_address_strips_unit():
    assert "123 SE MAIN ST" in normalize_address("123 SE Main St, Unit 4, Portland, OR")

def test_normalize_address_expands_abbreviations():
    result = normalize_address("123 se foster rd")
    assert "FOSTER" in result
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd C:/Users/tfalcon/co-op && python -m pytest tests/data-pipeline/test_geocoding.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: Implement geocoding module**

```python
# tools/data-pipeline/geocoding.py
"""Geocoding via Census Bureau API and Haversine distance computation."""

import json
import math
import re
import time
import urllib.request
import urllib.parse
from typing import Optional, Tuple

from config import CENSUS_GEOCODER_URL, RATE_LIMITS

# Earth radius in miles
_EARTH_RADIUS_MI = 3958.8


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return distance in miles between two lat/lon points."""
    if lat1 == lat2 and lon1 == lon2:
        return 0.0
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return round(_EARTH_RADIUS_MI * c, 4)


def normalize_address(address: str) -> str:
    """Normalize an address string for matching: uppercase, strip unit numbers."""
    addr = address.upper().strip()
    # Remove unit/apt/suite numbers
    addr = re.sub(r',?\s*(UNIT|APT|STE|SUITE|#)\s*\S+', '', addr)
    # Remove city/state/zip suffix for matching
    addr = re.sub(r',\s*PORTLAND.*$', '', addr)
    # Collapse whitespace
    addr = re.sub(r'\s+', ' ', addr).strip()
    return addr


def geocode(address: str, city: str = "Portland", state: str = "OR") -> Optional[Tuple[float, float]]:
    """Geocode an address using the Census Bureau Geocoding API.

    Returns (latitude, longitude) or None if geocoding fails.
    Free, no API key required.
    """
    full_address = f"{address}, {city}, {state}"
    params = urllib.parse.urlencode({
        "address": full_address,
        "benchmark": "Public_AR_Current",
        "format": "json",
    })
    url = f"{CENSUS_GEOCODER_URL}?{params}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PortlandCoopDataPipeline/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())

        matches = data.get("result", {}).get("addressMatches", [])
        if not matches:
            return None

        coords = matches[0]["coordinates"]
        return (float(coords["y"]), float(coords["x"]))  # lat, lon
    except Exception:
        return None


def batch_geocode(addresses: list[str], city: str = "Portland", state: str = "OR",
                  delay: float = None) -> dict[str, Optional[Tuple[float, float]]]:
    """Geocode a list of addresses, returning a dict of address -> (lat, lon).

    Rate-limited per config.
    """
    if delay is None:
        delay = RATE_LIMITS.get("census_geocoder", 1.0)
    results = {}
    for i, addr in enumerate(addresses):
        results[addr] = geocode(addr, city, state)
        if i < len(addresses) - 1:
            time.sleep(delay)
    return results
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd C:/Users/tfalcon/co-op && python -m pytest tests/data-pipeline/test_geocoding.py -v`
Expected: PASS — all 5 tests pass

- [ ] **Step 5: Commit**

```bash
git add tools/data-pipeline/geocoding.py tests/data-pipeline/test_geocoding.py
git commit -m "feat(data-pipeline): add geocoding module with Haversine and Census API"
```

---

### Task 3: Normalizer module

**Files:**
- Create: `tools/data-pipeline/normalizer.py`
- Create: `tests/data-pipeline/test_normalizer.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/data-pipeline/test_normalizer.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'data-pipeline'))

from normalizer import normalize_redfin_row, validate_comp_record, merge_redfin_assessor

def test_normalize_redfin_row_maps_fields():
    row = {
        "ADDRESS": "123 SE Foster Rd",
        "CITY": "Portland",
        "STATE OR PROVINCE": "OR",
        "SOLD DATE": "April 5, 2026",
        "PRICE": "$385,000",
        "SQUARE FEET": "1,200",
        "BEDS": "3",
        "BATHS": "1.5",
        "LOT SIZE": "5,000",
        "YEAR BUILT": "1952",
        "URL (SEE https://www.redfin.com/buy-a-home/comparative-market-analysis FOR INFO ON PRICING)": "https://redfin.com/...",
    }
    comp = normalize_redfin_row(row, "lents")
    assert comp["address"] == "123 SE Foster Rd, Portland, OR"
    assert comp["sale_date"] == "2026-04-05"
    assert comp["sale_price"] == 385000
    assert comp["sqft"] == 1200
    assert comp["beds"] == 3
    assert comp["baths"] == 1.5
    assert comp["lot_sqft"] == 5000
    assert comp["year_built"] == 1952
    assert comp["condition"] == "average"
    assert comp["neighborhood"] == "lents"

def test_normalize_redfin_row_condition_heuristic():
    row = {
        "ADDRESS": "456 NE Cully Blvd",
        "CITY": "Portland",
        "STATE OR PROVINCE": "OR",
        "SOLD DATE": "March 1, 2026",
        "PRICE": "$200,000",
        "SQUARE FEET": "1,000",
        "BEDS": "2",
        "BATHS": "1",
        "LOT SIZE": "4,500",
        "YEAR BUILT": "1945",
        "URL (SEE https://www.redfin.com/buy-a-home/comparative-market-analysis FOR INFO ON PRICING)": "",
        "HOG_DESCRIPTION": "Estate sale, sold as-is, needs work",
    }
    comp = normalize_redfin_row(row, "cully")
    assert comp["condition"] in ("fair", "poor")

def test_validate_comp_record_passes_good_record():
    record = {
        "address": "123 SE Foster Rd, Portland, OR",
        "sale_date": "2026-04-05",
        "sale_price": 385000,
        "sqft": 1200,
        "beds": 3,
        "baths": 1.5,
        "lot_sqft": 5000,
        "year_built": 1952,
        "condition": "average",
        "neighborhood": "lents",
    }
    errors = validate_comp_record(record)
    assert errors == []

def test_validate_comp_record_catches_bad_price():
    record = {
        "address": "123 SE Foster Rd, Portland, OR",
        "sale_date": "2026-04-05",
        "sale_price": -100,
        "sqft": 1200,
        "beds": 3,
        "baths": 1.5,
        "lot_sqft": 5000,
        "year_built": 1952,
        "condition": "average",
        "neighborhood": "lents",
    }
    errors = validate_comp_record(record)
    assert len(errors) > 0

def test_merge_redfin_assessor():
    redfin = {
        "address": "123 SE Foster Rd, Portland, OR",
        "sale_price": 385000,
        "sqft": 1200,
        "beds": 3,
        "baths": 1.5,
        "lot_sqft": 0,
        "year_built": 1952,
    }
    assessor = {
        "address": "123 SE FOSTER RD",
        "lot_sqft": 5200,
        "year_built": 1951,
        "assessed_value": 320000,
        "zoning": "R5",
    }
    merged = merge_redfin_assessor(redfin, assessor)
    assert merged["lot_sqft"] == 5200  # assessor fills gap
    assert merged["year_built"] == 1952  # redfin takes priority
    assert merged["assessed_value"] == 320000  # assessor field added
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd C:/Users/tfalcon/co-op && python -m pytest tests/data-pipeline/test_normalizer.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: Implement normalizer**

```python
# tools/data-pipeline/normalizer.py
"""Schema normalization, validation, and data merging for the pipeline."""

import re
from datetime import datetime
from typing import Optional

from geocoding import normalize_address

# Condition keywords found in listing descriptions
_POOR_KEYWORDS = {"tear-down", "condemned", "uninhabitable", "fire damage", "major structural"}
_FAIR_KEYWORDS = {"as-is", "fixer", "estate sale", "needs work", "handyman", "distressed",
                  "investor special", "tlc", "deferred maintenance"}
_GOOD_KEYWORDS = {"updated", "renovated", "remodeled", "move-in ready", "turnkey"}

VALID_CONDITIONS = {"poor", "fair", "average", "good", "excellent"}


def _parse_price(val: str) -> int:
    """Parse '$385,000' or '385000' into int."""
    cleaned = re.sub(r'[^\d.]', '', str(val))
    return int(float(cleaned)) if cleaned else 0


def _parse_int(val) -> int:
    """Parse '1,200' or 1200 into int."""
    if isinstance(val, (int, float)):
        return int(val)
    cleaned = re.sub(r'[^\d.]', '', str(val))
    return int(float(cleaned)) if cleaned else 0


def _parse_float(val) -> float:
    """Parse '1.5' or 1.5 into float."""
    if isinstance(val, (int, float)):
        return float(val)
    cleaned = re.sub(r'[^\d.]', '', str(val))
    return float(cleaned) if cleaned else 0.0


def _parse_date(val: str) -> str:
    """Parse Redfin date formats into ISO YYYY-MM-DD."""
    val = val.strip()
    for fmt in ("%B %d, %Y", "%b %d, %Y", "%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(val, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return val  # Return as-is if parsing fails


def _infer_condition(description: str) -> str:
    """Infer property condition from listing description text."""
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
    """Convert a Redfin CSV row dict to the comp record schema.

    Redfin CSV column names are uppercase with inconsistent naming.
    This handles the known column variations.
    """
    address_parts = [
        row.get("ADDRESS", ""),
        row.get("CITY", "Portland"),
        row.get("STATE OR PROVINCE", "OR"),
    ]
    address = f"{address_parts[0]}, {address_parts[1]}, {address_parts[2]}"

    # Look for description in various possible columns
    description = ""
    for key in ("HOG_DESCRIPTION", "DESCRIPTION", "REMARKS", "URL (SEE https://www.redfin.com/buy-a-home/comparative-market-analysis FOR INFO ON PRICING)"):
        if key in row and row[key] and not row[key].startswith("http"):
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
    """Validate a comp record against the expected schema. Returns list of error strings."""
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

    # Date format check
    sale_date = record.get("sale_date", "")
    if sale_date and not re.match(r'^\d{4}-\d{2}-\d{2}$', sale_date):
        errors.append(f"Invalid sale_date format (expected YYYY-MM-DD): {sale_date}")

    return errors


def merge_redfin_assessor(redfin: dict, assessor: dict) -> dict:
    """Merge a Redfin comp record with assessor data.

    Redfin fields take priority for beds/baths/sqft/year_built.
    Assessor fills gaps (lot_sqft if missing) and adds assessed_value/zoning.
    """
    merged = dict(redfin)

    # Fill lot_sqft from assessor if Redfin has 0 or missing
    if merged.get("lot_sqft", 0) == 0 and assessor.get("lot_sqft", 0) > 0:
        merged["lot_sqft"] = assessor["lot_sqft"]

    # Add assessor-only fields
    for field in ("assessed_value", "market_value", "zoning", "property_id", "annual_tax"):
        if field in assessor:
            merged[field] = assessor[field]

    return merged
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd C:/Users/tfalcon/co-op && python -m pytest tests/data-pipeline/test_normalizer.py -v`
Expected: PASS — all 5 tests pass

- [ ] **Step 5: Commit**

```bash
git add tools/data-pipeline/normalizer.py tests/data-pipeline/test_normalizer.py
git commit -m "feat(data-pipeline): add normalizer with Redfin parsing, validation, and merge"
```

---

### Task 4: Redfin fetcher

**Files:**
- Create: `tools/data-pipeline/fetchers/redfin.py`
- Create: `tests/data-pipeline/test_redfin.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/data-pipeline/test_redfin.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'data-pipeline'))

import json
import csv
import io
from fetchers.redfin import build_redfin_url, parse_redfin_csv, RedfinFetcher
from config import NEIGHBORHOODS

def test_build_redfin_url_includes_required_params():
    url = build_redfin_url("lents")
    assert "sold" in url.lower() or "status" in url.lower() or "gis-csv" in url.lower()
    # URL should reference the neighborhood's region
    assert "region_id" in url or "zip" in url.lower() or "97266" in url

def test_parse_redfin_csv_produces_valid_records():
    csv_content = (
        "ADDRESS,CITY,STATE OR PROVINCE,SOLD DATE,PRICE,SQUARE FEET,"
        "BEDS,BATHS,LOT SIZE,YEAR BUILT\n"
        '123 SE Foster Rd,Portland,OR,"April 5, 2026","$385,000","1,200",'
        '3,1.5,"5,000",1952\n'
        '456 SE 92nd Ave,Portland,OR,"March 10, 2026","$310,000","1,050",'
        '2,1.0,"4,500",1948\n'
    )
    records = parse_redfin_csv(csv_content, "lents")
    assert len(records) == 2
    assert records[0]["address"] == "123 SE Foster Rd, Portland, OR"
    assert records[0]["sale_price"] == 385000
    assert records[0]["neighborhood"] == "lents"
    assert records[1]["sqft"] == 1050

def test_parse_redfin_csv_skips_invalid_rows():
    csv_content = (
        "ADDRESS,CITY,STATE OR PROVINCE,SOLD DATE,PRICE,SQUARE FEET,"
        "BEDS,BATHS,LOT SIZE,YEAR BUILT\n"
        '123 SE Foster Rd,Portland,OR,"April 5, 2026","$385,000","1,200",'
        '3,1.5,"5,000",1952\n'
        ',,OR,,,,0,0,,\n'  # empty/invalid row
    )
    records = parse_redfin_csv(csv_content, "lents")
    assert len(records) == 1

def test_redfin_fetcher_writes_json(tmp_path):
    fetcher = RedfinFetcher(output_dir=tmp_path)
    # Test writing parsed records
    records = [
        {
            "address": "123 SE Foster Rd, Portland, OR",
            "sale_date": "2026-04-05",
            "sale_price": 385000,
            "sqft": 1200,
            "beds": 3,
            "baths": 1.5,
            "lot_sqft": 5000,
            "year_built": 1952,
            "condition": "average",
            "neighborhood": "lents",
            "price_per_sqft": 320.83,
        }
    ]
    fetcher.write_comps("lents", records)
    outfile = tmp_path / "lents-comps.json"
    assert outfile.exists()
    data = json.loads(outfile.read_text())
    assert len(data) == 1
    assert data[0]["sale_price"] == 385000
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd C:/Users/tfalcon/co-op && python -m pytest tests/data-pipeline/test_redfin.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: Implement Redfin fetcher**

```python
# tools/data-pipeline/fetchers/redfin.py
"""Fetch comparable sales data from Redfin's CSV download endpoint."""

import csv
import io
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import requests

from config import (
    NEIGHBORHOODS, REDFIN_DOWNLOAD_BASE, COMP_SALES_DIR,
    COMP_PRICE_MIN, COMP_PRICE_MAX, COMP_DATE_RANGE_MONTHS, RATE_LIMITS,
)
from normalizer import normalize_redfin_row, validate_comp_record

logger = logging.getLogger(__name__)


def build_redfin_url(neighborhood_slug: str, months_back: int = None) -> str:
    """Build the Redfin CSV download URL for a neighborhood.

    Uses Redfin's /stingray/api/gis-csv endpoint with region-based search
    for sold properties within the date and price range.
    """
    if months_back is None:
        months_back = COMP_DATE_RANGE_MONTHS

    info = NEIGHBORHOODS[neighborhood_slug]
    params = info["redfin_region_url_params"]
    zip_codes = info["zip_codes"]

    sold_after = (datetime.now() - timedelta(days=months_back * 30)).strftime("%Y-%m-%d")

    # Redfin CSV download URL with query parameters
    # Using ZIP code-based search as a reliable fallback
    url = (
        f"{REDFIN_DOWNLOAD_BASE}"
        f"?al=1"
        f"&market={params['market']}"
        f"&min_price={COMP_PRICE_MIN}"
        f"&max_price={COMP_PRICE_MAX}"
        f"&region_id={params['region_id']}"
        f"&region_type={params['region_type']}"
        f"&sold_within_days={months_back * 30}"
        f"&status=9"  # 9 = sold
        f"&uipt=1,2,3"  # 1=house, 2=condo, 3=townhouse
        f"&v=8"
    )
    return url


def parse_redfin_csv(csv_content: str, neighborhood_slug: str) -> list[dict]:
    """Parse Redfin CSV content into normalized comp records.

    Skips rows that fail validation.
    """
    reader = csv.DictReader(io.StringIO(csv_content))
    records = []

    for row in reader:
        try:
            record = normalize_redfin_row(row, neighborhood_slug)
            errors = validate_comp_record(record)
            if errors:
                logger.debug("Skipping invalid row %s: %s", row.get("ADDRESS", "?"), errors)
                continue
            records.append(record)
        except Exception as e:
            logger.debug("Error parsing row: %s", e)
            continue

    return records


class RedfinFetcher:
    """Fetches and writes Redfin comparable sales data."""

    def __init__(self, output_dir: Optional[Path] = None, session: Optional[requests.Session] = None):
        self.output_dir = output_dir or COMP_SALES_DIR
        self.session = session or requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/csv",
        })

    def fetch_neighborhood(self, neighborhood_slug: str) -> list[dict]:
        """Fetch comps for a single neighborhood. Returns parsed records."""
        url = build_redfin_url(neighborhood_slug)
        logger.info("Fetching Redfin data for %s", neighborhood_slug)
        logger.debug("URL: %s", url)

        try:
            resp = self.session.get(url, timeout=30)
            resp.raise_for_status()

            # Redfin sometimes returns a text error or redirect
            content = resp.text
            if not content.strip() or content.startswith("<!DOCTYPE"):
                logger.warning("Redfin returned HTML instead of CSV for %s — may need updated URL params", neighborhood_slug)
                return []

            records = parse_redfin_csv(content, neighborhood_slug)
            logger.info("Parsed %d valid comps for %s", len(records), neighborhood_slug)
            return records

        except requests.RequestException as e:
            logger.error("Failed to fetch Redfin data for %s: %s", neighborhood_slug, e)
            return []

    def write_comps(self, neighborhood_slug: str, records: list[dict]) -> Path:
        """Write comp records to JSON file."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        outfile = self.output_dir / f"{neighborhood_slug}-comps.json"
        with open(outfile, "w") as f:
            json.dump(records, f, indent=2)
        logger.info("Wrote %d comps to %s", len(records), outfile)
        return outfile

    def fetch_all(self) -> dict[str, int]:
        """Fetch comps for all neighborhoods. Returns {slug: count} summary."""
        delay = RATE_LIMITS.get("redfin", 3.0)
        summary = {}

        for i, slug in enumerate(NEIGHBORHOODS):
            records = self.fetch_neighborhood(slug)
            if records:
                self.write_comps(slug, records)
            summary[slug] = len(records)

            if i < len(NEIGHBORHOODS) - 1:
                time.sleep(delay)

        return summary
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd C:/Users/tfalcon/co-op && python -m pytest tests/data-pipeline/test_redfin.py -v`
Expected: PASS — all 4 tests pass

- [ ] **Step 5: Commit**

```bash
git add tools/data-pipeline/fetchers/redfin.py tests/data-pipeline/test_redfin.py
git commit -m "feat(data-pipeline): add Redfin CSV fetcher with parsing and validation"
```

---

### Task 5: Assessor fetcher

**Files:**
- Create: `tools/data-pipeline/fetchers/assessor.py`
- Create: `tests/data-pipeline/test_assessor.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/data-pipeline/test_assessor.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'data-pipeline'))

import json
import pandas as pd
from fetchers.assessor import parse_assessor_csv, filter_by_neighborhoods, AssessorFetcher
from config import NEIGHBORHOODS

def test_parse_assessor_csv_basic():
    csv_content = (
        "PropertyID,SitusAddr,OwnerName,TotalAssessedValue,TotalMarketValue,"
        "TaxYear,TotalTax,LotSqFt,YearBuilt,Zoning,LegalDesc,SitusZip\n"
        "R123456,123 SE FOSTER RD,SMITH JOHN,320000,385000,"
        "2025,4200.00,5000,1952,R5,LOT 1 BLK 2,97266\n"
        "R789012,456 NE CULLY BLVD,DOE JANE,290000,340000,"
        "2025,3800.50,6000,1948,R7,LOT 5 BLK 8,97218\n"
    )
    df = parse_assessor_csv(csv_content)
    assert len(df) == 2
    assert df.iloc[0]["property_id"] == "R123456"
    assert df.iloc[0]["address"] == "123 SE FOSTER RD"
    assert df.iloc[0]["assessed_value"] == 320000

def test_filter_by_neighborhoods():
    data = [
        {"property_id": "R1", "address": "123 SE FOSTER RD", "zip_code": "97266",
         "assessed_value": 320000, "market_value": 385000, "tax_year": 2025,
         "annual_tax": 4200.0, "lot_sqft": 5000, "year_built": 1952, "zoning": "R5",
         "legal_description": "LOT 1", "owner_name": "SMITH"},
        {"property_id": "R2", "address": "789 NW 23RD AVE", "zip_code": "97210",
         "assessed_value": 600000, "market_value": 750000, "tax_year": 2025,
         "annual_tax": 8000.0, "lot_sqft": 3000, "year_built": 1920, "zoning": "CM1",
         "legal_description": "LOT 3", "owner_name": "DOE"},
    ]
    df = pd.DataFrame(data)
    filtered = filter_by_neighborhoods(df)
    assert len(filtered) == 1  # Only 97266 (lents) should match
    assert filtered.iloc[0]["property_id"] == "R1"

def test_assessor_fetcher_writes_json(tmp_path):
    fetcher = AssessorFetcher(output_dir=tmp_path)
    records = [
        {"property_id": "R1", "address": "123 SE FOSTER RD", "zip_code": "97266",
         "assessed_value": 320000, "market_value": 385000, "tax_year": 2025,
         "annual_tax": 4200.0, "lot_sqft": 5000, "year_built": 1952, "zoning": "R5",
         "legal_description": "LOT 1", "owner_name": "SMITH"},
    ]
    df = pd.DataFrame(records)
    fetcher.write_by_neighborhood(df)
    outfile = tmp_path / "multnomah-by-neighborhood" / "lents.json"
    assert outfile.exists()
    data = json.loads(outfile.read_text())
    assert len(data) == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd C:/Users/tfalcon/co-op && python -m pytest tests/data-pipeline/test_assessor.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: Implement assessor fetcher**

```python
# tools/data-pipeline/fetchers/assessor.py
"""Fetch and parse Multnomah County assessor bulk property data."""

import io
import json
import logging
from pathlib import Path
from typing import Optional

import pandas as pd
import requests

from config import (
    NEIGHBORHOODS, ASSESSOR_BULK_URL, ASSESSOR_DIR,
    ASSESSOR_BY_NEIGHBORHOOD_DIR,
)

logger = logging.getLogger(__name__)

# Mapping from Multnomah County CSV column names to our schema
# The county changes column names occasionally — these are the known variants
COLUMN_MAP = {
    "PropertyID": "property_id",
    "PROPERTYID": "property_id",
    "prop_id": "property_id",
    "SitusAddr": "address",
    "SITUSADDR": "address",
    "situs_addr": "address",
    "OwnerName": "owner_name",
    "OWNERNAME": "owner_name",
    "owner_name": "owner_name",
    "TotalAssessedValue": "assessed_value",
    "TOTALASSESSEDVALUE": "assessed_value",
    "total_assessed": "assessed_value",
    "TotalMarketValue": "market_value",
    "TOTALMARKETVALUE": "market_value",
    "total_market": "market_value",
    "TaxYear": "tax_year",
    "TAXYEAR": "tax_year",
    "tax_year": "tax_year",
    "TotalTax": "annual_tax",
    "TOTALTAX": "annual_tax",
    "total_tax": "annual_tax",
    "LotSqFt": "lot_sqft",
    "LOTSQFT": "lot_sqft",
    "lot_sqft": "lot_sqft",
    "YearBuilt": "year_built",
    "YEARBUILT": "year_built",
    "year_built": "year_built",
    "Zoning": "zoning",
    "ZONING": "zoning",
    "zoning": "zoning",
    "LegalDesc": "legal_description",
    "LEGALDESC": "legal_description",
    "legal_desc": "legal_description",
    "SitusZip": "zip_code",
    "SITUSZIP": "zip_code",
    "situs_zip": "zip_code",
}


def parse_assessor_csv(csv_content: str) -> pd.DataFrame:
    """Parse Multnomah County assessor CSV into a normalized DataFrame."""
    df = pd.read_csv(io.StringIO(csv_content), dtype=str)

    # Rename columns using our mapping
    rename = {}
    for col in df.columns:
        if col in COLUMN_MAP:
            rename[col] = COLUMN_MAP[col]
    df = df.rename(columns=rename)

    # Type conversions
    int_cols = ["assessed_value", "market_value", "tax_year", "lot_sqft", "year_built"]
    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].str.replace(",", ""), errors="coerce").fillna(0).astype(int)

    float_cols = ["annual_tax"]
    for col in float_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].str.replace(",", ""), errors="coerce").fillna(0.0)

    # Clean zip codes (take first 5 digits)
    if "zip_code" in df.columns:
        df["zip_code"] = df["zip_code"].str[:5]

    return df


def filter_by_neighborhoods(df: pd.DataFrame) -> pd.DataFrame:
    """Filter assessor data to only target neighborhoods by ZIP code."""
    target_zips = set()
    for info in NEIGHBORHOODS.values():
        target_zips.update(info["zip_codes"])

    if "zip_code" not in df.columns:
        logger.warning("No zip_code column found — cannot filter by neighborhood")
        return df

    return df[df["zip_code"].isin(target_zips)].copy()


def _zip_to_neighborhood(zip_code: str) -> Optional[str]:
    """Map a ZIP code to its primary neighborhood slug."""
    for slug, info in NEIGHBORHOODS.items():
        if zip_code in info["zip_codes"]:
            return slug
    return None


class AssessorFetcher:
    """Fetches and processes Multnomah County assessor bulk data."""

    def __init__(self, output_dir: Optional[Path] = None, session: Optional[requests.Session] = None):
        self.output_dir = output_dir or ASSESSOR_DIR
        self.by_neighborhood_dir = self.output_dir / "multnomah-by-neighborhood"
        self.session = session or requests.Session()

    def fetch_bulk(self) -> Optional[pd.DataFrame]:
        """Download the bulk assessor CSV from Multnomah County.

        Note: The exact download URL may change. The county's data download
        page has links to current CSV files. This attempts the direct download
        and falls back to instructions if the URL has changed.
        """
        logger.info("Fetching Multnomah County assessor bulk data")
        try:
            resp = self.session.get(ASSESSOR_BULK_URL, timeout=60)
            resp.raise_for_status()

            # If we get HTML (the download page), we need to extract the CSV link
            if resp.headers.get("content-type", "").startswith("text/html"):
                logger.warning(
                    "Assessor URL returned HTML page — bulk CSV may require manual download. "
                    "Visit %s and download the property data CSV.", ASSESSOR_BULK_URL
                )
                return None

            df = parse_assessor_csv(resp.text)
            logger.info("Parsed %d assessor records", len(df))
            return df

        except requests.RequestException as e:
            logger.error("Failed to fetch assessor data: %s", e)
            return None

    def load_local_csv(self, csv_path: Path) -> pd.DataFrame:
        """Load assessor data from a locally downloaded CSV file."""
        logger.info("Loading assessor CSV from %s", csv_path)
        with open(csv_path) as f:
            df = parse_assessor_csv(f.read())
        logger.info("Parsed %d assessor records from local file", len(df))
        return df

    def write_bulk_csv(self, df: pd.DataFrame) -> Path:
        """Write filtered assessor data as CSV."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        outfile = self.output_dir / "multnomah-bulk-extract.csv"
        filtered = filter_by_neighborhoods(df)
        filtered.to_csv(outfile, index=False)
        logger.info("Wrote %d filtered records to %s", len(filtered), outfile)
        return outfile

    def write_by_neighborhood(self, df: pd.DataFrame) -> dict[str, int]:
        """Write assessor data split by neighborhood as JSON files."""
        self.by_neighborhood_dir.mkdir(parents=True, exist_ok=True)
        filtered = filter_by_neighborhoods(df)
        summary = {}

        for slug in NEIGHBORHOODS:
            zips = NEIGHBORHOODS[slug]["zip_codes"]
            hood_df = filtered[filtered["zip_code"].isin(zips)]
            records = hood_df.to_dict(orient="records")

            outfile = self.by_neighborhood_dir / f"{slug}.json"
            with open(outfile, "w") as f:
                json.dump(records, f, indent=2, default=str)

            summary[slug] = len(records)
            logger.info("Wrote %d assessor records for %s", len(records), slug)

        return summary

    def fetch_all(self) -> dict[str, int]:
        """Full pipeline: fetch/load → filter → write CSV + JSON."""
        # Try fetching; if that fails, check for local file
        df = self.fetch_bulk()

        if df is None:
            local_csv = self.output_dir / "multnomah-bulk-extract.csv"
            if local_csv.exists():
                logger.info("Using existing local CSV at %s", local_csv)
                df = self.load_local_csv(local_csv)
            else:
                logger.error("No assessor data available — download manually from %s", ASSESSOR_BULK_URL)
                return {}

        self.write_bulk_csv(df)
        return self.write_by_neighborhood(df)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd C:/Users/tfalcon/co-op && python -m pytest tests/data-pipeline/test_assessor.py -v`
Expected: PASS — all 3 tests pass

- [ ] **Step 5: Commit**

```bash
git add tools/data-pipeline/fetchers/assessor.py tests/data-pipeline/test_assessor.py
git commit -m "feat(data-pipeline): add Multnomah County assessor bulk data fetcher"
```

---

### Task 6: PortlandMaps fetcher

**Files:**
- Create: `tools/data-pipeline/fetchers/portlandmaps.py`
- Create: `tests/data-pipeline/test_portlandmaps.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/data-pipeline/test_portlandmaps.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'data-pipeline'))

import json
from fetchers.portlandmaps import parse_portlandmaps_response, PortlandMapsFetcher, address_to_slug

def test_address_to_slug():
    assert address_to_slug("123 SE Foster Rd, Portland, OR") == "123-se-foster-rd-portland-or"
    assert address_to_slug("456 NE Cully Blvd #4") == "456-ne-cully-blvd-4"

def test_parse_portlandmaps_response():
    api_response = {
        "results": [{
            "address": "123 SE FOSTER RD",
            "state_id": "1S2E15AC 01200",
            "zoning": "R5",
            "comprehensive_plan": "Single-Dwelling Residential",
            "flood_zone": "X",
            "seismic": "moderate",
            "permits": [
                {"status": "final", "year": 2022},
                {"status": "final", "year": 2023},
                {"status": "issued", "year": 2025},
            ],
            "liens": [{"amount": 5000.00, "type": "tax"}],
            "neighborhood_association": "Foster-Powell NA",
        }]
    }
    info = parse_portlandmaps_response(api_response, "123 SE Foster Rd")
    assert info["address"] == "123 SE Foster Rd"
    assert info["zoning"] == "R5"
    assert info["permits_last_5yr"] == 3
    assert info["open_permits"] == 1
    assert info["liens"] == 1
    assert info["lien_total"] == 5000.00

def test_portlandmaps_fetcher_cache(tmp_path):
    fetcher = PortlandMapsFetcher(cache_dir=tmp_path)
    # Write a cached record
    cached = {
        "address": "123 SE Foster Rd",
        "state_id": "1S2E15AC 01200",
        "zoning": "R5",
        "comprehensive_plan": "Single-Dwelling Residential",
        "flood_zone": "X",
        "seismic_zone": "moderate",
        "permits_last_5yr": 3,
        "open_permits": 1,
        "liens": 1,
        "lien_total": 5000.00,
        "neighborhood_association": "Foster-Powell NA",
    }
    slug = address_to_slug("123 SE Foster Rd")
    cache_file = tmp_path / f"{slug}.json"
    cache_file.write_text(json.dumps(cached))

    result = fetcher.lookup_cached("123 SE Foster Rd")
    assert result is not None
    assert result["zoning"] == "R5"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd C:/Users/tfalcon/co-op && python -m pytest tests/data-pipeline/test_portlandmaps.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: Implement PortlandMaps fetcher**

```python
# tools/data-pipeline/fetchers/portlandmaps.py
"""Fetch property info from PortlandMaps.com REST API."""

import json
import logging
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

from config import PORTLANDMAPS_API_BASE, PORTLANDMAPS_DIR, RATE_LIMITS

logger = logging.getLogger(__name__)


def address_to_slug(address: str) -> str:
    """Convert an address to a filesystem-safe slug."""
    slug = address.lower().strip()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug


def parse_portlandmaps_response(api_response: dict, original_address: str) -> dict:
    """Parse PortlandMaps API response into our PortlandMapsInfo schema."""
    results = api_response.get("results", [])
    if not results:
        return {
            "address": original_address,
            "state_id": "",
            "zoning": "",
            "comprehensive_plan": "",
            "flood_zone": "",
            "seismic_zone": "",
            "permits_last_5yr": 0,
            "open_permits": 0,
            "liens": 0,
            "lien_total": 0.0,
            "neighborhood_association": "",
        }

    r = results[0]

    # Count permits in last 5 years
    permits = r.get("permits", [])
    current_year = datetime.now().year
    permits_5yr = [p for p in permits if p.get("year", 0) >= current_year - 5]
    open_permits = len([p for p in permits if p.get("status", "").lower() in ("issued", "under review", "pending")])

    # Sum liens
    liens_list = r.get("liens", [])
    lien_total = sum(l.get("amount", 0) for l in liens_list)

    return {
        "address": original_address,
        "state_id": r.get("state_id", ""),
        "zoning": r.get("zoning", ""),
        "comprehensive_plan": r.get("comprehensive_plan", ""),
        "flood_zone": r.get("flood_zone", ""),
        "seismic_zone": r.get("seismic", r.get("seismic_zone", "")),
        "permits_last_5yr": len(permits_5yr),
        "open_permits": open_permits,
        "liens": len(liens_list),
        "lien_total": round(lien_total, 2),
        "neighborhood_association": r.get("neighborhood_association", ""),
    }


class PortlandMapsFetcher:
    """Fetch and cache property info from PortlandMaps API."""

    def __init__(self, cache_dir: Optional[Path] = None, session: Optional[requests.Session] = None):
        self.cache_dir = cache_dir or PORTLANDMAPS_DIR
        self.session = session or requests.Session()
        self.session.headers.update({
            "User-Agent": "PortlandCoopDataPipeline/1.0",
            "Accept": "application/json",
        })

    def lookup_cached(self, address: str) -> Optional[dict]:
        """Check local cache for a property."""
        slug = address_to_slug(address)
        cache_file = self.cache_dir / f"{slug}.json"
        if cache_file.exists():
            with open(cache_file) as f:
                return json.load(f)
        return None

    def fetch_property(self, address: str) -> Optional[dict]:
        """Fetch property info from PortlandMaps API."""
        # Check cache first
        cached = self.lookup_cached(address)
        if cached is not None:
            logger.debug("Cache hit for %s", address)
            return cached

        logger.info("Fetching PortlandMaps data for %s", address)

        try:
            # PortlandMaps detail API
            resp = self.session.get(
                f"{PORTLANDMAPS_API_BASE}/detail/",
                params={"address": address},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

            info = parse_portlandmaps_response(data, address)

            # Cache the result
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            slug = address_to_slug(address)
            cache_file = self.cache_dir / f"{slug}.json"
            with open(cache_file, "w") as f:
                json.dump(info, f, indent=2)

            return info

        except requests.RequestException as e:
            logger.error("Failed to fetch PortlandMaps data for %s: %s", address, e)
            return None

    def fetch_addresses(self, addresses: list[str]) -> dict[str, Optional[dict]]:
        """Fetch info for multiple addresses with rate limiting."""
        delay = RATE_LIMITS.get("portlandmaps", 1.0)
        results = {}
        for i, addr in enumerate(addresses):
            results[addr] = self.fetch_property(addr)
            if i < len(addresses) - 1 and results[addr] is not None:
                # Only delay if we actually hit the API (not cache)
                cached = self.lookup_cached(addr)
                if cached is None:
                    time.sleep(delay)
        return results
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd C:/Users/tfalcon/co-op && python -m pytest tests/data-pipeline/test_portlandmaps.py -v`
Expected: PASS — all 3 tests pass

- [ ] **Step 5: Commit**

```bash
git add tools/data-pipeline/fetchers/portlandmaps.py tests/data-pipeline/test_portlandmaps.py
git commit -m "feat(data-pipeline): add PortlandMaps API fetcher with caching"
```

---

### Task 7: Portland Police crime data fetcher

**Files:**
- Create: `tools/data-pipeline/fetchers/portland_police.py`
- Create: `tests/data-pipeline/test_portland_police.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/data-pipeline/test_portland_police.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'data-pipeline'))

import json
from fetchers.portland_police import compute_crime_trend, normalize_crime_score, PoliceFetcher

def test_compute_crime_trend_decreasing():
    # 100 crimes last year, 80 this year = -20% = improving
    trend = compute_crime_trend(prior_count=100, current_count=80)
    assert trend < 0  # negative = improving

def test_compute_crime_trend_increasing():
    trend = compute_crime_trend(prior_count=80, current_count=100)
    assert trend > 0  # positive = worsening

def test_compute_crime_trend_stable():
    trend = compute_crime_trend(prior_count=100, current_count=100)
    assert trend == 0.0

def test_normalize_crime_score_range():
    # Score should be clamped to [-10, +10]
    assert normalize_crime_score(-50) == -10.0
    assert normalize_crime_score(50) == 10.0
    assert -10 <= normalize_crime_score(-8) <= 10

def test_normalize_crime_score_maps_correctly():
    # -20% change should map to roughly -4 on [-10,10] scale
    score = normalize_crime_score(-20)
    assert -6 <= score <= -2

def test_police_fetcher_updates_neighborhood_json(tmp_path):
    # Create a minimal neighborhood JSON
    hood_file = tmp_path / "lents.json"
    hood_data = {
        "name": "Lents",
        "characteristics": {
            "crime_trend": "Unknown"
        }
    }
    hood_file.write_text(json.dumps(hood_data))

    fetcher = PoliceFetcher(neighborhood_dir=tmp_path)
    fetcher.update_neighborhood_crime("lents", -3.5)

    updated = json.loads(hood_file.read_text())
    assert updated["characteristics"]["crime_trend"] == "Improving — down 3.5% YoY"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd C:/Users/tfalcon/co-op && python -m pytest tests/data-pipeline/test_portland_police.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: Implement Portland Police fetcher**

```python
# tools/data-pipeline/fetchers/portland_police.py
"""Fetch and process Portland Police Bureau crime data."""

import json
import logging
from pathlib import Path
from typing import Optional

import requests

from config import NEIGHBORHOODS, NEIGHBORHOOD_DIR, PORTLAND_POLICE_DATA_URL, RATE_LIMITS

logger = logging.getLogger(__name__)

# Portland Open Data crime statistics API
# This uses the Socrata Open Data API (SODA) endpoint for PPB crime data
PORTLAND_CRIME_API = "https://public.tableau.com/views/PPBOpenData/CrimeData"
# Fallback: Portland's ArcGIS open data
PORTLAND_CRIME_ARCGIS = "https://opendata.arcgis.com/datasets/portland-crime-data.geojson"

# ZIP code to approximate neighborhood mapping for crime aggregation
ZIP_TO_NEIGHBORHOOD = {}
for slug, info in NEIGHBORHOODS.items():
    for z in info["zip_codes"]:
        ZIP_TO_NEIGHBORHOOD.setdefault(z, []).append(slug)


def compute_crime_trend(prior_count: int, current_count: int) -> float:
    """Compute year-over-year crime trend as percentage change.

    Returns: negative = improving (fewer crimes), positive = worsening.
    """
    if prior_count == 0:
        return 0.0
    return round(((current_count - prior_count) / prior_count) * 100, 1)


def normalize_crime_score(pct_change: float) -> float:
    """Normalize a percentage change to the [-10, +10] scale.

    Scale: -50% or better → -10 (strong improvement)
           0% → 0 (stable)
           +50% or worse → +10 (strong worsening)
    """
    # Linear mapping: -50% → -10, +50% → +10
    score = (pct_change / 50) * 10
    return round(max(-10.0, min(10.0, score)), 1)


def _crime_trend_description(pct_change: float) -> str:
    """Generate a human-readable crime trend description."""
    if pct_change < -2:
        return f"Improving — down {abs(pct_change)}% YoY"
    elif pct_change > 2:
        return f"Worsening — up {abs(pct_change)}% YoY"
    else:
        return f"Stable — {abs(pct_change)}% change YoY"


class PoliceFetcher:
    """Fetch Portland Police crime data and update neighborhood profiles."""

    def __init__(self, neighborhood_dir: Optional[Path] = None,
                 session: Optional[requests.Session] = None):
        self.neighborhood_dir = neighborhood_dir or NEIGHBORHOOD_DIR
        self.session = session or requests.Session()

    def fetch_crime_data(self) -> Optional[dict]:
        """Attempt to fetch crime statistics from Portland open data.

        Returns dict of {zip_code: {"prior_year": count, "current_year": count}}
        or None if fetching fails.
        """
        logger.info("Fetching Portland crime data")

        # Try ArcGIS endpoint (more reliable for programmatic access)
        try:
            resp = self.session.get(PORTLAND_CRIME_ARCGIS, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            # Aggregate by ZIP code and year
            zip_counts: dict[str, dict[str, int]] = {}
            features = data.get("features", [])

            for feature in features:
                props = feature.get("properties", {})
                zip_code = str(props.get("zip", props.get("ZIP", "")))[:5]
                year = props.get("year", props.get("YEAR", ""))

                if not zip_code or not year:
                    continue

                year_str = str(year)
                if zip_code not in zip_counts:
                    zip_counts[zip_code] = {}
                zip_counts[zip_code][year_str] = zip_counts[zip_code].get(year_str, 0) + 1

            return zip_counts

        except Exception as e:
            logger.warning("Failed to fetch crime data from ArcGIS: %s", e)
            return None

    def update_neighborhood_crime(self, slug: str, pct_change: float) -> None:
        """Update a neighborhood JSON file's crime_trend field."""
        hood_file = self.neighborhood_dir / f"{slug}.json"
        if not hood_file.exists():
            logger.warning("Neighborhood file not found: %s", hood_file)
            return

        with open(hood_file) as f:
            data = json.load(f)

        if "characteristics" not in data:
            data["characteristics"] = {}

        data["characteristics"]["crime_trend"] = _crime_trend_description(pct_change)
        data["characteristics"]["crime_trend_score"] = normalize_crime_score(pct_change)

        with open(hood_file, "w") as f:
            json.dump(data, f, indent=2)

        logger.info("Updated crime trend for %s: %s", slug, data["characteristics"]["crime_trend"])

    def fetch_all(self) -> dict[str, float]:
        """Full pipeline: fetch crime data → compute trends → update neighborhoods.

        Returns {slug: pct_change} summary.
        """
        crime_data = self.fetch_crime_data()
        summary = {}

        if crime_data is None:
            logger.warning("No crime data available — skipping neighborhood updates")
            return summary

        # Determine the two most recent years in the data
        all_years = set()
        for zd in crime_data.values():
            all_years.update(zd.keys())
        sorted_years = sorted(all_years, reverse=True)

        if len(sorted_years) < 2:
            logger.warning("Need at least 2 years of crime data for trend calculation")
            return summary

        current_year = sorted_years[0]
        prior_year = sorted_years[1]
        logger.info("Computing crime trends: %s vs %s", current_year, prior_year)

        for slug, info in NEIGHBORHOODS.items():
            prior_total = 0
            current_total = 0
            for z in info["zip_codes"]:
                if z in crime_data:
                    prior_total += crime_data[z].get(prior_year, 0)
                    current_total += crime_data[z].get(current_year, 0)

            if prior_total > 0:
                pct_change = compute_crime_trend(prior_total, current_total)
                self.update_neighborhood_crime(slug, pct_change)
                summary[slug] = pct_change
            else:
                logger.warning("No crime data for %s — skipping", slug)

        return summary
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd C:/Users/tfalcon/co-op && python -m pytest tests/data-pipeline/test_portland_police.py -v`
Expected: PASS — all 6 tests pass

- [ ] **Step 5: Commit**

```bash
git add tools/data-pipeline/fetchers/portland_police.py tests/data-pipeline/test_portland_police.py
git commit -m "feat(data-pipeline): add Portland Police crime data fetcher"
```

---

### Task 8: Distressed listing aggregator

**Files:**
- Create: `tools/data-pipeline/fetchers/distressed.py`
- Create: `tests/data-pipeline/test_distressed.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/data-pipeline/test_distressed.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'data-pipeline'))

import json
from fetchers.distressed import identify_distressed, score_distress_signal, DistressedAggregator

def test_identify_distressed_from_assessor():
    assessor_records = [
        {"address": "123 SE FOSTER RD", "assessed_value": 320000, "market_value": 385000,
         "lot_sqft": 5000, "year_built": 1952, "zoning": "R5", "zip_code": "97266",
         "annual_tax": 4200, "owner_name": "SMITH"},
        {"address": "456 SE 92ND AVE", "assessed_value": 180000, "market_value": 200000,
         "lot_sqft": 4500, "year_built": 1948, "zoning": "R5", "zip_code": "97266",
         "annual_tax": 0},  # zero tax = delinquent signal
    ]
    portlandmaps = {
        "123 SE FOSTER RD": {"liens": 0, "lien_total": 0, "open_permits": 0},
        "456 SE 92ND AVE": {"liens": 2, "lien_total": 15000, "open_permits": 0},
    }
    distressed = identify_distressed(assessor_records, portlandmaps)
    assert len(distressed) >= 1
    addresses = [d["address"] for d in distressed]
    assert "456 SE 92ND AVE" in addresses

def test_score_distress_signal():
    signals = {"tax_delinquent": True, "liens": True, "code_violations": False, "below_market": False}
    score = score_distress_signal(signals)
    assert 0 < score <= 10

def test_score_distress_signal_no_signals():
    signals = {"tax_delinquent": False, "liens": False, "code_violations": False, "below_market": False}
    score = score_distress_signal(signals)
    assert score == 0

def test_aggregator_writes_files(tmp_path):
    agg = DistressedAggregator(output_dir=tmp_path)
    distressed = [
        {"address": "456 SE 92ND AVE", "neighborhood": "lents", "distress_signals": ["tax_delinquent", "liens"],
         "distress_score": 6, "estimated_value_range": [180000, 220000], "source": "assessor+portlandmaps"},
    ]
    watchlist = [
        {"address": "789 NE CULLY BLVD", "neighborhood": "cully", "distress_signals": ["below_market"],
         "distress_score": 3, "estimated_value_range": [200000, 250000], "source": "comp_analysis"},
    ]
    agg.write_results(distressed, watchlist)
    assert (tmp_path / "distressed-listings.json").exists()
    assert (tmp_path / "watchlist.json").exists()
    d_data = json.loads((tmp_path / "distressed-listings.json").read_text())
    assert len(d_data) == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd C:/Users/tfalcon/co-op && python -m pytest tests/data-pipeline/test_distressed.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: Implement distressed aggregator**

```python
# tools/data-pipeline/fetchers/distressed.py
"""Aggregate distressed property leads from multiple data sources."""

import json
import logging
from pathlib import Path
from typing import Optional

from config import NEIGHBORHOODS, LISTINGS_DIR, COMP_PRICE_MIN, COMP_PRICE_MAX

logger = logging.getLogger(__name__)

# Distress signal weights for scoring
SIGNAL_WEIGHTS = {
    "tax_delinquent": 3,
    "liens": 2,
    "code_violations": 2,
    "below_market": 1,
    "long_dom": 1,
    "estate_sale": 1,
}

# Deal guardrails from M1 decisions
MAX_PURCHASE_PRICE = 200_000
TARGET_NEIGHBORHOODS = {"lents", "cully", "parkrose"}  # Tier 1


def score_distress_signal(signals: dict[str, bool]) -> int:
    """Score a set of distress signals. Higher = more distressed."""
    return sum(SIGNAL_WEIGHTS.get(k, 0) for k, v in signals.items() if v)


def identify_distressed(
    assessor_records: list[dict],
    portlandmaps_data: dict[str, dict],
    comp_records: Optional[list[dict]] = None,
) -> list[dict]:
    """Cross-reference data sources to identify distressed properties.

    Signals:
    - Tax delinquent: annual_tax == 0 or missing
    - Liens: portlandmaps liens > 0
    - Code violations: portlandmaps open_permits > 2 (proxy for violations)
    - Below market: assessed_value significantly below market_value or neighborhood median
    """
    distressed = []

    for record in assessor_records:
        address = record.get("address", "")
        signals = {
            "tax_delinquent": False,
            "liens": False,
            "code_violations": False,
            "below_market": False,
        }

        # Tax delinquency signal
        annual_tax = record.get("annual_tax", 0)
        if annual_tax == 0 or annual_tax is None:
            signals["tax_delinquent"] = True

        # PortlandMaps signals
        pm_data = portlandmaps_data.get(address, {})
        if pm_data.get("liens", 0) > 0:
            signals["liens"] = True
        if pm_data.get("open_permits", 0) > 2:
            signals["code_violations"] = True

        # Below-market signal
        assessed = record.get("assessed_value", 0)
        market = record.get("market_value", 0)
        if market > 0 and assessed > 0 and (assessed / market) < 0.75:
            signals["below_market"] = True

        score = score_distress_signal(signals)
        if score == 0:
            continue

        # Determine neighborhood from ZIP
        zip_code = str(record.get("zip_code", ""))
        neighborhood = None
        for slug, info in NEIGHBORHOODS.items():
            if zip_code in info["zip_codes"]:
                neighborhood = slug
                break

        active_signals = [k for k, v in signals.items() if v]
        estimated_low = int(assessed * 0.85) if assessed else 0
        estimated_high = int(market * 1.0) if market else int(assessed * 1.2) if assessed else 0

        distressed.append({
            "address": address,
            "neighborhood": neighborhood,
            "zip_code": zip_code,
            "distress_signals": active_signals,
            "distress_score": score,
            "estimated_value_range": [estimated_low, estimated_high],
            "assessed_value": assessed,
            "market_value": market,
            "lot_sqft": record.get("lot_sqft", 0),
            "year_built": record.get("year_built", 0),
            "zoning": record.get("zoning", ""),
            "source": "assessor+portlandmaps",
        })

    # Sort by distress score descending
    distressed.sort(key=lambda d: d["distress_score"], reverse=True)
    return distressed


def filter_to_deal_guardrails(properties: list[dict]) -> tuple[list[dict], list[dict]]:
    """Split distressed properties into deal-ready and watchlist.

    Deal-ready: within price ceiling and in target neighborhoods.
    Watchlist: distressed but outside current deal parameters.
    """
    deal_ready = []
    watchlist = []

    for prop in properties:
        est_high = prop.get("estimated_value_range", [0, 999999])[1]
        neighborhood = prop.get("neighborhood")

        if est_high <= MAX_PURCHASE_PRICE and neighborhood in TARGET_NEIGHBORHOODS:
            deal_ready.append(prop)
        else:
            watchlist.append(prop)

    return deal_ready, watchlist


class DistressedAggregator:
    """Aggregates distressed property leads and writes results."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or LISTINGS_DIR

    def write_results(self, distressed: list[dict], watchlist: list[dict]) -> None:
        """Write distressed listings and watchlist to JSON files."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        distressed_file = self.output_dir / "distressed-listings.json"
        with open(distressed_file, "w") as f:
            json.dump(distressed, f, indent=2)
        logger.info("Wrote %d distressed listings to %s", len(distressed), distressed_file)

        watchlist_file = self.output_dir / "watchlist.json"
        with open(watchlist_file, "w") as f:
            json.dump(watchlist, f, indent=2)
        logger.info("Wrote %d watchlist items to %s", len(watchlist), watchlist_file)

    def aggregate(
        self,
        assessor_records: list[dict],
        portlandmaps_data: dict[str, dict],
        comp_records: Optional[list[dict]] = None,
    ) -> dict[str, int]:
        """Full pipeline: identify → filter → write. Returns summary counts."""
        all_distressed = identify_distressed(assessor_records, portlandmaps_data, comp_records)
        deal_ready, watchlist = filter_to_deal_guardrails(all_distressed)

        self.write_results(deal_ready, watchlist)

        return {
            "total_distressed_found": len(all_distressed),
            "deal_ready": len(deal_ready),
            "watchlist": len(watchlist),
        }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd C:/Users/tfalcon/co-op && python -m pytest tests/data-pipeline/test_distressed.py -v`
Expected: PASS — all 4 tests pass

- [ ] **Step 5: Commit**

```bash
git add tools/data-pipeline/fetchers/distressed.py tests/data-pipeline/test_distressed.py
git commit -m "feat(data-pipeline): add distressed property aggregator"
```

---

### Task 9: RealCompLoader (replaces SyntheticMLSGenerator)

**Files:**
- Create: `tools/data-pipeline/loaders/real_comp_loader.py`
- Create: `tests/data-pipeline/test_real_comp_loader.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/data-pipeline/test_real_comp_loader.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'data-pipeline'))

import json
from datetime import date
from loaders.real_comp_loader import RealCompLoader

def _write_sample_comps(tmp_path):
    """Write sample comp data for testing."""
    comps_dir = tmp_path / "comp-sales"
    comps_dir.mkdir()
    comps = [
        {"address": "123 SE Foster Rd, Portland, OR", "sale_date": "2026-03-01",
         "sale_price": 350000, "sqft": 1100, "beds": 3, "baths": 1.5,
         "lot_sqft": 5000, "year_built": 1952, "condition": "average",
         "neighborhood": "lents", "price_per_sqft": 318.18, "lat": 45.4833, "lon": -122.5777},
        {"address": "456 SE 92nd Ave, Portland, OR", "sale_date": "2026-01-15",
         "sale_price": 310000, "sqft": 1000, "beds": 2, "baths": 1.0,
         "lot_sqft": 4500, "year_built": 1948, "condition": "fair",
         "neighborhood": "lents", "price_per_sqft": 310.00, "lat": 45.4840, "lon": -122.5760},
        {"address": "789 SE Harold St, Portland, OR", "sale_date": "2025-06-01",
         "sale_price": 420000, "sqft": 1400, "beds": 3, "baths": 2.0,
         "lot_sqft": 6000, "year_built": 1955, "condition": "good",
         "neighborhood": "lents", "price_per_sqft": 300.00, "lat": 45.4850, "lon": -122.5790},
    ]
    (comps_dir / "lents-comps.json").write_text(json.dumps(comps))
    return comps_dir

def test_load_comps_returns_list(tmp_path):
    comps_dir = _write_sample_comps(tmp_path)
    loader = RealCompLoader(comps_dir=comps_dir)
    result = loader.load_comps("lents")
    assert isinstance(result, list)
    assert len(result) == 3

def test_load_comps_filters_by_date(tmp_path):
    comps_dir = _write_sample_comps(tmp_path)
    loader = RealCompLoader(comps_dir=comps_dir)
    # Only last 6 months from reference date 2026-04-08
    result = loader.load_comps("lents", months_back=6, reference_date=date(2026, 4, 8))
    # Should exclude the June 2025 comp
    assert len(result) == 2

def test_load_comps_filters_by_count(tmp_path):
    comps_dir = _write_sample_comps(tmp_path)
    loader = RealCompLoader(comps_dir=comps_dir)
    result = loader.load_comps("lents", count=2)
    assert len(result) == 2

def test_load_comps_returns_compsale_compatible(tmp_path):
    comps_dir = _write_sample_comps(tmp_path)
    loader = RealCompLoader(comps_dir=comps_dir)
    result = loader.load_comps("lents", count=1)
    comp = result[0]
    # Must have all CompSale fields
    required = {"address", "sale_date", "sale_price", "sqft", "beds", "baths",
                "lot_sqft", "year_built", "condition", "distance_miles", "price_per_sqft"}
    assert required.issubset(set(vars(comp).keys()))

def test_load_comps_computes_distance(tmp_path):
    comps_dir = _write_sample_comps(tmp_path)
    loader = RealCompLoader(comps_dir=comps_dir)
    # Subject at a known location
    result = loader.load_comps("lents", subject_lat=45.4835, subject_lon=-122.5770)
    for comp in result:
        assert comp.distance_miles >= 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd C:/Users/tfalcon/co-op && python -m pytest tests/data-pipeline/test_real_comp_loader.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: Implement RealCompLoader**

```python
# tools/data-pipeline/loaders/real_comp_loader.py
"""RealCompLoader — drop-in replacement for SyntheticMLSGenerator.

Reads real comp data from data/comp-sales/{neighborhood}-comps.json
and returns List[CompSale] with the same interface.
"""

import json
import logging
from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "comp-analyzer"))
from data_sources import CompSale

from geocoding import haversine
from config import COMP_SALES_DIR

logger = logging.getLogger(__name__)

# Neighborhood name normalization (matches data_sources.py conventions)
_SLUG_MAP = {
    "st. johns": "st-johns",
    "st johns": "st-johns",
    "foster-powell": "foster-powell",
    "foster powell": "foster-powell",
}


def _normalize_slug(neighborhood: str) -> str:
    """Normalize neighborhood name to file slug."""
    lower = neighborhood.strip().lower()
    return _SLUG_MAP.get(lower, lower)


class RealCompLoader:
    """Load real comparable sales from JSON files.

    Drop-in replacement for SyntheticMLSGenerator. Same method signature
    for load_comps() as generate_comps().
    """

    def __init__(self, comps_dir: Optional[Path] = None):
        self.comps_dir = comps_dir or COMP_SALES_DIR

    def load_comps(
        self,
        neighborhood: str,
        sqft_target: int = 1200,
        beds: int = 3,
        baths: float = 1.0,
        radius_miles: float = 0.5,
        months_back: int = 12,
        count: int = 10,
        reference_date: Optional[date] = None,
        subject_lat: Optional[float] = None,
        subject_lon: Optional[float] = None,
    ) -> List[CompSale]:
        """Load and filter real comps from JSON files.

        Parameters match SyntheticMLSGenerator.generate_comps() for drop-in use.
        Additional params subject_lat/subject_lon enable distance computation.
        """
        slug = _normalize_slug(neighborhood)
        comps_file = self.comps_dir / f"{slug}-comps.json"

        if not comps_file.exists():
            logger.warning("No comp data found at %s", comps_file)
            return []

        with open(comps_file) as f:
            raw_records = json.load(f)

        ref = reference_date or date.today()
        cutoff = ref - timedelta(days=months_back * 30)

        comps = []
        for record in raw_records:
            # Date filter
            try:
                sale_date = date.fromisoformat(record["sale_date"])
            except (ValueError, KeyError):
                continue
            if sale_date < cutoff:
                continue

            # Compute distance
            distance = 0.0
            if subject_lat and subject_lon and "lat" in record and "lon" in record:
                distance = haversine(subject_lat, subject_lon, record["lat"], record["lon"])
                # Radius filter
                if distance > radius_miles:
                    continue

            # Compute price_per_sqft if not present
            sqft = record.get("sqft", 0)
            sale_price = record.get("sale_price", 0)
            price_per_sqft = record.get("price_per_sqft", 0)
            if price_per_sqft == 0 and sqft > 0:
                price_per_sqft = round(sale_price / sqft, 2)

            comp = CompSale(
                address=record.get("address", ""),
                sale_date=record.get("sale_date", ""),
                sale_price=sale_price,
                sqft=sqft,
                beds=record.get("beds", 0),
                baths=record.get("baths", 0),
                lot_sqft=record.get("lot_sqft", 0),
                year_built=record.get("year_built", 0),
                condition=record.get("condition", "average"),
                distance_miles=distance,
                price_per_sqft=price_per_sqft,
            )
            comps.append(comp)

        # Sort by relevance: prefer comps similar in sqft to target, then by recency
        comps.sort(key=lambda c: (
            abs(c.sqft - sqft_target),  # sqft similarity
            -date.fromisoformat(c.sale_date).toordinal(),  # most recent first (negative for descending)
        ))

        return comps[:count]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd C:/Users/tfalcon/co-op && python -m pytest tests/data-pipeline/test_real_comp_loader.py -v`
Expected: PASS — all 5 tests pass

- [ ] **Step 5: Commit**

```bash
git add tools/data-pipeline/loaders/real_comp_loader.py tests/data-pipeline/test_real_comp_loader.py
git commit -m "feat(data-pipeline): add RealCompLoader replacing SyntheticMLSGenerator"
```

---

### Task 10: AssessorLoader (replaces MultnomahAssessor stub)

**Files:**
- Create: `tools/data-pipeline/loaders/assessor_loader.py`
- Create: `tests/data-pipeline/test_assessor_loader.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/data-pipeline/test_assessor_loader.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'data-pipeline'))

import json
from loaders.assessor_loader import AssessorLoader, fuzzy_address_match

def _write_sample_assessor(tmp_path):
    assessor_dir = tmp_path / "multnomah-by-neighborhood"
    assessor_dir.mkdir(parents=True)
    records = [
        {"property_id": "R123456", "address": "123 SE FOSTER RD",
         "owner_name": "SMITH JOHN", "assessed_value": 320000, "market_value": 385000,
         "tax_year": 2025, "annual_tax": 4200.0, "lot_sqft": 5000,
         "year_built": 1952, "zoning": "R5", "legal_description": "LOT 1 BLK 2"},
        {"property_id": "R789012", "address": "456 SE 92ND AVE",
         "owner_name": "DOE JANE", "assessed_value": 280000, "market_value": 330000,
         "tax_year": 2025, "annual_tax": 3600.0, "lot_sqft": 4500,
         "year_built": 1948, "zoning": "R5", "legal_description": "LOT 5 BLK 8"},
    ]
    (assessor_dir / "lents.json").write_text(json.dumps(records))
    return tmp_path

def test_fuzzy_address_match_exact():
    assert fuzzy_address_match("123 SE FOSTER RD", "123 SE Foster Rd") is True

def test_fuzzy_address_match_with_suffix():
    assert fuzzy_address_match("123 SE FOSTER RD", "123 SE Foster Road") is True

def test_fuzzy_address_match_with_city():
    assert fuzzy_address_match("123 SE FOSTER RD", "123 SE Foster Rd, Portland, OR") is True

def test_fuzzy_address_match_mismatch():
    assert fuzzy_address_match("123 SE FOSTER RD", "456 NE CULLY BLVD") is False

def test_loader_lookup_finds_record(tmp_path):
    assessor_dir = _write_sample_assessor(tmp_path)
    loader = AssessorLoader(assessor_dir=assessor_dir)
    result = loader.lookup("123 SE Foster Rd, Portland, OR")
    assert result is not None
    assert result.property_id == "R123456"
    assert result.assessed_value == 320000
    assert result.zoning == "R5"

def test_loader_lookup_returns_none_for_unknown(tmp_path):
    assessor_dir = _write_sample_assessor(tmp_path)
    loader = AssessorLoader(assessor_dir=assessor_dir)
    result = loader.lookup("999 NW NONEXISTENT ST")
    assert result is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd C:/Users/tfalcon/co-op && python -m pytest tests/data-pipeline/test_assessor_loader.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: Implement AssessorLoader**

```python
# tools/data-pipeline/loaders/assessor_loader.py
"""AssessorLoader — drop-in replacement for MultnomahAssessor stub.

Reads real assessor data from data/assessor/multnomah-by-neighborhood/*.json.
"""

import json
import logging
import re
from pathlib import Path
from typing import Optional

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "comp-analyzer"))
from data_sources import AssessorRecord

from config import ASSESSOR_BY_NEIGHBORHOOD_DIR, NEIGHBORHOODS

logger = logging.getLogger(__name__)

# Street suffix normalization
_SUFFIX_MAP = {
    "ROAD": "RD", "STREET": "ST", "AVENUE": "AVE", "BOULEVARD": "BLVD",
    "DRIVE": "DR", "LANE": "LN", "COURT": "CT", "PLACE": "PL",
    "CIRCLE": "CIR", "TERRACE": "TER", "WAY": "WAY",
}

# Directional normalization
_DIR_MAP = {
    "NORTH": "N", "SOUTH": "S", "EAST": "E", "WEST": "W",
    "NORTHEAST": "NE", "NORTHWEST": "NW", "SOUTHEAST": "SE", "SOUTHWEST": "SW",
}


def _normalize_for_match(address: str) -> str:
    """Normalize an address for fuzzy matching."""
    addr = address.upper().strip()
    # Remove city, state, zip
    addr = re.sub(r',\s*(PORTLAND|OR|OREGON).*$', '', addr)
    # Expand/normalize suffixes
    for full, abbr in _SUFFIX_MAP.items():
        addr = re.sub(rf'\b{full}\b', abbr, addr)
    # Normalize directionals
    for full, abbr in _DIR_MAP.items():
        addr = re.sub(rf'\b{full}\b', abbr, addr)
    # Remove unit/apt
    addr = re.sub(r'\s*(UNIT|APT|STE|SUITE|#)\s*\S+', '', addr)
    # Collapse whitespace
    addr = re.sub(r'\s+', ' ', addr).strip()
    return addr


def fuzzy_address_match(assessor_addr: str, query_addr: str) -> bool:
    """Check if two addresses match after normalization."""
    return _normalize_for_match(assessor_addr) == _normalize_for_match(query_addr)


class AssessorLoader:
    """Load assessor records from local JSON files.

    Drop-in replacement for MultnomahAssessor stub.
    """

    def __init__(self, assessor_dir: Optional[Path] = None):
        self.assessor_dir = assessor_dir or ASSESSOR_BY_NEIGHBORHOOD_DIR
        self._cache: Optional[list[dict]] = None

    def _load_all(self) -> list[dict]:
        """Load all assessor records from all neighborhood files."""
        if self._cache is not None:
            return self._cache

        records = []
        by_hood_dir = self.assessor_dir / "multnomah-by-neighborhood"
        if not by_hood_dir.exists():
            # Try the assessor_dir itself (it might already be the by-neighborhood dir)
            by_hood_dir = self.assessor_dir
            if not by_hood_dir.exists():
                logger.warning("Assessor data directory not found: %s", self.assessor_dir)
                return []

        for slug in NEIGHBORHOODS:
            hood_file = by_hood_dir / f"{slug}.json"
            if hood_file.exists():
                with open(hood_file) as f:
                    hood_records = json.load(f)
                records.extend(hood_records)

        self._cache = records
        logger.info("Loaded %d assessor records", len(records))
        return records

    def lookup(self, address: str) -> Optional[AssessorRecord]:
        """Look up an assessor record by address with fuzzy matching."""
        records = self._load_all()

        for record in records:
            if fuzzy_address_match(record.get("address", ""), address):
                return AssessorRecord(
                    property_id=record.get("property_id", ""),
                    address=record.get("address", ""),
                    owner_name=record.get("owner_name", "[REDACTED]"),
                    assessed_value=int(record.get("assessed_value", 0)),
                    market_value=int(record.get("market_value", 0)),
                    tax_year=int(record.get("tax_year", 0)),
                    annual_tax=float(record.get("annual_tax", 0)),
                    lot_sqft=int(record.get("lot_sqft", 0)),
                    year_built=int(record.get("year_built", 0)),
                    zoning=record.get("zoning", ""),
                    legal_description=record.get("legal_description", ""),
                )

        return None
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd C:/Users/tfalcon/co-op && python -m pytest tests/data-pipeline/test_assessor_loader.py -v`
Expected: PASS — all 6 tests pass

- [ ] **Step 5: Commit**

```bash
git add tools/data-pipeline/loaders/assessor_loader.py tests/data-pipeline/test_assessor_loader.py
git commit -m "feat(data-pipeline): add AssessorLoader replacing MultnomahAssessor stub"
```

---

### Task 11: PortlandMapsLookup loader (replaces stub)

**Files:**
- Create: `tools/data-pipeline/loaders/portlandmaps_lookup.py`
- Create: `tests/data-pipeline/test_portlandmaps_lookup.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/data-pipeline/test_portlandmaps_lookup.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'data-pipeline'))

import json
from loaders.portlandmaps_lookup import PortlandMapsLookupLoader

def _write_sample_cache(tmp_path):
    cache_dir = tmp_path / "portlandmaps"
    cache_dir.mkdir()
    cached = {
        "address": "123 SE Foster Rd",
        "state_id": "1S2E15AC 01200",
        "zoning": "R5",
        "comprehensive_plan": "Single-Dwelling Residential",
        "flood_zone": "X",
        "seismic_zone": "moderate",
        "permits_last_5yr": 3,
        "open_permits": 1,
        "liens": 1,
        "lien_total": 5000.00,
        "neighborhood_association": "Foster-Powell NA",
    }
    slug = "123-se-foster-rd"
    (cache_dir / f"{slug}.json").write_text(json.dumps(cached))
    return cache_dir

def test_lookup_from_cache(tmp_path):
    cache_dir = _write_sample_cache(tmp_path)
    loader = PortlandMapsLookupLoader(cache_dir=cache_dir)
    result = loader.lookup("123 SE Foster Rd")
    assert result is not None
    assert result.zoning == "R5"
    assert result.permits_last_5yr == 3
    assert result.liens == 1
    assert result.lien_total == 5000.00

def test_lookup_returns_none_for_uncached(tmp_path):
    cache_dir = tmp_path / "portlandmaps"
    cache_dir.mkdir()
    loader = PortlandMapsLookupLoader(cache_dir=cache_dir, fetch_on_miss=False)
    result = loader.lookup("999 NW NONEXISTENT ST")
    assert result is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd C:/Users/tfalcon/co-op && python -m pytest tests/data-pipeline/test_portlandmaps_lookup.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: Implement PortlandMapsLookup loader**

```python
# tools/data-pipeline/loaders/portlandmaps_lookup.py
"""PortlandMapsLookupLoader — drop-in replacement for PortlandMapsLookup stub.

Reads cached data from data/portlandmaps/{slug}.json, falls back to live API.
"""

import json
import logging
import re
from pathlib import Path
from typing import Optional

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "comp-analyzer"))
from data_sources import PortlandMapsInfo

from config import PORTLANDMAPS_DIR

logger = logging.getLogger(__name__)


def _address_to_slug(address: str) -> str:
    """Convert address to filesystem-safe slug."""
    slug = address.lower().strip()
    # Remove city/state/zip
    slug = re.sub(r',\s*portland.*$', '', slug)
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug


class PortlandMapsLookupLoader:
    """Load PortlandMaps data from cache, optionally fetching on miss.

    Drop-in replacement for PortlandMapsLookup stub.
    """

    def __init__(self, cache_dir: Optional[Path] = None, fetch_on_miss: bool = True):
        self.cache_dir = cache_dir or PORTLANDMAPS_DIR
        self.fetch_on_miss = fetch_on_miss
        self._fetcher = None

    def _get_fetcher(self):
        """Lazy-load the PortlandMapsFetcher for live API calls."""
        if self._fetcher is None:
            from fetchers.portlandmaps import PortlandMapsFetcher
            self._fetcher = PortlandMapsFetcher(cache_dir=self.cache_dir)
        return self._fetcher

    def lookup(self, address: str) -> Optional[PortlandMapsInfo]:
        """Look up PortlandMaps info for an address.

        Checks local cache first, then optionally hits the live API.
        """
        slug = _address_to_slug(address)
        cache_file = self.cache_dir / f"{slug}.json"

        if cache_file.exists():
            with open(cache_file) as f:
                data = json.load(f)
            return PortlandMapsInfo(
                address=data.get("address", address),
                state_id=data.get("state_id", ""),
                zoning=data.get("zoning", ""),
                comprehensive_plan=data.get("comprehensive_plan", ""),
                flood_zone=data.get("flood_zone", ""),
                seismic_zone=data.get("seismic_zone", ""),
                permits_last_5yr=int(data.get("permits_last_5yr", 0)),
                open_permits=int(data.get("open_permits", 0)),
                liens=int(data.get("liens", 0)),
                lien_total=float(data.get("lien_total", 0)),
                neighborhood_association=data.get("neighborhood_association", ""),
            )

        if not self.fetch_on_miss:
            return None

        # Try live API
        fetcher = self._get_fetcher()
        data = fetcher.fetch_property(address)
        if data is None:
            return None

        return PortlandMapsInfo(
            address=data.get("address", address),
            state_id=data.get("state_id", ""),
            zoning=data.get("zoning", ""),
            comprehensive_plan=data.get("comprehensive_plan", ""),
            flood_zone=data.get("flood_zone", ""),
            seismic_zone=data.get("seismic_zone", ""),
            permits_last_5yr=int(data.get("permits_last_5yr", 0)),
            open_permits=int(data.get("open_permits", 0)),
            liens=int(data.get("liens", 0)),
            lien_total=float(data.get("lien_total", 0)),
            neighborhood_association=data.get("neighborhood_association", ""),
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd C:/Users/tfalcon/co-op && python -m pytest tests/data-pipeline/test_portlandmaps_lookup.py -v`
Expected: PASS — all 2 tests pass

- [ ] **Step 5: Commit**

```bash
git add tools/data-pipeline/loaders/portlandmaps_lookup.py tests/data-pipeline/test_portlandmaps_lookup.py
git commit -m "feat(data-pipeline): add PortlandMapsLookup loader replacing stub"
```

---

### Task 12: Integration — update data_sources.py

**Files:**
- Modify: `tools/comp-analyzer/data_sources.py:1-12` (module docstring)
- Modify: `tools/comp-analyzer/data_sources.py:170-306` (SyntheticMLSGenerator usage)
- Modify: `tools/comp-analyzer/data_sources.py:333-367` (MultnomahAssessor)
- Modify: `tools/comp-analyzer/data_sources.py:390-435` (PortlandMapsLookup)
- Modify: `tools/comp-analyzer/comp_analyzer.py:38-43` (imports)
- Modify: `tools/comp-analyzer/comp_analyzer.py:244-267` (run_analysis)
- Create: `tests/data-pipeline/test_integration.py`

- [ ] **Step 1: Write the failing integration test**

```python
# tests/data-pipeline/test_integration.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'data-pipeline'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'comp-analyzer'))

import json
from pathlib import Path

def _setup_real_data(tmp_path):
    """Create minimal real data files for integration testing."""
    # Comp sales
    comps_dir = tmp_path / "comp-sales"
    comps_dir.mkdir()
    comps = [
        {"address": "123 SE Foster Rd, Portland, OR", "sale_date": "2026-03-01",
         "sale_price": 350000, "sqft": 1100, "beds": 3, "baths": 1.5,
         "lot_sqft": 5000, "year_built": 1952, "condition": "average",
         "neighborhood": "lents", "price_per_sqft": 318.18},
        {"address": "456 SE 92nd Ave, Portland, OR", "sale_date": "2026-02-15",
         "sale_price": 310000, "sqft": 1000, "beds": 2, "baths": 1.0,
         "lot_sqft": 4500, "year_built": 1948, "condition": "fair",
         "neighborhood": "lents", "price_per_sqft": 310.00},
        {"address": "789 SE Harold St, Portland, OR", "sale_date": "2026-01-10",
         "sale_price": 380000, "sqft": 1200, "beds": 3, "baths": 1.5,
         "lot_sqft": 5500, "year_built": 1955, "condition": "good",
         "neighborhood": "lents", "price_per_sqft": 316.67},
        {"address": "321 SE Holgate Blvd, Portland, OR", "sale_date": "2025-12-01",
         "sale_price": 340000, "sqft": 1150, "beds": 3, "baths": 1.0,
         "lot_sqft": 5200, "year_built": 1950, "condition": "average",
         "neighborhood": "lents", "price_per_sqft": 295.65},
        {"address": "654 SE Flavel St, Portland, OR", "sale_date": "2025-11-15",
         "sale_price": 295000, "sqft": 950, "beds": 2, "baths": 1.0,
         "lot_sqft": 4800, "year_built": 1945, "condition": "fair",
         "neighborhood": "lents", "price_per_sqft": 310.53},
    ]
    (comps_dir / "lents-comps.json").write_text(json.dumps(comps))

    # Assessor
    assessor_dir = tmp_path / "assessor" / "multnomah-by-neighborhood"
    assessor_dir.mkdir(parents=True)
    assessor = [
        {"property_id": "R100", "address": "5432 SE 92ND AVE",
         "owner_name": "[REDACTED]", "assessed_value": 300000, "market_value": 360000,
         "tax_year": 2025, "annual_tax": 4000.0, "lot_sqft": 5000,
         "year_built": 1952, "zoning": "R5", "legal_description": "LOT 10 BLK 3"},
    ]
    (assessor_dir / "lents.json").write_text(json.dumps(assessor))

    # PortlandMaps cache
    pm_dir = tmp_path / "portlandmaps"
    pm_dir.mkdir()
    pm = {
        "address": "5432 SE 92nd Ave",
        "state_id": "1S2E15AC 01200", "zoning": "R5",
        "comprehensive_plan": "Single-Dwelling Residential",
        "flood_zone": "X", "seismic_zone": "moderate",
        "permits_last_5yr": 2, "open_permits": 0,
        "liens": 0, "lien_total": 0.0,
        "neighborhood_association": "Lents NA",
    }
    (pm_dir / "5432-se-92nd-ave.json").write_text(json.dumps(pm))

    return tmp_path

def test_data_sources_real_mode(tmp_path, monkeypatch):
    data_dir = _setup_real_data(tmp_path)

    # Patch config paths to use tmp_path
    import config
    monkeypatch.setattr(config, "COMP_SALES_DIR", data_dir / "comp-sales")
    monkeypatch.setattr(config, "ASSESSOR_BY_NEIGHBORHOOD_DIR", data_dir / "assessor" / "multnomah-by-neighborhood")
    monkeypatch.setattr(config, "PORTLANDMAPS_DIR", data_dir / "portlandmaps")

    from data_sources import get_comp_loader, get_assessor, get_portlandmaps

    # Test comp loader
    loader = get_comp_loader()
    comps = loader.load_comps("lents", count=3)
    assert len(comps) == 3
    assert all(hasattr(c, "sale_price") for c in comps)

    # Test assessor
    assessor = get_assessor()
    record = assessor.lookup("5432 SE 92nd Ave, Portland, OR")
    assert record is not None
    assert record.zoning == "R5"

    # Test portlandmaps
    pm = get_portlandmaps()
    info = pm.lookup("5432 SE 92nd Ave")
    assert info is not None
    assert info.zoning == "R5"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd C:/Users/tfalcon/co-op && python -m pytest tests/data-pipeline/test_integration.py -v`
Expected: FAIL — get_comp_loader not found

- [ ] **Step 3: Update data_sources.py with real data support**

Add the following to the **end** of `tools/comp-analyzer/data_sources.py` (after the existing `PortlandMapsLookup` class, around line 436):

```python
# ---------------------------------------------------------------------------
# Real data integration — factory functions
# ---------------------------------------------------------------------------

import sys as _sys
from pathlib import Path as _Path

# Add data-pipeline to path for loader imports
_pipeline_path = str(_Path(__file__).resolve().parent.parent / "data-pipeline")
if _pipeline_path not in _sys.path:
    _sys.path.insert(0, _pipeline_path)

_DATA_DIR = _Path(__file__).resolve().parent.parent.parent / "data"
_COMP_SALES_DIR = _DATA_DIR / "comp-sales"


def _has_real_data() -> bool:
    """Check if real comp data files exist."""
    if not _COMP_SALES_DIR.exists():
        return False
    return any(_COMP_SALES_DIR.glob("*-comps.json"))


def get_comp_loader():
    """Return RealCompLoader if real data exists, else SyntheticMLSGenerator."""
    if _has_real_data():
        from loaders.real_comp_loader import RealCompLoader
        return RealCompLoader()
    return SyntheticMLSGenerator()


def get_assessor():
    """Return AssessorLoader if real data exists, else MultnomahAssessor stub."""
    assessor_dir = _DATA_DIR / "assessor" / "multnomah-by-neighborhood"
    if assessor_dir.exists() and any(assessor_dir.glob("*.json")):
        from loaders.assessor_loader import AssessorLoader
        return AssessorLoader()
    return MultnomahAssessor()


def get_portlandmaps():
    """Return PortlandMapsLookupLoader if cache exists, else stub."""
    pm_dir = _DATA_DIR / "portlandmaps"
    if pm_dir.exists():
        from loaders.portlandmaps_lookup import PortlandMapsLookupLoader
        return PortlandMapsLookupLoader()
    return PortlandMapsLookup()
```

- [ ] **Step 4: Update comp_analyzer.py to use factory functions**

Replace the import block at `tools/comp-analyzer/comp_analyzer.py:38-43`:

```python
from data_sources import (
    CompSale,
    get_comp_loader,
    get_assessor,
    get_portlandmaps,
)
```

Replace `run_analysis` at `tools/comp-analyzer/comp_analyzer.py:244-267` — change lines 258-267 (the generator and assessor/portmaps calls):

```python
    loader = get_comp_loader()
    # Use load_comps if RealCompLoader, generate_comps if Synthetic
    if hasattr(loader, 'load_comps'):
        raw_comps = loader.load_comps(
            neighborhood=subject.neighborhood,
            sqft_target=subject.sqft,
            beds=subject.beds,
            baths=subject.baths,
            radius_miles=radius_miles,
            months_back=12,
            count=generate_count,
        )
    else:
        raw_comps = loader.generate_comps(
            neighborhood=subject.neighborhood,
            sqft_target=subject.sqft,
            beds=subject.beds,
            baths=subject.baths,
            radius_miles=radius_miles,
            months_back=12,
            count=generate_count,
        )
```

And replace lines 289-290 (assessor/portmaps lookups):

```python
    assessor = get_assessor().lookup(subject.address)
    portmaps = get_portlandmaps().lookup(subject.address)
```

- [ ] **Step 5: Run integration test**

Run: `cd C:/Users/tfalcon/co-op && python -m pytest tests/data-pipeline/test_integration.py -v`
Expected: PASS

- [ ] **Step 6: Run existing comp_analyzer tests (if any) to verify no regression**

Run: `cd C:/Users/tfalcon/co-op && python -m pytest tests/ -v --tb=short 2>/dev/null || python -c "from tools.comp_analyzer import comp_analyzer; print('import OK')"`
Expected: No import errors, no regressions

- [ ] **Step 7: Commit**

```bash
git add tools/comp-analyzer/data_sources.py tools/comp-analyzer/comp_analyzer.py tests/data-pipeline/test_integration.py
git commit -m "feat(data-pipeline): integrate real data loaders into comp_analyzer"
```

---

### Task 13: CLI orchestrator

**Files:**
- Create: `tools/data-pipeline/pipeline.py`
- Create: `tests/data-pipeline/test_pipeline.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/data-pipeline/test_pipeline.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'data-pipeline'))

from pipeline import build_parser, get_execution_order

def test_parser_accepts_all_flag():
    parser = build_parser()
    args = parser.parse_args(["--all"])
    assert args.all is True

def test_parser_accepts_source_flag():
    parser = build_parser()
    args = parser.parse_args(["--source", "redfin"])
    assert args.source == "redfin"

def test_parser_accepts_validate_flag():
    parser = build_parser()
    args = parser.parse_args(["--validate"])
    assert args.validate is True

def test_parser_accepts_geocode_flag():
    parser = build_parser()
    args = parser.parse_args(["--geocode"])
    assert args.geocode is True

def test_execution_order():
    order = get_execution_order()
    assert order.index("assessor") < order.index("redfin")
    assert order.index("redfin") < order.index("portlandmaps")
    assert order.index("portlandmaps") < order.index("distressed")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd C:/Users/tfalcon/co-op && python -m pytest tests/data-pipeline/test_pipeline.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: Implement the orchestrator**

```python
#!/usr/bin/env python3
# tools/data-pipeline/pipeline.py
"""CLI orchestrator for the Portland Housing Co-op data pipeline.

Usage:
    python pipeline.py --all                    # Full refresh
    python pipeline.py --source redfin          # Redfin comps only
    python pipeline.py --source assessor        # Assessor bulk data
    python pipeline.py --source portlandmaps    # PortlandMaps (needs addresses)
    python pipeline.py --source police          # Crime data
    python pipeline.py --source distressed      # Distressed aggregation
    python pipeline.py --geocode                # Geocode all comps
    python pipeline.py --validate               # Schema validation only
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from config import COMP_SALES_DIR, ASSESSOR_DIR, ASSESSOR_BY_NEIGHBORHOOD_DIR, PORTLANDMAPS_DIR, NEIGHBORHOODS

logger = logging.getLogger("data-pipeline")

EXECUTION_ORDER = ["assessor", "redfin", "geocode", "portlandmaps", "police", "distressed"]


def get_execution_order() -> list[str]:
    """Return the dependency-ordered execution sequence."""
    return list(EXECUTION_ORDER)


def run_assessor() -> dict:
    """Run the assessor fetcher."""
    from fetchers.assessor import AssessorFetcher
    fetcher = AssessorFetcher()
    return fetcher.fetch_all()


def run_redfin() -> dict:
    """Run the Redfin fetcher."""
    from fetchers.redfin import RedfinFetcher
    fetcher = RedfinFetcher()
    return fetcher.fetch_all()


def run_geocode() -> dict:
    """Geocode all comp records that don't have lat/lon."""
    from geocoding import geocode
    import time
    from config import RATE_LIMITS

    summary = {}
    delay = RATE_LIMITS.get("census_geocoder", 1.0)

    for slug in NEIGHBORHOODS:
        comps_file = COMP_SALES_DIR / f"{slug}-comps.json"
        if not comps_file.exists():
            summary[slug] = 0
            continue

        with open(comps_file) as f:
            comps = json.load(f)

        geocoded = 0
        for comp in comps:
            if "lat" in comp and "lon" in comp and comp["lat"] and comp["lon"]:
                continue  # Already geocoded

            result = geocode(comp.get("address", ""))
            if result:
                comp["lat"] = result[0]
                comp["lon"] = result[1]
                geocoded += 1
                time.sleep(delay)

        with open(comps_file, "w") as f:
            json.dump(comps, f, indent=2)

        summary[slug] = geocoded
        logger.info("Geocoded %d/%d comps for %s", geocoded, len(comps), slug)

    return summary


def run_portlandmaps(addresses: list[str] = None) -> dict:
    """Run the PortlandMaps fetcher."""
    from fetchers.portlandmaps import PortlandMapsFetcher
    fetcher = PortlandMapsFetcher()

    if addresses:
        results = fetcher.fetch_addresses(addresses)
        return {"fetched": sum(1 for v in results.values() if v is not None)}

    # Default: fetch for all addresses in comp data
    all_addresses = []
    for slug in NEIGHBORHOODS:
        comps_file = COMP_SALES_DIR / f"{slug}-comps.json"
        if comps_file.exists():
            with open(comps_file) as f:
                comps = json.load(f)
            all_addresses.extend(c.get("address", "") for c in comps if c.get("address"))

    if not all_addresses:
        logger.warning("No addresses found for PortlandMaps lookup")
        return {"fetched": 0}

    results = fetcher.fetch_addresses(all_addresses)
    return {"fetched": sum(1 for v in results.values() if v is not None)}


def run_police() -> dict:
    """Run the Portland Police crime data fetcher."""
    from fetchers.portland_police import PoliceFetcher
    fetcher = PoliceFetcher()
    return fetcher.fetch_all()


def run_distressed() -> dict:
    """Run the distressed listing aggregator."""
    from fetchers.distressed import DistressedAggregator

    # Load assessor data
    assessor_records = []
    if ASSESSOR_BY_NEIGHBORHOOD_DIR.exists():
        for slug in NEIGHBORHOODS:
            hood_file = ASSESSOR_BY_NEIGHBORHOOD_DIR / f"{slug}.json"
            if hood_file.exists():
                with open(hood_file) as f:
                    assessor_records.extend(json.load(f))

    # Load portlandmaps data
    portlandmaps_data = {}
    if PORTLANDMAPS_DIR.exists():
        for pm_file in PORTLANDMAPS_DIR.glob("*.json"):
            with open(pm_file) as f:
                data = json.load(f)
            address = data.get("address", "")
            if address:
                portlandmaps_data[address] = data

    agg = DistressedAggregator()
    return agg.aggregate(assessor_records, portlandmaps_data)


def run_validate() -> dict:
    """Validate all data files against expected schemas."""
    from normalizer import validate_comp_record

    errors = {}
    total_valid = 0
    total_invalid = 0

    for slug in NEIGHBORHOODS:
        comps_file = COMP_SALES_DIR / f"{slug}-comps.json"
        if not comps_file.exists():
            continue

        with open(comps_file) as f:
            comps = json.load(f)

        slug_errors = []
        for i, comp in enumerate(comps):
            errs = validate_comp_record(comp)
            if errs:
                slug_errors.append({"index": i, "address": comp.get("address", "?"), "errors": errs})
                total_invalid += 1
            else:
                total_valid += 1

        if slug_errors:
            errors[slug] = slug_errors

    return {"valid": total_valid, "invalid": total_invalid, "errors": errors}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pipeline",
        description="Portland Housing Co-op real data pipeline orchestrator.",
    )
    parser.add_argument("--all", action="store_true", help="Run all fetchers in dependency order")
    parser.add_argument("--source", choices=["redfin", "assessor", "portlandmaps", "police", "distressed"],
                        help="Run a specific source fetcher")
    parser.add_argument("--geocode", action="store_true", help="Geocode all comp records")
    parser.add_argument("--validate", action="store_true", help="Validate all data files")
    parser.add_argument("--addresses", help="JSON file with addresses for portlandmaps lookup")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable debug logging")
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(name)s %(levelname)s %(message)s")

    if not any([args.all, args.source, args.geocode, args.validate]):
        parser.print_help()
        return 1

    results = {}

    if args.all:
        order = get_execution_order()
        for step in order:
            logger.info("=== Running: %s ===", step)
            try:
                if step == "assessor":
                    results[step] = run_assessor()
                elif step == "redfin":
                    results[step] = run_redfin()
                elif step == "geocode":
                    results[step] = run_geocode()
                elif step == "portlandmaps":
                    results[step] = run_portlandmaps()
                elif step == "police":
                    results[step] = run_police()
                elif step == "distressed":
                    results[step] = run_distressed()
            except Exception as e:
                logger.error("Step %s failed: %s", step, e)
                results[step] = {"error": str(e)}

        # Validate at the end
        logger.info("=== Running: validate ===")
        results["validate"] = run_validate()

    elif args.source:
        source_map = {
            "redfin": run_redfin,
            "assessor": run_assessor,
            "portlandmaps": lambda: run_portlandmaps(
                json.loads(Path(args.addresses).read_text()) if args.addresses else None
            ),
            "police": run_police,
            "distressed": run_distressed,
        }
        results[args.source] = source_map[args.source]()

    elif args.geocode:
        results["geocode"] = run_geocode()

    elif args.validate:
        results["validate"] = run_validate()

    # Print summary
    print("\n" + "=" * 60)
    print("Pipeline Results:")
    print("=" * 60)
    print(json.dumps(results, indent=2, default=str))

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd C:/Users/tfalcon/co-op && python -m pytest tests/data-pipeline/test_pipeline.py -v`
Expected: PASS — all 5 tests pass

- [ ] **Step 5: Commit**

```bash
git add tools/data-pipeline/pipeline.py tests/data-pipeline/test_pipeline.py
git commit -m "feat(data-pipeline): add CLI orchestrator with dependency ordering"
```

---

### Task 14: Create data directories and run full test suite

**Files:**
- Create: `data/comp-sales/.gitkeep`
- Create: `data/assessor/.gitkeep`
- Create: `data/assessor/multnomah-by-neighborhood/.gitkeep`
- Create: `data/portlandmaps/.gitkeep`

- [ ] **Step 1: Create data directories**

```bash
mkdir -p data/comp-sales data/assessor/multnomah-by-neighborhood data/portlandmaps
touch data/comp-sales/.gitkeep data/assessor/.gitkeep data/assessor/multnomah-by-neighborhood/.gitkeep data/portlandmaps/.gitkeep
```

- [ ] **Step 2: Install dependencies**

```bash
pip install requests pandas
```

- [ ] **Step 3: Run full test suite**

Run: `cd C:/Users/tfalcon/co-op && python -m pytest tests/data-pipeline/ -v --tb=short`
Expected: All tests pass (approximately 40+ tests across all modules)

- [ ] **Step 4: Run pipeline validate on existing data**

Run: `cd C:/Users/tfalcon/co-op && python tools/data-pipeline/pipeline.py --validate`
Expected: Runs without error (may report 0 files if no real data yet)

- [ ] **Step 5: Commit**

```bash
git add data/comp-sales/.gitkeep data/assessor/.gitkeep data/assessor/multnomah-by-neighborhood/.gitkeep data/portlandmaps/.gitkeep
git commit -m "chore: create data directories for pipeline output"
```

---
