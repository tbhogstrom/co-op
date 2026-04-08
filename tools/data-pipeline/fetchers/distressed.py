"""Aggregate distressed property leads from multiple data sources."""

import json
import logging
from pathlib import Path
from typing import Optional

from config import NEIGHBORHOODS, LISTINGS_DIR

logger = logging.getLogger(__name__)

SIGNAL_WEIGHTS = {
    "tax_delinquent": 3, "liens": 2, "code_violations": 2,
    "below_market": 1, "long_dom": 1, "estate_sale": 1,
}
MAX_PURCHASE_PRICE = 200_000
TARGET_NEIGHBORHOODS = {"lents", "cully", "parkrose"}


def score_distress_signal(signals: dict[str, bool]) -> int:
    return sum(SIGNAL_WEIGHTS.get(k, 0) for k, v in signals.items() if v)


def identify_distressed(assessor_records: list[dict], portlandmaps_data: dict[str, dict],
                         comp_records: Optional[list[dict]] = None) -> list[dict]:
    distressed = []
    for record in assessor_records:
        address = record.get("address", "")
        signals = {"tax_delinquent": False, "liens": False, "code_violations": False, "below_market": False}
        annual_tax = record.get("annual_tax", 0)
        if annual_tax == 0 or annual_tax is None:
            signals["tax_delinquent"] = True
        pm_data = portlandmaps_data.get(address, {})
        if pm_data.get("liens", 0) > 0:
            signals["liens"] = True
        if pm_data.get("open_permits", 0) > 2:
            signals["code_violations"] = True
        assessed = record.get("assessed_value", 0)
        market = record.get("market_value", 0)
        if market > 0 and assessed > 0 and (assessed / market) < 0.75:
            signals["below_market"] = True
        score = score_distress_signal(signals)
        if score == 0:
            continue
        zip_code = str(record.get("zip_code", ""))
        neighborhood = None
        for slug, info in NEIGHBORHOODS.items():
            if zip_code in info["zip_codes"]:
                neighborhood = slug
                break
        active_signals = [k for k, v in signals.items() if v]
        estimated_low = int(assessed * 0.85) if assessed else 0
        estimated_high = int(market * 1.0) if market else int(assessed * 1.2) if assessed else 0
        distressed.append({
            "address": address, "neighborhood": neighborhood, "zip_code": zip_code,
            "distress_signals": active_signals, "distress_score": score,
            "estimated_value_range": [estimated_low, estimated_high],
            "assessed_value": assessed, "market_value": market,
            "lot_sqft": record.get("lot_sqft", 0), "year_built": record.get("year_built", 0),
            "zoning": record.get("zoning", ""), "source": "assessor+portlandmaps",
        })
    distressed.sort(key=lambda d: d["distress_score"], reverse=True)
    return distressed


def filter_to_deal_guardrails(properties: list[dict]) -> tuple[list[dict], list[dict]]:
    deal_ready, watchlist = [], []
    for prop in properties:
        est_high = prop.get("estimated_value_range", [0, 999999])[1]
        neighborhood = prop.get("neighborhood")
        if est_high <= MAX_PURCHASE_PRICE and neighborhood in TARGET_NEIGHBORHOODS:
            deal_ready.append(prop)
        else:
            watchlist.append(prop)
    return deal_ready, watchlist


class DistressedAggregator:
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or LISTINGS_DIR

    def write_results(self, distressed: list[dict], watchlist: list[dict]) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        with open(self.output_dir / "distressed-listings.json", "w") as f:
            json.dump(distressed, f, indent=2)
        with open(self.output_dir / "watchlist.json", "w") as f:
            json.dump(watchlist, f, indent=2)

    def aggregate(self, assessor_records: list[dict], portlandmaps_data: dict[str, dict],
                  comp_records: Optional[list[dict]] = None) -> dict[str, int]:
        all_distressed = identify_distressed(assessor_records, portlandmaps_data, comp_records)
        deal_ready, watchlist = filter_to_deal_guardrails(all_distressed)
        self.write_results(deal_ready, watchlist)
        return {"total_distressed_found": len(all_distressed), "deal_ready": len(deal_ready), "watchlist": len(watchlist)}
