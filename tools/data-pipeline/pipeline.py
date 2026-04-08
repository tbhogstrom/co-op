#!/usr/bin/env python3
"""CLI orchestrator for the Portland Housing Co-op real data pipeline.

Usage:
    python pipeline.py --all                    # Full refresh
    python pipeline.py --source redfin          # Redfin comps only
    python pipeline.py --source assessor        # Assessor bulk data
    python pipeline.py --source portlandmaps    # PortlandMaps (needs addresses)
    python pipeline.py --source police          # Crime data
    python pipeline.py --source distressed      # Distressed aggregation
    python pipeline.py --geocode                # Geocode all comps
    python pipeline.py --validate               # Schema validation only
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from config import COMP_SALES_DIR, ASSESSOR_DIR, ASSESSOR_BY_NEIGHBORHOOD_DIR, PORTLANDMAPS_DIR, NEIGHBORHOODS

logger = logging.getLogger("data-pipeline")

EXECUTION_ORDER = ["assessor", "redfin", "geocode", "portlandmaps", "police", "distressed"]


def get_execution_order() -> list[str]:
    """Return the dependency-ordered execution sequence."""
    return list(EXECUTION_ORDER)


def run_assessor() -> dict:
    from fetchers.assessor import AssessorFetcher
    fetcher = AssessorFetcher()
    return fetcher.fetch_all()


def run_redfin() -> dict:
    from fetchers.redfin import RedfinFetcher
    fetcher = RedfinFetcher()
    return fetcher.fetch_all()


def run_geocode() -> dict:
    from geocoding import geocode
    import time
    from config import RATE_LIMITS

    summary = {}
    delay = RATE_LIMITS.get("census_geocoder", 1.0)

    for slug in NEIGHBORHOODS:
        comps_file = COMP_SALES_DIR / f"{slug}-comps.json"
        if not comps_file.exists():
            summary[slug] = 0
            continue

        with open(comps_file) as f:
            comps = json.load(f)

        geocoded = 0
        for comp in comps:
            if "lat" in comp and "lon" in comp and comp["lat"] and comp["lon"]:
                continue

            result = geocode(comp.get("address", ""))
            if result:
                comp["lat"] = result[0]
                comp["lon"] = result[1]
                geocoded += 1
                time.sleep(delay)

        with open(comps_file, "w") as f:
            json.dump(comps, f, indent=2)

        summary[slug] = geocoded
        logger.info("Geocoded %d/%d comps for %s", geocoded, len(comps), slug)

    return summary


def run_portlandmaps(addresses: list[str] = None) -> dict:
    from fetchers.portlandmaps import PortlandMapsFetcher
    fetcher = PortlandMapsFetcher()

    if addresses:
        results = fetcher.fetch_addresses(addresses)
        return {"fetched": sum(1 for v in results.values() if v is not None)}

    all_addresses = []
    for slug in NEIGHBORHOODS:
        comps_file = COMP_SALES_DIR / f"{slug}-comps.json"
        if comps_file.exists():
            with open(comps_file) as f:
                comps = json.load(f)
            all_addresses.extend(c.get("address", "") for c in comps if c.get("address"))

    if not all_addresses:
        logger.warning("No addresses found for PortlandMaps lookup")
        return {"fetched": 0}

    results = fetcher.fetch_addresses(all_addresses)
    return {"fetched": sum(1 for v in results.values() if v is not None)}


def run_police() -> dict:
    from fetchers.portland_police import PoliceFetcher
    fetcher = PoliceFetcher()
    return fetcher.fetch_all()


def run_distressed() -> dict:
    from fetchers.distressed import DistressedAggregator

    assessor_records = []
    if ASSESSOR_BY_NEIGHBORHOOD_DIR.exists():
        for slug in NEIGHBORHOODS:
            hood_file = ASSESSOR_BY_NEIGHBORHOOD_DIR / f"{slug}.json"
            if hood_file.exists():
                with open(hood_file) as f:
                    assessor_records.extend(json.load(f))

    portlandmaps_data = {}
    if PORTLANDMAPS_DIR.exists():
        for pm_file in PORTLANDMAPS_DIR.glob("*.json"):
            with open(pm_file) as f:
                data = json.load(f)
            address = data.get("address", "")
            if address:
                portlandmaps_data[address] = data

    agg = DistressedAggregator()
    return agg.aggregate(assessor_records, portlandmaps_data)


def run_validate() -> dict:
    from normalizer import validate_comp_record

    errors = {}
    total_valid = 0
    total_invalid = 0

    for slug in NEIGHBORHOODS:
        comps_file = COMP_SALES_DIR / f"{slug}-comps.json"
        if not comps_file.exists():
            continue

        with open(comps_file) as f:
            comps = json.load(f)

        slug_errors = []
        for i, comp in enumerate(comps):
            errs = validate_comp_record(comp)
            if errs:
                slug_errors.append({"index": i, "address": comp.get("address", "?"), "errors": errs})
                total_invalid += 1
            else:
                total_valid += 1

        if slug_errors:
            errors[slug] = slug_errors

    return {"valid": total_valid, "invalid": total_invalid, "errors": errors}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pipeline",
        description="Portland Housing Co-op real data pipeline orchestrator.",
    )
    parser.add_argument("--all", action="store_true", help="Run all fetchers in dependency order")
    parser.add_argument("--source", choices=["redfin", "assessor", "portlandmaps", "police", "distressed"],
                        help="Run a specific source fetcher")
    parser.add_argument("--geocode", action="store_true", help="Geocode all comp records")
    parser.add_argument("--validate", action="store_true", help="Validate all data files")
    parser.add_argument("--addresses", help="JSON file with addresses for portlandmaps lookup")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable debug logging")
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(name)s %(levelname)s %(message)s")

    if not any([args.all, args.source, args.geocode, args.validate]):
        parser.print_help()
        return 1

    results = {}

    if args.all:
        order = get_execution_order()
        for step in order:
            logger.info("=== Running: %s ===", step)
            try:
                if step == "assessor":
                    results[step] = run_assessor()
                elif step == "redfin":
                    results[step] = run_redfin()
                elif step == "geocode":
                    results[step] = run_geocode()
                elif step == "portlandmaps":
                    results[step] = run_portlandmaps()
                elif step == "police":
                    results[step] = run_police()
                elif step == "distressed":
                    results[step] = run_distressed()
            except Exception as e:
                logger.error("Step %s failed: %s", step, e)
                results[step] = {"error": str(e)}

        logger.info("=== Running: validate ===")
        results["validate"] = run_validate()

    elif args.source:
        source_map = {
            "redfin": run_redfin,
            "assessor": run_assessor,
            "portlandmaps": lambda: run_portlandmaps(
                json.loads(Path(args.addresses).read_text()) if args.addresses else None
            ),
            "police": run_police,
            "distressed": run_distressed,
        }
        results[args.source] = source_map[args.source]()

    elif args.geocode:
        results["geocode"] = run_geocode()

    elif args.validate:
        results["validate"] = run_validate()

    print("\n" + "=" * 60)
    print("Pipeline Results:")
    print("=" * 60)
    print(json.dumps(results, indent=2, default=str))

    return 0


if __name__ == "__main__":
    sys.exit(main())
