# Real Data Pipeline — Design Spec

**Date:** 2026-04-08
**Status:** Approved
**Source Spec:** `workspace/deliverables/data-spec/real-comp-data-spec.md`

## Goal

Replace synthetic data generation in the co-op's analysis tools with a real data pipeline that fetches, normalizes, and loads actual Portland market data. End state: run one command (`python pipeline.py --all`) and the entire `data/` directory is populated with real, current data that the existing tools consume unchanged.

## Scope

### In Scope
- 5 automated fetchers (Redfin CSV downloads, Multnomah County assessor bulk data, PortlandMaps API, Portland Police open data, distressed listing aggregation)
- 3 loader classes replacing stubs in `data_sources.py` (RealCompLoader, AssessorLoader, PortlandMapsLookup)
- Geocoding via Census Bureau API (free, no key)
- Schema normalization and validation
- CLI orchestrator with per-source and full-refresh modes
- Integration with existing tools (comp_analyzer, arv_calculator, deal_scorer)

### Out of Scope
- Walk Score API integration (requires API key)
- GreatSchools API integration (requires API key)
- Web scraping or ToS-violating data collection
- Changes to existing tool logic (they consume the same dataclass interfaces)

## Architecture

```
tools/data-pipeline/
├── pipeline.py              # Orchestrator CLI
├── config.py                # Neighborhoods, URLs, paths, rate limits
├── normalizer.py            # Schema validation and field normalization
├── geocoding.py             # Census Bureau geocoding + Haversine distance
├── fetchers/
│   ├── __init__.py
│   ├── redfin.py            # Redfin CSV download → comp-sales JSON
│   ├── assessor.py          # Multnomah County bulk CSV → assessor data
│   ├── portlandmaps.py      # PortlandMaps API → zoning/permits/liens
│   ├── portland_police.py   # Crime open data → neighborhood crime trends
│   └── distressed.py        # Cross-reference aggregation of distressed leads
└── loaders/
    ├── __init__.py
    ├── real_comp_loader.py  # RealCompLoader (replaces SyntheticMLSGenerator)
    ├── assessor_loader.py   # AssessorLoader (replaces MultnomahAssessor stub)
    └── portlandmaps_lookup.py  # PortlandMapsLookup (live API + cache)
```

### Data Flow

```
External Sources                    data/ directory                    Existing Tools
─────────────────                   ──────────────                     ──────────────
Redfin CSV URLs ──→ redfin.py ──→ data/comp-sales/*.json ──→ RealCompLoader ──→ comp_analyzer.py
                                                                                  arv_calculator.py

Multnomah County ──→ assessor.py ──→ data/assessor/*.json ──→ AssessorLoader ──→ deal_scorer.py
Bulk Download                       data/assessor/*.csv

PortlandMaps API ──→ portlandmaps.py ──→ data/portlandmaps/*.json ──→ PortlandMapsLookup

Portland Police ──→ portland_police.py ──→ updates data/portland-neighborhoods/*.json
Open Data                                  (crime_trend field)

Cross-reference ──→ distressed.py ──→ data/property-listings/distressed-listings.json
(assessor + portlandmaps + comps)     data/property-listings/watchlist.json

Census Bureau ──→ geocoding.py ──→ lat/lon added to comp-sales JSON
Geocoding API
```

## Component Details

### Fetchers

#### redfin.py
- **Source:** Redfin's `/stingray/api/gis-csv` download endpoint
- **Parameters per neighborhood:** ZIP codes, sold status, date range (trailing 12 months), price range ($180K–$600K)
- **Output:** `data/comp-sales/{neighborhood}-comps.json` — array of CompSale-schema records
- **Field mapping:** Redfin CSV headers → CompSale fields (address, sale_date, sale_price, sqft, beds, baths, lot_sqft, year_built)
- **Condition heuristic:** Default `"average"`. If listing remarks contain fixer/as-is/estate/distressed keywords → `"fair"` or `"poor"`
- **Rate limiting:** 2–3 second delay between requests
- **Expected volume:** 30–50 records per neighborhood, 210–350 total

#### assessor.py
- **Source:** `https://www.multco.us/assessment-taxation/data-download` (bulk CSV)
- **Processing:** Download, filter by target ZIP codes, parse into AssessorRecord schema
- **Output:** `data/assessor/multnomah-bulk-extract.csv` (filtered raw) and `data/assessor/multnomah-by-neighborhood/{neighborhood}.json`
- **Fields:** property_id, address, owner, assessed_value, market_value, tax_year, annual_tax, lot_sqft, year_built, zoning, legal_description
- **Refresh frequency:** Monthly (source updates quarterly)

#### portlandmaps.py
- **Source:** `https://www.portlandmaps.com/api/` (no auth required for basic queries)
- **Input:** List of addresses (from comp sales, watchlist, or CLI argument)
- **Output:** `data/portlandmaps/{address-slug}.json` per property
- **Fields:** zoning, comprehensive_plan, flood_zone, seismic_zone, permits_last_5yr, open_permits, liens, lien_total, neighborhood_association
- **Caching:** Check local cache before hitting API

#### portland_police.py
- **Source:** Portland Police Bureau open data portal (CSV/GeoJSON)
- **Processing:** Compute year-over-year crime count change per neighborhood, normalize to [-10, +10] scale
- **Output:** Updates `crime_trend` field in `data/portland-neighborhoods/{name}.json`

