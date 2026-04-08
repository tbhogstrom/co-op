import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'data-pipeline'))

from normalizer import normalize_redfin_row, validate_comp_record, merge_redfin_assessor


def test_normalize_redfin_row_maps_fields():
    row = {
        "ADDRESS": "123 SE Foster Rd",
        "CITY": "Portland",
        "STATE OR PROVINCE": "OR",
        "SOLD DATE": "April 5, 2026",
        "PRICE": "$385,000",
        "SQUARE FEET": "1,200",
        "BEDS": "3",
        "BATHS": "1.5",
        "LOT SIZE": "5,000",
        "YEAR BUILT": "1952",
    }
    comp = normalize_redfin_row(row, "lents")
    assert comp["address"] == "123 SE Foster Rd, Portland, OR"
    assert comp["sale_date"] == "2026-04-05"
    assert comp["sale_price"] == 385000
    assert comp["sqft"] == 1200
    assert comp["beds"] == 3
    assert comp["baths"] == 1.5
    assert comp["lot_sqft"] == 5000
    assert comp["year_built"] == 1952
    assert comp["condition"] == "average"
    assert comp["neighborhood"] == "lents"


def test_normalize_redfin_row_condition_heuristic():
    row = {
        "ADDRESS": "456 NE Cully Blvd",
        "CITY": "Portland",
        "STATE OR PROVINCE": "OR",
        "SOLD DATE": "March 1, 2026",
        "PRICE": "$200,000",
        "SQUARE FEET": "1,000",
        "BEDS": "2",
        "BATHS": "1",
        "LOT SIZE": "4,500",
        "YEAR BUILT": "1945",
        "HOG_DESCRIPTION": "Estate sale, sold as-is, needs work",
    }
    comp = normalize_redfin_row(row, "cully")
    assert comp["condition"] in ("fair", "poor")


def test_validate_comp_record_passes_good_record():
    record = {
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
    }
    errors = validate_comp_record(record)
    assert errors == []


def test_validate_comp_record_catches_bad_price():
    record = {
        "address": "123 SE Foster Rd, Portland, OR",
        "sale_date": "2026-04-05",
        "sale_price": -100,
        "sqft": 1200,
        "beds": 3,
        "baths": 1.5,
        "lot_sqft": 5000,
        "year_built": 1952,
        "condition": "average",
        "neighborhood": "lents",
    }
    errors = validate_comp_record(record)
    assert len(errors) > 0


def test_merge_redfin_assessor():
    redfin = {
        "address": "123 SE Foster Rd, Portland, OR",
        "sale_price": 385000,
        "sqft": 1200,
        "beds": 3,
        "baths": 1.5,
        "lot_sqft": 0,
        "year_built": 1952,
    }
    assessor = {
        "address": "123 SE FOSTER RD",
        "lot_sqft": 5200,
        "year_built": 1951,
        "assessed_value": 320000,
        "zoning": "R5",
    }
    merged = merge_redfin_assessor(redfin, assessor)
    assert merged["lot_sqft"] == 5200
    assert merged["year_built"] == 1952
    assert merged["assessed_value"] == 320000
