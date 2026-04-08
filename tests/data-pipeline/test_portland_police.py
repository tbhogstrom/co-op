import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'data-pipeline'))

import json
from fetchers.portland_police import compute_crime_trend, normalize_crime_score, PoliceFetcher


def test_compute_crime_trend_decreasing():
    trend = compute_crime_trend(prior_count=100, current_count=80)
    assert trend < 0


def test_compute_crime_trend_increasing():
    trend = compute_crime_trend(prior_count=80, current_count=100)
    assert trend > 0


def test_compute_crime_trend_stable():
    trend = compute_crime_trend(prior_count=100, current_count=100)
    assert trend == 0.0


def test_normalize_crime_score_range():
    assert normalize_crime_score(-50) == -10.0
    assert normalize_crime_score(50) == 10.0
    assert -10 <= normalize_crime_score(-8) <= 10


def test_normalize_crime_score_maps_correctly():
    score = normalize_crime_score(-20)
    assert -6 <= score <= -2


def test_police_fetcher_updates_neighborhood_json(tmp_path):
    hood_file = tmp_path / "lents.json"
    hood_data = {"name": "Lents", "characteristics": {"crime_trend": "Unknown"}}
    hood_file.write_text(json.dumps(hood_data))
    fetcher = PoliceFetcher(neighborhood_dir=tmp_path)
    fetcher.update_neighborhood_crime("lents", -3.5)
    updated = json.loads(hood_file.read_text())
    assert updated["characteristics"]["crime_trend"] == "Improving — down 3.5% YoY"
