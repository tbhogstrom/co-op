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

COLUMN_MAP = {
    "PropertyID": "property_id", "PROPERTYID": "property_id", "prop_id": "property_id",
    "SitusAddr": "address", "SITUSADDR": "address", "situs_addr": "address",
    "OwnerName": "owner_name", "OWNERNAME": "owner_name", "owner_name": "owner_name",
    "TotalAssessedValue": "assessed_value", "TOTALASSESSEDVALUE": "assessed_value", "total_assessed": "assessed_value",
    "TotalMarketValue": "market_value", "TOTALMARKETVALUE": "market_value", "total_market": "market_value",
    "TaxYear": "tax_year", "TAXYEAR": "tax_year", "tax_year": "tax_year",
    "TotalTax": "annual_tax", "TOTALTAX": "annual_tax", "total_tax": "annual_tax",
    "LotSqFt": "lot_sqft", "LOTSQFT": "lot_sqft", "lot_sqft": "lot_sqft",
    "YearBuilt": "year_built", "YEARBUILT": "year_built", "year_built": "year_built",
    "Zoning": "zoning", "ZONING": "zoning", "zoning": "zoning",
    "LegalDesc": "legal_description", "LEGALDESC": "legal_description", "legal_desc": "legal_description",
    "SitusZip": "zip_code", "SITUSZIP": "zip_code", "situs_zip": "zip_code",
}


def parse_assessor_csv(csv_content: str) -> pd.DataFrame:
    df = pd.read_csv(io.StringIO(csv_content), dtype=str)
    rename = {}
    for col in df.columns:
        if col in COLUMN_MAP:
            rename[col] = COLUMN_MAP[col]
    df = df.rename(columns=rename)
    int_cols = ["assessed_value", "market_value", "tax_year", "lot_sqft", "year_built"]
    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].str.replace(",", ""), errors="coerce").fillna(0).astype(int)
    float_cols = ["annual_tax"]
    for col in float_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].str.replace(",", ""), errors="coerce").fillna(0.0)
    if "zip_code" in df.columns:
        df["zip_code"] = df["zip_code"].str[:5]
    return df


def filter_by_neighborhoods(df: pd.DataFrame) -> pd.DataFrame:
    target_zips = set()
    for info in NEIGHBORHOODS.values():
        target_zips.update(info["zip_codes"])
    if "zip_code" not in df.columns:
        logger.warning("No zip_code column found — cannot filter by neighborhood")
        return df
    return df[df["zip_code"].isin(target_zips)].copy()


class AssessorFetcher:
    def __init__(self, output_dir: Optional[Path] = None, session: Optional[requests.Session] = None):
        self.output_dir = output_dir or ASSESSOR_DIR
        self.by_neighborhood_dir = self.output_dir / "multnomah-by-neighborhood"
        self.session = session or requests.Session()

    def fetch_bulk(self) -> Optional[pd.DataFrame]:
        logger.info("Fetching Multnomah County assessor bulk data")
        try:
            resp = self.session.get(ASSESSOR_BULK_URL, timeout=60)
            resp.raise_for_status()
            if resp.headers.get("content-type", "").startswith("text/html"):
                logger.warning("Assessor URL returned HTML page — bulk CSV may require manual download from %s", ASSESSOR_BULK_URL)
                return None
            df = parse_assessor_csv(resp.text)
            logger.info("Parsed %d assessor records", len(df))
            return df
        except requests.RequestException as e:
            logger.error("Failed to fetch assessor data: %s", e)
            return None

    def load_local_csv(self, csv_path: Path) -> pd.DataFrame:
        logger.info("Loading assessor CSV from %s", csv_path)
        with open(csv_path) as f:
            df = parse_assessor_csv(f.read())
        logger.info("Parsed %d assessor records from local file", len(df))
        return df

    def write_bulk_csv(self, df: pd.DataFrame) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        outfile = self.output_dir / "multnomah-bulk-extract.csv"
        filtered = filter_by_neighborhoods(df)
        filtered.to_csv(outfile, index=False)
        logger.info("Wrote %d filtered records to %s", len(filtered), outfile)
        return outfile

    def write_by_neighborhood(self, df: pd.DataFrame) -> dict[str, int]:
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
