import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'data-pipeline'))

from config import NEIGHBORHOODS, DATA_DIR, COMP_SALES_DIR, ASSESSOR_DIR, PORTLANDMAPS_DIR


def test_neighborhoods_has_seven_entries():
    assert len(NEIGHBORHOODS) == 7


def test_each_neighborhood_has_required_fields():
    required = {"name", "slug", "zip_codes", "redfin_region_url_params"}
    for slug, info in NEIGHBORHOODS.items():
        missing = required - set(info.keys())
        assert not missing, f"{slug} missing: {missing}"


def test_data_dirs_are_paths():
    from pathlib import Path
    assert isinstance(DATA_DIR, Path)
    assert isinstance(COMP_SALES_DIR, Path)
    assert isinstance(ASSESSOR_DIR, Path)
    assert isinstance(PORTLANDMAPS_DIR, Path)
