"""Fetch and process Portland Police Bureau crime data."""

import json
import logging
from pathlib import Path
from typing import Optional

import requests

from config import NEIGHBORHOODS, NEIGHBORHOOD_DIR, PORTLAND_POLICE_DATA_URL, RATE_LIMITS

logger = logging.getLogger(__name__)

PORTLAND_CRIME_ARCGIS = "https://opendata.arcgis.com/datasets/portland-crime-data.geojson"

ZIP_TO_NEIGHBORHOOD = {}
for slug, info in NEIGHBORHOODS.items():
    for z in info["zip_codes"]:
        ZIP_TO_NEIGHBORHOOD.setdefault(z, []).append(slug)


def compute_crime_trend(prior_count: int, current_count: int) -> float:
    if prior_count == 0:
        return 0.0
    return round(((current_count - prior_count) / prior_count) * 100, 1)


def normalize_crime_score(pct_change: float) -> float:
    score = (pct_change / 50) * 10
    return round(max(-10.0, min(10.0, score)), 1)


def _crime_trend_description(pct_change: float) -> str:
    if pct_change < -2:
        return f"Improving — down {abs(pct_change)}% YoY"
    elif pct_change > 2:
        return f"Worsening — up {abs(pct_change)}% YoY"
    else:
        return f"Stable — {abs(pct_change)}% change YoY"


class PoliceFetcher:
    def __init__(self, neighborhood_dir: Optional[Path] = None,
                 session: Optional[requests.Session] = None):
        self.neighborhood_dir = neighborhood_dir or NEIGHBORHOOD_DIR
        self.session = session or requests.Session()

    def fetch_crime_data(self) -> Optional[dict]:
        logger.info("Fetching Portland crime data")
        try:
            resp = self.session.get(PORTLAND_CRIME_ARCGIS, timeout=30)
            resp.raise_for_status()
            data = resp.json()
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
            logger.warning("Failed to fetch crime data: %s", e)
            return None

    def update_neighborhood_crime(self, slug: str, pct_change: float) -> None:
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
        crime_data = self.fetch_crime_data()
        summary = {}
        if crime_data is None:
            logger.warning("No crime data available — skipping")
            return summary
        all_years = set()
        for zd in crime_data.values():
            all_years.update(zd.keys())
        sorted_years = sorted(all_years, reverse=True)
        if len(sorted_years) < 2:
            logger.warning("Need at least 2 years of crime data")
            return summary
        current_year = sorted_years[0]
        prior_year = sorted_years[1]
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
        return summary
