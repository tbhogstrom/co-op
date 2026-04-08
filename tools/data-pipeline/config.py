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
            "region_id": 35022,
            "region_type": 1,
            "market": "portland",
        },
    },
    "cully": {
        "name": "Cully",
        "slug": "cully",
        "zip_codes": ["97218", "97213"],
        "redfin_region_url_params": {
            "region_id": 32221,
            "region_type": 1,
            "market": "portland",
        },
    },
    "foster-powell": {
        "name": "Foster-Powell",
        "slug": "foster-powell",
        "zip_codes": ["97206"],
        "redfin_region_url_params": {
            "region_id": 31386,
            "region_type": 1,
            "market": "portland",
        },
    },
    "st-johns": {
        "name": "St. Johns",
        "slug": "st-johns",
        "zip_codes": ["97203"],
        "redfin_region_url_params": {
            "region_id": 30396,
            "region_type": 1,
            "market": "portland",
        },
    },
    "woodstock": {
        "name": "Woodstock",
        "slug": "woodstock",
        "zip_codes": ["97202", "97206"],
        "redfin_region_url_params": {
            "region_id": 32495,
            "region_type": 1,
            "market": "portland",
        },
    },
    "montavilla": {
        "name": "Montavilla",
        "slug": "montavilla",
        "zip_codes": ["97216", "97220"],
        "redfin_region_url_params": {
            "region_id": 33898,
            "region_type": 1,
            "market": "portland",
        },
    },
    "parkrose": {
        "name": "Parkrose",
        "slug": "parkrose",
        "zip_codes": ["97220", "97230"],
        "redfin_region_url_params": {
            "region_id": 8613,
            "region_type": 1,
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
