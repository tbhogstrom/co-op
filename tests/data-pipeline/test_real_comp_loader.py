import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'data-pipeline'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'comp-analyzer'))

import json
from datetime import date
from loaders.real_comp_loader import RealCompLoader


def _write_sample_comps(tmp_path):
    comps_dir = tmp_path / "comp-sales"
    comps_dir.mkdir()
    comps = [
        {"address": "123 SE Foster Rd, Portland, OR", "sale_date": "2026-03-01",
         "sale_price": 350000, "sqft": 1100, "beds": 3, "baths": 1.5,
         "lot_sqft": 5000, "year_built": 1952, "condition": "average",
         "neighborhood": "lents", "price_per_sqft": 318.18, "lat": 45.4833, "lon": -122.5777},
        {"address": "456 SE 92nd Ave, Portland, OR", "sale_date": "2026-01-15",
         "sale_price": 310000, "sqft": 1000, "beds": 2, "baths": 1.0,
         "lot_sqft": 4500, "year_built": 1948, "condition": "fair",
         "neighborhood": "lents", "price_per_sqft": 310.00, "lat": 45.4840, "lon": -122.5760},
        {"address": "789 SE Harold St, Portland, OR", "sale_date": "2025-06-01",
         "sale_price": 420000, "sqft": 1400, "beds": 3, "baths": 2.0,
         "lot_sqft": 6000, "year_built": 1955, "condition": "good",
         "neighborhood": "lents", "price_per_sqft": 300.00, "lat": 45.4850, "lon": -122.5790},
    ]
    (comps_dir / "lents-comps.json").write_text(json.dumps(comps))
    return comps_dir


def test_load_comps_returns_list(tmp_path):
    comps_dir = _write_sample_comps(tmp_path)
    loader = RealCompLoader(comps_dir=comps_dir)
    result = loader.load_comps("lents")
    assert isinstance(result, list)
    assert len(result) == 3


def test_load_comps_filters_by_date(tmp_path):
    comps_dir = _write_sample_comps(tmp_path)
    loader = RealCompLoader(comps_dir=comps_dir)
    result = loader.load_comps("lents", months_back=6, reference_date=date(2026, 4, 8))
    assert len(result) == 2


def test_load_comps_filters_by_count(tmp_path):
    comps_dir = _write_sample_comps(tmp_path)
    loader = RealCompLoader(comps_dir=comps_dir)
    result = loader.load_comps("lents", count=2)
    assert len(result) == 2


def test_load_comps_returns_compsale_compatible(tmp_path):
    comps_dir = _write_sample_comps(tmp_path)
    loader = RealCompLoader(comps_dir=comps_dir)
    result = loader.load_comps("lents", count=1)
    comp = result[0]
    required = {"address", "sale_date", "sale_price", "sqft", "beds", "baths",
                "lot_sqft", "year_built", "condition", "distance_miles", "price_per_sqft"}
    assert required.issubset(set(vars(comp).keys()))


def test_load_comps_computes_distance(tmp_path):
    comps_dir = _write_sample_comps(tmp_path)
    loader = RealCompLoader(comps_dir=comps_dir)
    result = loader.load_comps("lents", subject_lat=45.4835, subject_lon=-122.5770)
    for comp in result:
        assert comp.distance_miles >= 0
