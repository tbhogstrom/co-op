"""PortlandMapsLookupLoader — drop-in replacement for PortlandMapsLookup stub."""

import json
import logging
import re
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "comp-analyzer"))
from data_sources import PortlandMapsInfo

from config import PORTLANDMAPS_DIR

logger = logging.getLogger(__name__)


def _address_to_slug(address: str) -> str:
    slug = address.lower().strip()
    slug = re.sub(r',\s*portland.*$', '', slug)
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug


class PortlandMapsLookupLoader:
    def __init__(self, cache_dir: Optional[Path] = None, fetch_on_miss: bool = True):
        self.cache_dir = cache_dir or PORTLANDMAPS_DIR
        self.fetch_on_miss = fetch_on_miss
        self._fetcher = None

    def _get_fetcher(self):
        if self._fetcher is None:
            from fetchers.portlandmaps import PortlandMapsFetcher
            self._fetcher = PortlandMapsFetcher(cache_dir=self.cache_dir)
        return self._fetcher

    def lookup(self, address: str) -> Optional[PortlandMapsInfo]:
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
