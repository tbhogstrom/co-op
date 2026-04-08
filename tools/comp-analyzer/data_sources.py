"""
data_sources.py — Data fetching layer for the Portland comp analyzer.

Provides:
  - SyntheticMLSGenerator: generates realistic MLS-style comparable sales
    calibrated to actual Portland neighborhood price bands.
  - MultnomahAssessor: stub for Multnomah County assessor public records.
  - PortlandMapsLookup: stub for PortlandMaps.com property info.

No external dependencies — uses only the Python 3.9+ standard library.
"""

from __future__ import annotations

import hashlib
import math
import random
from dataclasses import dataclass, field, asdict
from datetime import date, timedelta
from typing import List, Optional, Dict, Tuple

# ---------------------------------------------------------------------------
# Portland neighborhood price calibration
# Ranges are for *typical* 2-3 BR houses in fair-to-good condition, as of
# late-2025 / early-2026.  Low end ≈ distressed / small; high end ≈ updated
# / larger.  Square-footage bands are similarly calibrated.
# ---------------------------------------------------------------------------

NEIGHBORHOOD_PROFILES: Dict[str, Dict] = {
    "lents": {
        "price_range": (280_000, 420_000),
        "sqft_range": (900, 1400),
        "lot_sqft_range": (4000, 6500),
        "year_built_range": (1920, 1965),
        "street_prefixes": ["SE"],
        "street_names": [
            "92nd Ave", "90th Ave", "88th Ave", "91st Ave", "Foster Rd",
            "Woodstock Blvd", "Harold St", "Holgate Blvd", "Ramona St",
            "Flavel St", "93rd Ave", "Knight St", "Steele St",
        ],
    },
    "cully": {
        "price_range": (300_000, 450_000),
        "sqft_range": (1000, 1500),
        "lot_sqft_range": (4500, 7500),
        "year_built_range": (1925, 1960),
        "street_prefixes": ["NE"],
        "street_names": [
            "Cully Blvd", "Prescott St", "Killingsworth St", "57th Ave",
            "60th Ave", "Emerson St", "Sumner St", "Simpson St",
            "Alberta St", "Ainsworth St",
        ],
    },
    "foster-powell": {
        "price_range": (350_000, 520_000),
        "sqft_range": (1000, 1600),
        "lot_sqft_range": (4000, 6000),
        "year_built_range": (1910, 1955),
        "street_prefixes": ["SE"],
        "street_names": [
            "Foster Rd", "Powell Blvd", "52nd Ave", "50th Ave", "Gladstone St",
            "Steele St", "Rhone St", "Reedway St", "Holgate Blvd",
            "48th Ave", "54th Ave",
        ],
    },
    "st. johns": {
        "price_range": (340_000, 500_000),
        "sqft_range": (1100, 1600),
        "lot_sqft_range": (4500, 7000),
        "year_built_range": (1905, 1950),
        "street_prefixes": ["N"],
        "street_names": [
            "Lombard St", "Burlington Ave", "Richmond Ave", "Syracuse St",
            "Charleston Ave", "Central St", "Fessenden St", "Ivanhoe St",
            "Jersey St", "Portsmouth Ave",
        ],
    },
    "woodstock": {
        "price_range": (380_000, 550_000),
        "sqft_range": (1100, 1700),
        "lot_sqft_range": (4500, 6500),
        "year_built_range": (1915, 1955),
        "street_prefixes": ["SE"],
        "street_names": [
            "Woodstock Blvd", "42nd Ave", "45th Ave", "41st Ave",
            "Martins St", "Reedway St", "Steele St", "Mitchell St",
            "Knight St", "Crystal Springs Blvd",
        ],
    },
    "montavilla": {
        "price_range": (320_000, 480_000),
        "sqft_range": (1000, 1500),
        "lot_sqft_range": (4000, 6500),
        "year_built_range": (1920, 1955),
        "street_prefixes": ["SE", "NE"],
        "street_names": [
            "Stark St", "Washington St", "80th Ave", "82nd Ave",
            "Burnside St", "Glisan St", "76th Ave", "78th Ave",
            "Morrison St", "Main St",
        ],
    },
    "parkrose": {
        "price_range": (260_000, 400_000),
        "sqft_range": (900, 1400),
        "lot_sqft_range": (5000, 8000),
        "year_built_range": (1940, 1970),
        "street_prefixes": ["NE"],
        "street_names": [
            "Sandy Blvd", "Shaver St", "Prescott St", "109th Ave",
            "111th Ave", "112th Ave", "Fremont St", "Beech St",
            "Sacramento St", "Marx St",
        ],
    },
}

# Canonical neighborhood key lookup (case-insensitive, dash-insensitive).
_NEIGHBORHOOD_ALIAS: Dict[str, str] = {}
for _key in NEIGHBORHOOD_PROFILES:
    _NEIGHBORHOOD_ALIAS[_key] = _key
    _NEIGHBORHOOD_ALIAS[_key.replace(" ", "")] = _key
    _NEIGHBORHOOD_ALIAS[_key.replace(".", "")] = _key
    _NEIGHBORHOOD_ALIAS[_key.replace("-", " ")] = _key


