import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'data-pipeline'))

import json
from fetchers.distressed import identify_distressed, score_distress_signal, DistressedAggregator


def test_identify_distressed_from_assessor():
    assessor_records = [
        {"address": "123 SE FOSTER RD", "assessed_value": 320000, "market_value": 385000,
         "lot_sqft": 5000, "year_built": 1952, "zoning": "R5", "zip_code": "97266",
         "annual_tax": 4200, "owner_name": "SMITH"},
        {"address": "456 SE 92ND AVE", "assessed_value": 180000, "market_value": 200000,
         "lot_sqft": 4500, "year_built": 1948, "zoning": "R5", "zip_code": "97266",
         "annual_tax": 0},
    ]
    portlandmaps = {
        "123 SE FOSTER RD": {"liens": 0, "lien_total": 0, "open_permits": 0},
        "456 SE 92ND AVE": {"liens": 2, "lien_total": 15000, "open_permits": 0},
    }
    distressed = identify_distressed(assessor_records, portlandmaps)
    assert len(distressed) >= 1
    addresses = [d["address"] for d in distressed]
    assert "456 SE 92ND AVE" in addresses


def test_score_distress_signal():
    signals = {"tax_delinquent": True, "liens": True, "code_violations": False, "below_market": False}
    score = score_distress_signal(signals)
    assert 0 < score <= 10


def test_score_distress_signal_no_signals():
    signals = {"tax_delinquent": False, "liens": False, "code_violations": False, "below_market": False}
    score = score_distress_signal(signals)
    assert score == 0


def test_aggregator_writes_files(tmp_path):
    agg = DistressedAggregator(output_dir=tmp_path)
    distressed = [
        {"address": "456 SE 92ND AVE", "neighborhood": "lents", "distress_signals": ["tax_delinquent", "liens"],
         "distress_score": 6, "estimated_value_range": [180000, 220000], "source": "assessor+portlandmaps"},
    ]
    watchlist = [
        {"address": "789 NE CULLY BLVD", "neighborhood": "cully", "distress_signals": ["below_market"],
         "distress_score": 3, "estimated_value_range": [200000, 250000], "source": "comp_analysis"},
    ]
    agg.write_results(distressed, watchlist)
    assert (tmp_path / "distressed-listings.json").exists()
    assert (tmp_path / "watchlist.json").exists()
    d_data = json.loads((tmp_path / "distressed-listings.json").read_text())
    assert len(d_data) == 1
