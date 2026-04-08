import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'data-pipeline'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'comp-analyzer'))

import json
from loaders.portlandmaps_lookup import PortlandMapsLookupLoader


def _write_sample_cache(tmp_path):
    cache_dir = tmp_path / "portlandmaps"
    cache_dir.mkdir()
    cached = {
        "address": "123 SE Foster Rd", "state_id": "1S2E15AC 01200",
        "zoning": "R5", "comprehensive_plan": "Single-Dwelling Residential",
        "flood_zone": "X", "seismic_zone": "moderate",
        "permits_last_5yr": 3, "open_permits": 1,
        "liens": 1, "lien_total": 5000.00,
        "neighborhood_association": "Foster-Powell NA",
    }
    slug = "123-se-foster-rd"
    (cache_dir / f"{slug}.json").write_text(json.dumps(cached))
    return cache_dir


def test_lookup_from_cache(tmp_path):
    cache_dir = _write_sample_cache(tmp_path)
    loader = PortlandMapsLookupLoader(cache_dir=cache_dir)
    result = loader.lookup("123 SE Foster Rd")
    assert result is not None
    assert result.zoning == "R5"
    assert result.permits_last_5yr == 3
    assert result.liens == 1
    assert result.lien_total == 5000.00


def test_lookup_returns_none_for_uncached(tmp_path):
    cache_dir = tmp_path / "portlandmaps"
    cache_dir.mkdir()
    loader = PortlandMapsLookupLoader(cache_dir=cache_dir, fetch_on_miss=False)
    result = loader.lookup("999 NW NONEXISTENT ST")
    assert result is None
