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
    if months_back is None:
        months_back = COMP_DATE_RANGE_MONTHS
    info = NEIGHBORHOODS[neighborhood_slug]
    params = info["redfin_region_url_params"]
    url = (
        f"{REDFIN_DOWNLOAD_BASE}"
        f"?al=1"
        f"&market={params['market']}"
        f"&min_price={COMP_PRICE_MIN}"
        f"&max_price={COMP_PRICE_MAX}"
        f"&region_id={params['region_id']}"
        f"&region_type={params['region_type']}"
        f"&sold_within_days={months_back * 30}"
        f"&status=9"
        f"&uipt=1,2,3"
        f"&v=8"
    )
    return url


def parse_redfin_csv(csv_content: str, neighborhood_slug: str) -> list[dict]:
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
    def __init__(self, output_dir: Optional[Path] = None, session: Optional[requests.Session] = None):
        self.output_dir = output_dir or COMP_SALES_DIR
        self.session = session or requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/csv",
        })

    def fetch_neighborhood(self, neighborhood_slug: str) -> list[dict]:
        url = build_redfin_url(neighborhood_slug)
        logger.info("Fetching Redfin data for %s", neighborhood_slug)
        try:
            resp = self.session.get(url, timeout=30)
            resp.raise_for_status()
            content = resp.text
            if not content.strip() or content.startswith("<!DOCTYPE"):
                logger.warning("Redfin returned HTML instead of CSV for %s", neighborhood_slug)
                return []
            records = parse_redfin_csv(content, neighborhood_slug)
            logger.info("Parsed %d valid comps for %s", len(records), neighborhood_slug)
            return records
        except requests.RequestException as e:
            logger.error("Failed to fetch Redfin data for %s: %s", neighborhood_slug, e)
            return []

    def write_comps(self, neighborhood_slug: str, records: list[dict]) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        outfile = self.output_dir / f"{neighborhood_slug}-comps.json"
        with open(outfile, "w") as f:
            json.dump(records, f, indent=2)
        logger.info("Wrote %d comps to %s", len(records), outfile)
        return outfile

    def fetch_all(self) -> dict[str, int]:
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