#### distressed.py
- **Source:** Cross-references assessor data (tax delinquency), PortlandMaps (code violations, open liens), and comp data (below-market sales)
- **Filters:** Deal guardrails ($180K–$200K ceiling, target neighborhoods)
- **Output:** `data/property-listings/distressed-listings.json` and `data/property-listings/watchlist.json`
- **Dependency:** Runs after assessor + portlandmaps fetchers

### Loaders

#### RealCompLoader (replaces SyntheticMLSGenerator)
- **Interface:** `load_comps(neighborhood, sqft_target, beds, baths, radius_miles, months_back, count, reference_date) -> List[CompSale]`
- **Source:** Reads `data/comp-sales/{neighborhood}-comps.json`
- **Filtering:** Date range, price range, radius (if geocoded with lat/lon)
- **Sorting:** By relevance to subject property (sqft similarity, recency, distance)
- **Drop-in replacement:** Same method signature and return type as `SyntheticMLSGenerator.generate_comps()`

#### AssessorLoader (replaces MultnomahAssessor stub)
- **Interface:** `lookup(address) -> AssessorRecord`
- **Source:** Reads `data/assessor/multnomah-by-neighborhood/*.json`
- **Address matching:** Normalize street suffixes (St/Street, Ave/Avenue), directionals (N/North), unit numbers

#### PortlandMapsLookup (replaces stub)
- **Interface:** `lookup(address) -> PortlandMapsInfo`
- **Source:** Cache-first from `data/portlandmaps/{address-slug}.json`, fallback to live API
- **Returns:** Same `PortlandMapsInfo` dataclass as the existing stub

### Geocoding

- **Source:** Census Bureau Geocoding API (`https://geocoding.geo.census.gov/geocoder/`) — free, no key
- **Functions:** `geocode(address, city, state) -> (lat, lon)` and `haversine(lat1, lon1, lat2, lon2) -> float` (miles)
- **Integration:** Batch-geocodes all comps after Redfin fetch, stores lat/lon in the comp JSON files
- **Rate limiting:** Respect Census API limits

### Normalizer

- **Schema validation:** Ensures all fetched records have required fields, correct types, values in expected ranges
- **Field normalization:** Redfin CSV headers → canonical field names, date format standardization, address normalization
- **Merge logic:** Combines Redfin comp data with assessor records by fuzzy address match (Redfin has beds/baths/condition; assessor has assessed_value/zoning)
- **Default fills:** Missing condition → `"average"`, missing lot_sqft → assessor value or neighborhood median

### Config

- **Neighborhood definitions:** 7 neighborhoods with name, ZIP codes, Redfin region identifiers, bounding coordinates
- **Target parameters:** Price range ($180K–$600K for comps), date range (trailing 12 months), sqft range (700–2,000)
- **File paths:** All `data/` subdirectories
- **Rate limits:** Per-source delay settings

### Orchestrator (pipeline.py)

```
Usage:
  python pipeline.py --all                              # Full refresh
  python pipeline.py --source redfin                    # Redfin comps only
  python pipeline.py --source assessor                  # Assessor bulk data only
  python pipeline.py --source portlandmaps --addresses file.json
  python pipeline.py --source police                    # Crime data only
  python pipeline.py --source distressed                # Distressed aggregation
  python pipeline.py --geocode                          # Geocode all comps
  python pipeline.py --validate                         # Schema validation only
```

**Execution order for `--all`:** assessor → redfin → geocode → portlandmaps → police → distressed → validate

Each step logs progress, skips gracefully on failure (with warning), and reports summary at end.

## Integration with Existing Tools

### Changes to data_sources.py
- Add imports for `RealCompLoader`, `AssessorLoader`, `PortlandMapsLookup` from `tools/data-pipeline/loaders/`
- Add `USE_REAL_DATA = True` flag (or detect presence of `data/comp-sales/` files)
- When real data available: route through real loaders. When not: fall back to synthetic (preserves dev/demo workflow)
- No changes to `CompSale`, `AssessorRecord`, or `PortlandMapsInfo` dataclasses — loaders produce the same types

### No changes needed
- `comp_analyzer.py` — consumes `List[CompSale]` regardless of source
- `arv_calculator.py` — consumes comp data and neighborhood profiles
- `deal_scorer.py` / `scoring_rubric.py` — consumes normalized neighborhood JSON and property data

## Dependencies

```
requests          # HTTP fetching for all external sources
pandas            # CSV parsing for assessor bulk data
```

All other functionality uses Python stdlib.

## Data Directory Structure (After Pipeline Run)

```
data/
├── comp-sales/                          # NEW — populated by redfin.py
│   ├── lents-comps.json
│   ├── cully-comps.json
│   ├── foster-powell-comps.json
│   ├── st-johns-comps.json
│   ├── woodstock-comps.json
│   ├── montavilla-comps.json
│   └── parkrose-comps.json
├── assessor/                            # NEW — populated by assessor.py
│   ├── multnomah-bulk-extract.csv
│   └── multnomah-by-neighborhood/
│       ├── lents.json
│       ├── cully.json
│       └── ... (7 files)
├── portlandmaps/                        # NEW — populated by portlandmaps.py
│   └── {address-slug}.json              # One per queried property
├── portland-neighborhoods/              # EXISTING — updated by police, merge
│   ├── lents.json
│   ├── cully.json
│   └── ... (7 files + metro-summary.json)
└── property-listings/                   # EXISTING — updated by distressed.py
    ├── distressed-listings.json
    └── watchlist.json
```
