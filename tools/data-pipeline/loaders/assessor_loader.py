"""AssessorLoader — drop-in replacement for MultnomahAssessor stub."""

import json
import logging
import re
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "comp-analyzer"))
from data_sources import AssessorRecord

from config import ASSESSOR_BY_NEIGHBORHOOD_DIR, NEIGHBORHOODS

logger = logging.getLogger(__name__)

_SUFFIX_MAP = {
    "ROAD": "RD", "STREET": "ST", "AVENUE": "AVE", "BOULEVARD": "BLVD",
    "DRIVE": "DR", "LANE": "LN", "COURT": "CT", "PLACE": "PL",
    "CIRCLE": "CIR", "TERRACE": "TER", "WAY": "WAY",
}

_DIR_MAP = {
    "NORTH": "N", "SOUTH": "S", "EAST": "E", "WEST": "W",
    "NORTHEAST": "NE", "NORTHWEST": "NW", "SOUTHEAST": "SE", "SOUTHWEST": "SW",
}


def _normalize_for_match(address: str) -> str:
    addr = address.upper().strip()
    addr = re.sub(r',\s*(PORTLAND|OR|OREGON).*$', '', addr)
    for full, abbr in _SUFFIX_MAP.items():
        addr = re.sub(rf'\b{full}\b', abbr, addr)
    for full, abbr in _DIR_MAP.items():
        addr = re.sub(rf'\b{full}\b', abbr, addr)
    addr = re.sub(r'\s*(UNIT|APT|STE|SUITE|#)\s*\S+', '', addr)
    addr = re.sub(r'\s+', ' ', addr).strip()
    return addr


def fuzzy_address_match(assessor_addr: str, query_addr: str) -> bool:
    return _normalize_for_match(assessor_addr) == _normalize_for_match(query_addr)


class AssessorLoader:
    def __init__(self, assessor_dir: Optional[Path] = None):
        self.assessor_dir = assessor_dir or ASSESSOR_BY_NEIGHBORHOOD_DIR
        self._cache: Optional[list[dict]] = None

    def _load_all(self) -> list[dict]:
        if self._cache is not None:
            return self._cache
        records = []
        by_hood_dir = self.assessor_dir / "multnomah-by-neighborhood"
        if not by_hood_dir.exists():
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