def _resolve_neighborhood(name: str) -> str:
    """Return the canonical neighborhood key, or raise ValueError."""
    normalized = name.strip().lower()
    if normalized in NEIGHBORHOOD_PROFILES:
        return normalized
    if normalized in _NEIGHBORHOOD_ALIAS:
        return _NEIGHBORHOOD_ALIAS[normalized]
    raise ValueError(
        f"Unknown neighborhood: {name!r}.  "
        f"Supported: {', '.join(sorted(NEIGHBORHOOD_PROFILES))}"
    )


# ---------------------------------------------------------------------------
# Comparable sale record
# ---------------------------------------------------------------------------

CONDITIONS = ["poor", "fair", "average", "good", "excellent"]
CONDITION_WEIGHTS = [0.08, 0.20, 0.40, 0.25, 0.07]  # distribution


@dataclass
class CompSale:
    """A single comparable sale record."""

    address: str
    sale_date: str  # ISO format YYYY-MM-DD
    sale_price: int
    sqft: int
    beds: int
    baths: float
    lot_sqft: int
    year_built: int
    condition: str  # poor / fair / average / good / excellent
    distance_miles: float
    price_per_sqft: float

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Synthetic MLS generator
# ---------------------------------------------------------------------------

class SyntheticMLSGenerator:
    """Generate realistic Portland MLS-style comparable sales.

    Data is deterministic for a given seed so results are reproducible.
    """

    def __init__(self, seed: Optional[int] = None) -> None:
        self._rng = random.Random(seed)

    # ----- public API -------------------------------------------------------

    def generate_comps(
        self,
        neighborhood: str,
        sqft_target: int = 1200,
        beds: int = 3,
        baths: float = 1.0,
        radius_miles: float = 0.5,
        months_back: int = 12,
        count: int = 10,
        reference_date: Optional[date] = None,
    ) -> List[CompSale]:
        """Return *count* synthetic comp sales near a target property.

        Parameters
        ----------
        neighborhood : str
            Portland neighborhood name (case-insensitive).
        sqft_target : int
            Target square footage — comps will cluster around this value.
        beds : int
            Target bedroom count.
        baths : float
            Target bathroom count (e.g. 1.0, 1.5, 2.0).
        radius_miles : float
            Maximum distance for generated comps.
        months_back : int
            How far back to generate sale dates.
        count : int
            Number of comps to generate.
        reference_date : date | None
            Anchor date for sale-date generation; defaults to today.
        """
        key = _resolve_neighborhood(neighborhood)
        profile = NEIGHBORHOOD_PROFILES[key]
        ref = reference_date or date.today()

        comps: List[CompSale] = []
        for _ in range(count):
            comp = self._make_one(profile, sqft_target, beds, baths,
                                  radius_miles, months_back, ref)
            comps.append(comp)
        return comps

    # ----- internals --------------------------------------------------------

    def _make_one(
        self,
        profile: dict,
        sqft_target: int,
        beds: int,
        baths: float,
        radius_miles: float,
        months_back: int,
        ref: date,
    ) -> CompSale:
        rng = self._rng

        # Square footage: gaussian around target, clipped to profile range
        lo_sqft, hi_sqft = profile["sqft_range"]
        sqft = int(rng.gauss(sqft_target, (hi_sqft - lo_sqft) * 0.20))
        sqft = max(lo_sqft, min(hi_sqft, sqft))

        # Bedrooms: mostly same as target, occasionally +-1
        bed_delta = rng.choices([-1, 0, 0, 0, 1], k=1)[0]
        comp_beds = max(1, beds + bed_delta)

        # Bathrooms: target +- 0.5 sometimes
        bath_delta = rng.choices([-0.5, 0, 0, 0, 0.5], k=1)[0]
        comp_baths = max(1.0, baths + bath_delta)

        # Year built
        yb_lo, yb_hi = profile["year_built_range"]
        year_built = rng.randint(yb_lo, yb_hi)

        # Condition
        condition = rng.choices(CONDITIONS, weights=CONDITION_WEIGHTS, k=1)[0]

        # Lot sqft
        lot_lo, lot_hi = profile["lot_sqft_range"]
        lot_sqft = rng.randint(lot_lo, lot_hi)

        # Sale price — driven by per-sqft pricing calibrated to neighborhood
        price_lo, price_hi = profile["price_range"]
        base_ppsf = rng.uniform(price_lo / hi_sqft, price_hi / lo_sqft)

        # Adjust ppsf for condition
        condition_mult = {
            "poor": 0.82, "fair": 0.92, "average": 1.00,
            "good": 1.08, "excellent": 1.18,
        }[condition]
        ppsf = base_ppsf * condition_mult

        # Small random jitter (+/- 5%)
        ppsf *= rng.uniform(0.95, 1.05)

        sale_price = int(round(ppsf * sqft, -3))  # round to nearest $1000
        sale_price = max(price_lo - 30_000, min(price_hi + 40_000, sale_price))

        # Sale date
        days_back = rng.randint(14, months_back * 30)
        sale_date = ref - timedelta(days=days_back)

        # Distance
        distance = round(rng.uniform(0.05, radius_miles), 2)

        # Address
        prefix = rng.choice(profile["street_prefixes"])
        street = rng.choice(profile["street_names"])
        number = rng.randint(1000, 9999)
        address = f"{number} {prefix} {street}, Portland, OR"

        price_per_sqft = round(sale_price / sqft, 2)

        return CompSale(
            address=address,
            sale_date=sale_date.isoformat(),
            sale_price=sale_price,
            sqft=sqft,
            beds=comp_beds,
            baths=comp_baths,
            lot_sqft=lot_sqft,
            year_built=year_built,
            condition=condition,
            distance_miles=distance,
            price_per_sqft=price_per_sqft,
        )


