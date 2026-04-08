"""Geocoding via Census Bureau API and Haversine distance computation."""

import json
import math
import re
import time
import urllib.request
import urllib.parse
from typing import Optional, Tuple

from config import CENSUS_GEOCODER_URL, RATE_LIMITS

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
    addr = re.sub(r',?\s*\b(UNIT|APT|STE|SUITE|#)\s*\S+', '', addr)
    addr = re.sub(r',\s*PORTLAND.*$', '', addr)
    addr = re.sub(r'\s+', ' ', addr).strip()
    return addr


def geocode(address: str, city: str = "Portland", state: str = "OR") -> Optional[Tuple[float, float]]:
    """Geocode an address using the Census Bureau Geocoding API. Returns (lat, lon) or None."""
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
        return (float(coords["y"]), float(coords["x"]))
    except Exception:
        return None


def batch_geocode(addresses: list[str], city: str = "Portland", state: str = "OR",
                  delay: float = None) -> dict[str, Optional[Tuple[float, float]]]:
    """Geocode a list of addresses, returning {address: (lat, lon)}."""
    if delay is None:
        delay = RATE_LIMITS.get("census_geocoder", 1.0)
    results = {}
    for i, addr in enumerate(addresses):
        results[addr] = geocode(addr, city, state)
        if i < len(addresses) - 1:
            time.sleep(delay)
    return results
