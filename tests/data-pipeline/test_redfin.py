import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'data-pipeline'))

import json
from fetchers.redfin import build_redfin_url, parse_redfin_csv, RedfinFetcher


def test_build_redfin_url_includes_required_params():
    url = build_redfin_url("lents")
    assert "gis-csv" in url
    assert "region_id=35022" in url
    assert "status=9" in url


def test_parse_redfin_csv_produces_valid_records():
    csv_content = (
        "ADDRESS,CITY,STATE OR PROVINCE,SOLD DATE,PRICE,SQUARE FEET,"
        "BEDS,BATHS,LOT SIZE,YEAR BUILT\n"
        '123 SE Foster Rd,Portland,OR,"April 5, 2026","$385,000","1,200",'
        '3,1.5,"5,000",1952\n'
        '456 SE 92nd Ave,Portland,OR,"March 10, 2026","$310,000","1,050",'
        '2,1.0,"4,500",1948\n'
    )
    records = parse_redfin_csv(csv_content, "lents")
    assert len(records) == 2
    assert records[0]["address"] == "123 SE Foster Rd, Portland, OR"
    assert records[0]["sale_price"] == 385000
    assert records[0]["neighborhood"] == "lents"
    assert records[1]["sqft"] == 1050


def test_parse_redfin_csv_skips_invalid_rows():
    csv_content = (
        "ADDRESS,CITY,STATE OR PROVINCE,SOLD DATE,PRICE,SQUARE FEET,"
        "BEDS,BATHS,LOT SIZE,YEAR BUILT\n"
        '123 SE Foster Rd,Portland,OR,"April 5, 2026","$385,000","1,200",'
        '3,1.5,"5,000",1952\n'
        ',,OR,,,,0,0,,\n'
    )
    records = parse_redfin_csv(csv_content, "lents")
    assert len(records) == 1


def test_redfin_fetcher_writes_json(tmp_path):
    fetcher = RedfinFetcher(output_dir=tmp_path)
    records = [
        {
            "address": "123 SE Foster Rd, Portland, OR",
            "sale_date": "2026-04-05",
            "sale_price": 385000,
            "sqft": 1200,
            "beds": 3,
            "baths": 1.5,
            "lot_sqft": 5000,
            "year_built": 1952,
            "condition": "average",
            "neighborhood": "lents",
            "price_per_sqft": 320.83,
        }
    ]
    fetcher.write_comps("lents", records)
    outfile = tmp_path / "lents-comps.json"
    assert outfile.exists()
    data = json.loads(outfile.read_text())
    assert len(data) == 1
    assert data[0]["sale_price"] == 385000