# ---------------------------------------------------------------------------
# Real-data stubs (Multnomah County assessor, PortlandMaps)
# ---------------------------------------------------------------------------

@dataclass
class AssessorRecord:
    """Property tax & assessment data from Multnomah County."""

    property_id: str
    address: str
    owner_name: str
    assessed_value: int
    market_value: int
    tax_year: int
    annual_tax: float
    lot_sqft: int
    year_built: int
    zoning: str
    legal_description: str

    def to_dict(self) -> dict:
        return asdict(self)


class MultnomahAssessor:
    """Stub for Multnomah County assessor public-record lookups.

    In production this would scrape or query the county assessor's
    CAMA database.  For now it returns a synthetic record seeded from
    the address so results are deterministic.
    """

    BASE_URL = "https://multcoproptax.com"

    def lookup(self, address: str) -> AssessorRecord:
        """Return an assessor record for *address*."""
        # Deterministic seed from address
        h = int(hashlib.sha256(address.encode()).hexdigest(), 16)
        rng = random.Random(h)

        assessed = rng.randint(180_000, 420_000)
        market = int(assessed * rng.uniform(1.05, 1.35))
        lot = rng.randint(4000, 8000)
        year = rng.randint(1910, 1970)
        tax_rate = rng.uniform(0.011, 0.015)

        return AssessorRecord(
            property_id=f"R{rng.randint(100000, 999999)}",
            address=address,
            owner_name="[REDACTED — public record]",
            assessed_value=assessed,
            market_value=market,
            tax_year=2025,
            annual_tax=round(assessed * tax_rate, 2),
            lot_sqft=lot,
            year_built=year,
            zoning=rng.choice(["R5", "R7", "R10", "R2.5", "CM1"]),
            legal_description=f"LOT {rng.randint(1,30)} BLK {rng.randint(1,15)}",
        )


@dataclass
class PortlandMapsInfo:
    """Property information from PortlandMaps.com."""

    address: str
    state_id: str
    zoning: str
    comprehensive_plan: str
    flood_zone: str
    seismic_zone: str
    permits_last_5yr: int
    open_permits: int
    liens: int
    lien_total: float
    neighborhood_association: str

    def to_dict(self) -> dict:
        return asdict(self)


class PortlandMapsLookup:
    """Stub for PortlandMaps.com property information.

    Production version would query the PortlandMaps REST API
    (https://www.portlandmaps.com/api/).
    """

    BASE_URL = "https://www.portlandmaps.com/detail"

    def lookup(self, address: str) -> PortlandMapsInfo:
        """Return PortlandMaps info for *address*."""
        h = int(hashlib.sha256(address.encode()).hexdigest(), 16)
        rng = random.Random(h)

        zoning = rng.choice(["R5", "R7", "R10", "R2.5", "CM1", "CE"])
        permits = rng.randint(0, 6)
        open_p = rng.randint(0, min(2, permits))
        liens = rng.choices([0, 0, 0, 1, 2], k=1)[0]
        lien_total = round(rng.uniform(2000, 35000), 2) if liens else 0.0

        return PortlandMapsInfo(
            address=address,
            state_id=f"1N2E{rng.randint(10,35)}{rng.choice('ABCD')}{rng.choice('ABCD')}"
                     f" {rng.randint(100,9999):05d}",
            zoning=zoning,
            comprehensive_plan=rng.choice([
                "Single-Dwelling Residential",
                "Multi-Dwelling Residential",
                "Mixed-Use Civic Corridor",
            ]),
            flood_zone=rng.choice(["X (minimal)", "X (minimal)", "AE (1% annual)"]),
            seismic_zone=rng.choice(["moderate", "moderate", "high"]),
            permits_last_5yr=permits,
            open_permits=open_p,
            liens=liens,
            lien_total=lien_total,
            neighborhood_association=rng.choice([
                "Lents Neighborhood Association",
                "Cully Association of Neighbors",
                "Foster-Powell Neighborhood Assoc.",
                "St. Johns Neighborhood Assoc.",
                "Woodstock Neighborhood Assoc.",
                "Montavilla Neighborhood Assoc.",
                "Parkrose Neighborhood Assoc.",
            ]),
        )


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
