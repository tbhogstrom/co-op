import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'data-pipeline'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'comp-analyzer'))

import json
from loaders.assessor_loader import AssessorLoader, fuzzy_address_match


def _write_sample_assessor(tmp_path):
    assessor_dir = tmp_path / "multnomah-by-neighborhood"
    assessor_dir.mkdir(parents=True)
    records = [
        {"property_id": "R123456", "address": "123 SE FOSTER RD",
         "owner_name": "SMITH JOHN", "assessed_value": 320000, "market_value": 385000,
         "tax_year": 2025, "annual_tax": 4200.0, "lot_sqft": 5000,
         "year_built": 1952, "zoning": "R5", "legal_description": "LOT 1 BLK 2"},
        {"property_id": "R789012", "address": "456 SE 92ND AVE",
         "owner_name": "DOE JANE", "assessed_value": 280000, "market_value": 330000,
         "tax_year": 2025, "annual_tax": 3600.0, "lot_sqft": 4500,
         "year_built": 1948, "zoning": "R5", "legal_description": "LOT 5 BLK 8"},
    ]
    (assessor_dir / "lents.json").write_text(json.dumps(records))
    return tmp_path


def test_fuzzy_address_match_exact():
    assert fuzzy_address_match("123 SE FOSTER RD", "123 SE Foster Rd") is True


def test_fuzzy_address_match_with_suffix():
    assert fuzzy_address_match("123 SE FOSTER RD", "123 SE Foster Road") is True


def test_fuzzy_address_match_with_city():
    assert fuzzy_address_match("123 SE FOSTER RD", "123 SE Foster Rd, Portland, OR") is True


def test_fuzzy_address_match_mismatch():
    assert fuzzy_address_match("123 SE FOSTER RD", "456 NE CULLY BLVD") is False


def test_loader_lookup_finds_record(tmp_path):
    assessor_dir = _write_sample_assessor(tmp_path)
    loader = AssessorLoader(assessor_dir=assessor_dir)
    result = loader.lookup("123 SE Foster Rd, Portland, OR")
    assert result is not None
    assert result.property_id == "R123456"
    assert result.assessed_value == 320000
    assert result.zoning == "R5"


def test_loader_lookup_returns_none_for_unknown(tmp_path):
    assessor_dir = _write_sample_assessor(tmp_path)
    loader = AssessorLoader(assessor_dir=assessor_dir)
    result = loader.lookup("999 NW NONEXISTENT ST")
    assert result is None
