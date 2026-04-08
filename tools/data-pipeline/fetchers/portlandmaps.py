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
    slug = address.lower().strip()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug


def parse_portlandmaps_response(api_response: dict, original_address: str) -> dict:
    results = api_response.get("results", [])
    if not results:
        return {
            "address": original_address, "state_id": "", "zoning": "",
            "comprehensive_plan": "", "flood_zone": "", "seismic_zone": "",
            "permits_last_5yr": 0, "open_permits": 0, "liens": 0,
            "lien_total": 0.0, "neighborhood_association": "",
        }
    r = results[0]
    permits = r.get("permits", [])
    current_year = datetime.now().year
    permits_5yr = [p for p in permits if p.get("year", 0) >= current_year - 5]
    open_permits = len([p for p in permits if p.get("status", "").lower() in ("issued", "under review", "pending")])
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
    def __init__(self, cache_dir: Optional[Path] = None, session: Optional[requests.Session] = None):
        self.cache_dir = cache_dir or PORTLANDMAPS_DIR
        self.session = session or requests.Session()
        self.session.headers.update({
            "User-Agent": "PortlandCoopDataPipeline/1.0",
            "Accept": "application/json",
        })

    def lookup_cached(self, address: str) -> Optional[dict]:
        slug = address_to_slug(address)
        cache_file = self.cache_dir / f"{slug}.json"
        if cache_file.exists():
            with open(cache_file) as f:
                return json.load(f)
        return None

    def fetch_property(self, address: str) -> Optional[dict]:
        cached = self.lookup_cached(address)
        if cached is not None:
            logger.debug("Cache hit for %s", address)
            return cached
        logger.info("Fetching PortlandMaps data for %s", address)
        try:
            resp = self.session.get(
                f"{PORTLANDMAPS_API_BASE}/detail/",
                params={"address": address},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            info = parse_portlandmaps_response(data, address)
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
        delay = RATE_LIMITS.get("portlandmaps", 1.0)
        results = {}
        for i, addr in enumerate(addresses):
            results[addr] = self.fetch_property(addr)
            if i < len(addresses) - 1 and self.lookup_cached(addr) is None:
                time.sleep(delay)
        return results
