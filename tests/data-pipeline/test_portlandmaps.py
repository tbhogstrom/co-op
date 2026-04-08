import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'data-pipeline'))

import json
from fetchers.portlandmaps import parse_portlandmaps_response, PortlandMapsFetcher, address_to_slug


def test_address_to_slug():
    assert address_to_slug("123 SE Foster Rd, Portland, OR") == "123-se-foster-rd-portland-or"
    assert address_to_slug("456 NE Cully Blvd #4") == "456-ne-cully-blvd-4"


def test_parse_portlandmaps_response():
    api_response = {
        "results": [{
            "address": "123 SE FOSTER RD",
            "state_id": "1S2E15AC 01200",
            "zoning": "R5",
            "comprehensive_plan": "Single-Dwelling Residential",
            "flood_zone": "X",
            "seismic": "moderate",
            "permits": [
                {"status": "final", "year": 2022},
                {"status": "final", "year": 2023},
                {"status": "issued", "year": 2025},
            ],
            "liens": [{"amount": 5000.00, "type": "tax"}],
            "neighborhood_association": "Foster-Powell NA",
        }]
    }
    info = parse_portlandmaps_response(api_response, "123 SE Foster Rd")
    assert info["address"] == "123 SE Foster Rd"
    assert info["zoning"] == "R5"
    assert info["permits_last_5yr"] == 3
    assert info["open_permits"] == 1
    assert info["liens"] == 1
    assert info["lien_total"] == 5000.00


def test_portlandmaps_fetcher_cache(tmp_path):
    fetcher = PortlandMapsFetcher(cache_dir=tmp_path)
    cached = {
        "address": "123 SE Foster Rd", "state_id": "1S2E15AC 01200",
        "zoning": "R5", "comprehensive_plan": "Single-Dwelling Residential",
        "flood_zone": "X", "seismic_zone": "moderate",
        "permits_last_5yr": 3, "open_permits": 1,
        "liens": 1, "lien_total": 5000.00,
        "neighborhood_association": "Foster-Powell NA",
    }
    slug = address_to_slug("123 SE Foster Rd")
    (tmp_path / f"{slug}.json").write_text(json.dumps(cached))
    result = fetcher.lookup_cached("123 SE Foster Rd")
    assert result is not None
    assert result["zoning"] == "R5"
