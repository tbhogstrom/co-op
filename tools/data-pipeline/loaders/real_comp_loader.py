"""RealCompLoader — drop-in replacement for SyntheticMLSGenerator."""

import json
import logging
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "comp-analyzer"))
from data_sources import CompSale

from geocoding import haversine
from config import COMP_SALES_DIR

logger = logging.getLogger(__name__)

_SLUG_MAP = {
    "st. johns": "st-johns",
    "st johns": "st-johns",
    "foster-powell": "foster-powell",
    "foster powell": "foster-powell",
}


def _normalize_slug(neighborhood: str) -> str:
    lower = neighborhood.strip().lower()
    return _SLUG_MAP.get(lower, lower)


class RealCompLoader:
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
            try:
                sale_date = date.fromisoformat(record["sale_date"])
            except (ValueError, KeyError):
                continue
            if sale_date < cutoff:
                continue
            distance = 0.0
            if subject_lat and subject_lon and "lat" in record and "lon" in record:
                distance = haversine(subject_lat, subject_lon, record["lat"], record["lon"])
                if distance > radius_miles:
                    continue
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
        comps.sort(key=lambda c: (
            abs(c.sqft - sqft_target),
            -date.fromisoformat(c.sale_date).toordinal(),
        ))
        return comps[:count]
