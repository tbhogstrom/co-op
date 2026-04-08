import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'data-pipeline'))

from geocoding import haversine, normalize_address


def test_haversine_known_distance():
    portland_hall = (45.5152, -122.6784)
    pdx_airport = (45.5898, -122.5951)
    dist = haversine(*portland_hall, *pdx_airport)
    assert 5.0 < dist < 11.0, f"Expected ~6-7 miles, got {dist}"


def test_haversine_same_point():
    dist = haversine(45.5, -122.6, 45.5, -122.6)
    assert dist == 0.0


def test_haversine_returns_miles():
    dist = haversine(45.0, -122.0, 46.0, -122.0)
    assert 68.0 < dist < 70.0


def test_normalize_address_strips_unit():
    assert "123 SE MAIN ST" in normalize_address("123 SE Main St, Unit 4, Portland, OR")


def test_normalize_address_expands_abbreviations():
    result = normalize_address("123 se foster rd")
    assert "FOSTER" in result
