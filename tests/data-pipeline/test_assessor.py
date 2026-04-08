import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'data-pipeline'))

import json
import pandas as pd
from fetchers.assessor import parse_assessor_csv, filter_by_neighborhoods, AssessorFetcher


def test_parse_assessor_csv_basic():
    csv_content = (
        "PropertyID,SitusAddr,OwnerName,TotalAssessedValue,TotalMarketValue,"
        "TaxYear,TotalTax,LotSqFt,YearBuilt,Zoning,LegalDesc,SitusZip\n"
        "R123456,123 SE FOSTER RD,SMITH JOHN,320000,385000,"
        "2025,4200.00,5000,1952,R5,LOT 1 BLK 2,97266\n"
        "R789012,456 NE CULLY BLVD,DOE JANE,290000,340000,"
        "2025,3800.50,6000,1948,R7,LOT 5 BLK 8,97218\n"
    )
    df = parse_assessor_csv(csv_content)
    assert len(df) == 2
    assert df.iloc[0]["property_id"] == "R123456"
    assert df.iloc[0]["address"] == "123 SE FOSTER RD"
    assert df.iloc[0]["assessed_value"] == 320000


def test_filter_by_neighborhoods():
    data = [
        {"property_id": "R1", "address": "123 SE FOSTER RD", "zip_code": "97266",
         "assessed_value": 320000, "market_value": 385000, "tax_year": 2025,
         "annual_tax": 4200.0, "lot_sqft": 5000, "year_built": 1952, "zoning": "R5",
         "legal_description": "LOT 1", "owner_name": "SMITH"},
        {"property_id": "R2", "address": "789 NW 23RD AVE", "zip_code": "97210",
         "assessed_value": 600000, "market_value": 750000, "tax_year": 2025,
         "annual_tax": 8000.0, "lot_sqft": 3000, "year_built": 1920, "zoning": "CM1",
         "legal_description": "LOT 3", "owner_name": "DOE"},
    ]
    df = pd.DataFrame(data)
    filtered = filter_by_neighborhoods(df)
    assert len(filtered) == 1
    assert filtered.iloc[0]["property_id"] == "R1"


def test_assessor_fetcher_writes_json(tmp_path):
    fetcher = AssessorFetcher(output_dir=tmp_path)
    records = [
        {"property_id": "R1", "address": "123 SE FOSTER RD", "zip_code": "97266",
         "assessed_value": 320000, "market_value": 385000, "tax_year": 2025,
         "annual_tax": 4200.0, "lot_sqft": 5000, "year_built": 1952, "zoning": "R5",
         "legal_description": "LOT 1", "owner_name": "SMITH"},
    ]
    df = pd.DataFrame(records)
    fetcher.write_by_neighborhood(df)
    outfile = tmp_path / "multnomah-by-neighborhood" / "lents.json"
    assert outfile.exists()
    data = json.loads(outfile.read_text())
    assert len(data) == 1
