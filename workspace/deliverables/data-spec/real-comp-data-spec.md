# Real Comparable Sales Data Specification

**Status:** ACTIONABLE — ready for data fetch  
**Date:** 2026-04-08  
**Authors:** Maven (coordinator), Reeves (real estate analyst), Ledger (CFO)  
**Purpose:** Replace all synthetic data in `/tools/` and `/data/` with real Portland property data  

---

## Table of Contents

1. [Data Needed — The Shopping List](#1-data-needed)
2. [Where to Get It — Public Sources](#2-public-sources)
3. [How the Tools Expect Data — Schemas](#3-tool-schemas)
4. [Gaps and Bridges](#4-gaps-and-bridges)
5. [Drop-In File Manifest](#5-file-manifest)

---

## 1. Data Needed

We need three categories of real data to replace what's currently synthetic.

### 1A. Comparable Sales Data (highest priority)

This is the core data the `comp-analyzer` and `arv-calculator` consume. We need **closed residential sales** in our 7 target neighborhoods.

| Field | Type | Required | Example | Notes |
|-------|------|----------|---------|-------|
| `address` | string | YES | `"4523 SE 92nd Ave, Portland, OR"` | Full street address |
| `sale_date` | string | YES | `"2025-08-15"` | ISO format YYYY-MM-DD |
| `sale_price` | int | YES | `345000` | Actual closed sale price in dollars |
| `sqft` | int | YES | `1050` | Above-grade living area |
| `beds` | int | YES | `3` | Bedroom count |
| `baths` | float | YES | `1.5` | Bathroom count (half baths = 0.5) |
| `lot_sqft` | int | YES | `5000` | Lot square footage |
| `year_built` | int | YES | `1952` | Year of original construction |
| `condition` | string | DERIVED | `"fair"` | See mapping below |
| `distance_miles` | float | COMPUTED | `0.23` | Computed at runtime from subject |
| `price_per_sqft` | float | COMPUTED | `328.57` | = sale_price / sqft |

**Coverage requirements:**

| Parameter | Requirement |
|-----------|-------------|
| **Neighborhoods** | `lents`, `cully`, `foster-powell`, `st-johns`, `woodstock`, `montavilla`, `parkrose` |
| **ZIP codes** | 97266, 97218, 97206, 97203, 97202, 97216, 97220, 97230, 97233 |
| **Date range** | 2025-04-01 through 2026-04-07 (trailing 12 months) |
| **Property types** | Single-family residential only (SFR) |
| **Target volume** | 30-50 closed sales per neighborhood (210-350 total) |
| **Price range** | $180,000 – $600,000 (our operating band) |
| **Sqft range** | 700 – 2,000 sqft (typical for target neighborhoods) |

**Condition mapping** (if source provides condition data — most won't):

| Source Description | Map To |
|-------------------|--------|
| Tear down, major structural failure, uninhabitable | `"poor"` |
| Dated, deferred maintenance, livable but needs work | `"fair"` |
| Standard condition, no major issues | `"average"` |
| Updated kitchen/bath, well-maintained | `"good"` |
| Recently renovated, modern finishes throughout | `"excellent"` |

If no condition data is available (common with public records), default to `"average"` and we'll flag it as a known limitation.

### 1B. Neighborhood Market Data

This feeds the `deal-scorer` neighborhood rubric and the `/data/portland-neighborhoods/*.json` files.

| Field | Type | Tool Key | Source Priority |
|-------|------|----------|-----------------|
| Median home price | int | `median_home_price` | Redfin, Zillow, RMLS reports |
| Median price/sqft | int | `median_price_per_sqft` | Redfin (available per neighborhood) |
| Median renovated price/sqft | int | `median_renovated_price_per_sqft` | Filter comps to "excellent" condition |
| 1-year price change % | float | `price_change_1yr_pct` | Redfin, Zillow Research |
| 3-year price change % | float | `price_change_3yr_pct` | Redfin, Zillow Research |
| Avg days on market | int | `avg_days_on_market` | Redfin, RMLS public reports |
| Active listings count | int | `active_listings` | Redfin, Zillow (snapshot) |
| Distressed listing % | float | `distressed_listing_pct` | Foreclosure.com, county records |
| Foreclosure rate % | float | `foreclosure_rate_pct` | ATTOM Data, county records |
| Months of inventory | float | `months_of_inventory` | = active_listings / closed_per_month |
| Population | int | `population` | Census/ACS 2024 |
| Median household income | int | `median_household_income` | Census/ACS 2024 |
| Owner-occupied % | float | `owner_occupied_pct` | Census/ACS 2024 |
| Walkability score | int (0-100) | `walkability_score` | Walk Score API |
| Transit score | int (0-100) | `transit_score` | Walk Score API (transit sub-score) |
| School rating avg | float (1-10) | `school_rating_avg` | GreatSchools API |
| Crime rate trend | numeric | `crime_rate_trend` | Portland Police open data |
| Development pipeline score | int (0-100) | `development_pipeline_score` | Manual — see note below |

**Deal-scorer specific fields** (derived from above for neighborhood scoring input):

| Scorer Key | Derivation |
|------------|------------|
| `median_home_price_ratio` | = neighborhood median / metro median ($485,000) |
| `appreciation_3yr_pct` | = `price_change_3yr_pct` directly |
| `days_on_market_avg` | = `avg_days_on_market` directly |
| `distressed_density_pct` | = `distressed_listing_pct` directly |
| `crime_rate_trend` | Positive = improving. Scale: -10 to +10. Map YoY % change. |
| `transit_score` | 0-100, direct from Walk Score |
| `school_rating` | 1-10, direct from GreatSchools |
| `development_pipeline_score` | 0-100, manually assessed (no public API) |
| `walkability_score` | 0-100, direct from Walk Score |

### 1C. Property Assessor & Public Records Data

This feeds the `MultnomahAssessor` and `PortlandMapsLookup` stubs in `data_sources.py`.

**Assessor record fields:**

| Field | Type | Source |
|-------|------|--------|
| `property_id` | string | County assessor (`R######`) |
| `address` | string | County assessor |
| `owner_name` | string | County assessor (public record) |
| `assessed_value` | int | County assessor |
| `market_value` | int | County assessor (real market value) |
| `tax_year` | int | County assessor |
| `annual_tax` | float | County assessor |
| `lot_sqft` | int | County assessor |
| `year_built` | int | County assessor |
| `zoning` | string | County assessor / PortlandMaps |
| `legal_description` | string | County assessor |

**PortlandMaps record fields:**

| Field | Type | Source |
|-------|------|--------|
| `address` | string | PortlandMaps |
| `state_id` | string | PortlandMaps (e.g., `1N2E24AB 01200`) |
| `zoning` | string | PortlandMaps (R5, R7, R2.5, CM1, etc.) |
| `comprehensive_plan` | string | PortlandMaps |
| `flood_zone` | string | PortlandMaps / FEMA |
| `seismic_zone` | string | PortlandMaps |
| `permits_last_5yr` | int | PortlandMaps permits search |
| `open_permits` | int | PortlandMaps permits search |
| `liens` | int | PortlandMaps / county recorder |
| `lien_total` | float | PortlandMaps / county recorder |
| `neighborhood_association` | string | PortlandMaps |

---

## 2. Public Sources

### 2A. Comparable Sales — Primary Sources

#### Multnomah County Assessment & Taxation (FREE, no API key)
- **URL:** https://multcoproptax.com/Property-Search
- **What you get:** Assessed value, real market value, tax amount, lot size, year built, zoning, owner name, property ID, legal description
- **What you DON'T get:** Sale price (sometimes), sale date, sqft living area, beds/baths, condition
- **Access method:** Web search by address, account number, or owner name. No bulk API.
- **Bulk option:** Download the full assessment roll (updated annually):
  - https://www.multco.us/assessment-taxation/data-download
  - CSV format, ~300K records, includes: property_id, situs_address, real_market_value, assessed_value, tax_amount, lot_size, year_built, zoning
  - **This is your best bulk source for assessor data.**

#### PortlandMaps.com API (FREE, no API key for basic queries)
- **URL:** https://www.portlandmaps.com/api/
- **Documentation:** https://www.portlandmaps.com/api/documentation/
- **Key endpoints:**
  - `/detail/{state_id}` — Full property detail
  - `/suggest/{address}` — Address autocomplete / lookup
  - `/permits/{state_id}` — Permit history
  - `/zoning/{state_id}` — Zoning designation and overlays
- **What you get:** State ID, zoning, comprehensive plan designation, flood zone, permits, neighborhood association, some property characteristics
- **What you DON'T get:** Sale price, beds/baths, interior sqft reliably
- **Rate limits:** Undocumented but reasonable for our volume (~350 lookups)
- **Access method:** REST API, JSON responses, no auth required for basic queries

#### Redfin (FREE, no API key needed for scraping public data)
- **URL:** https://www.redfin.com/city/30772/OR/Portland/filter/
- **What you get:** Sale price, sale date, sqft, beds, baths, lot size, year built, property type, days on market, status, price/sqft
- **Neighborhood pages (use these for market stats):**
  - Lents: https://www.redfin.com/neighborhood/350132/OR/Portland/Lents
  - Cully: https://www.redfin.com/neighborhood/350070/OR/Portland/Cully
  - Foster-Powell: https://www.redfin.com/neighborhood/350089/OR/Portland/Foster-Powell
  - St. Johns: https://www.redfin.com/neighborhood/350179/OR/Portland/St-Johns
  - Woodstock: https://www.redfin.com/neighborhood/350219/OR/Portland/Woodstock
  - Montavilla: https://www.redfin.com/neighborhood/350140/OR/Portland/Montavilla
  - Parkrose: https://www.redfin.com/neighborhood/350154/OR/Portland/Parkrose
- **Bulk download:** Redfin Data Center (https://www.redfin.com/news/data-center/) provides CSV downloads of market stats by neighborhood. Also allows download of recently sold properties.
- **Sold homes filter:** Add `/sold-last-1-year/` to neighborhood URL for closed sales
- **Access method:** Browser for manual, or scrape the download links. Redfin's data downloads are explicitly public.

#### Zillow / Zillow Research (FREE)
- **URL:** https://www.zillow.com/research/data/
- **What you get:** Median home values (ZHVI), price per sqft, rental estimates, historical appreciation by ZIP code and neighborhood
- **Bulk downloads:**
  - ZHVI (Zillow Home Value Index) by ZIP: CSV download
  - Price per square foot by ZIP: CSV download
  - URL: https://www.zillow.com/research/data/ → select "Home Values" → geography "ZIP Code"
- **Best for:** Appreciation rates, median values, price-per-sqft trends
- **Individual properties:** https://www.zillow.com/homes/Portland-OR/ — search by address for Zestimate, sale history, tax records, beds/baths/sqft

#### Oregon ORMAP / County GIS Data (FREE)
- **URL:** https://www.oregonmap.org/
- **What you get:** Parcel boundaries, tax lot data, GIS property records
- **Also:** Multnomah County GIS: https://gis.multco.us/
- **Format:** Shapefile/GeoJSON — useful for lot boundaries and zoning overlays

### 2B. Neighborhood Market Stats

#### Walk Score API (FREE tier available)
- **URL:** https://www.walkscore.com/professional/api.php
- **What you get:** Walk Score (0-100), Transit Score (0-100), Bike Score (0-100) per address
- **Free tier:** 5,000 requests/day — more than enough
- **Access method:** REST API, requires free API key signup
- **Direct lookup (no API):** https://www.walkscore.com/score/{address} — scrape the page
- **Neighborhood pages:**
  - https://www.walkscore.com/OR/Portland/Lents
  - https://www.walkscore.com/OR/Portland/Cully
  - etc.

#### GreatSchools API (FREE, requires key)
- **URL:** https://www.greatschools.org/api/
- **What you get:** School ratings (1-10) by location, school type, grade level
- **Access method:** REST API, free API key
- **Direct pages (no API):**
  - https://www.greatschools.org/oregon/portland/ — then filter by neighborhood/ZIP

#### Portland Police Bureau Open Data (FREE)
- **URL:** https://www.portland.gov/police/open-data
- **What you get:** Crime incident data, offense counts by neighborhood, year-over-year trends
- **Bulk download:** CSV of all incidents, filterable by date/neighborhood
- **Direct:** https://public.tableau.com/app/profile/portlandpolicebureau — interactive dashboards
- **What we need:** Total offenses by neighborhood for 2024 vs 2025 to compute YoY trend

#### U.S. Census / American Community Survey (FREE)
- **URL:** https://data.census.gov/
- **What you get:** Population, median household income, owner-occupied %, renter %
- **Access method:** Search by census tract or ZIP code
- **API:** https://api.census.gov/ — free, no key required for basic queries
- **Key tables:**
  - B25003: Tenure (owner vs renter)
  - B19013: Median household income
  - B01001: Population
- **Geography:** Census tracts map roughly to neighborhoods. ZIP code tabulation areas (ZCTAs) are the easiest proxy.

### 2C. Distressed Property Sources

#### Foreclosure.com (FREE basic access)
- **URL:** https://www.foreclosure.com/Portland-OR/
- **What you get:** Pre-foreclosure, auction, bank-owned/REO listings
- **Filterable by:** ZIP code, price range, property type

#### Multnomah County Recorder (FREE)
- **URL:** https://multco-web.tylerhost.net/recorder/web/
- **What you get:** Lis pendens (foreclosure notices), liens, deed transfers
- **Access method:** Search by name, document type, or date range

#### Portland Bureau of Development Services (FREE)
- **URL:** https://www.portland.gov/bds/code-enforcement
- **What you get:** Code violation properties, enforcement actions
- **Also:** https://www.portlandmaps.com/ — permits and code cases searchable by address

#### Property Tax Delinquency — Multnomah County (FREE)
- **URL:** https://multcoproptax.com/ — search individual accounts
- **Bulk:** Tax delinquency lists available via public records request
- **What you get:** Properties with unpaid taxes (potential motivated sellers)

---

## 3. Tool Schemas — Exact Format Required

### 3A. Comp Sales JSON (for `comp-analyzer` and `arv-calculator`)

Drop real comp data into: **`data/comp-sales/`** (new directory)

**File naming:** `{neighborhood}-comps.json` (e.g., `lents-comps.json`)

**Format — array of objects:**

```json
[
  {
    "address": "4523 SE 92nd Ave, Portland, OR",
    "sale_date": "2025-08-15",
    "sale_price": 345000,
    "sqft": 1050,
    "beds": 3,
    "baths": 1.0,
    "lot_sqft": 5000,
    "year_built": 1952,
    "condition": "fair",
    "neighborhood": "lents"
  },
  ...
]
```

**Notes:**
- `condition` can be omitted — tools will default to `"average"`
- `distance_miles` is NOT in the raw data — `comp_analyzer.py` will compute it at runtime when comparing against a subject property (requires geocoding or manual entry; see Gaps section)
- `price_per_sqft` is NOT in the raw data — computed at runtime as `sale_price / sqft`
- `neighborhood` is an addition to the current comp schema — needed to filter comps by neighborhood when loading from file instead of generating synthetically

**One file per neighborhood, 7 files total:**

```
data/comp-sales/
  lents-comps.json
  cully-comps.json
  foster-powell-comps.json
  st-johns-comps.json
  woodstock-comps.json
  montavilla-comps.json
  parkrose-comps.json
```

### 3B. Neighborhood Profile JSON (for `deal-scorer` and general reference)

**Overwrite existing files in:** `data/portland-neighborhoods/{name}.json`

Keep the exact same schema that's already there. Here's a complete field map with data source for each:

```json
{
  "name": "Lents",
  "quadrant": "SE",
  "zip_codes": ["97266"],
  "boundaries": {
    "north": "SE Powell Blvd",
    "south": "SE Woodstock Blvd / city limits",
    "east": "SE 111th Ave",
    "west": "SE 82nd Ave"
  },
  "market_data": {
    "median_home_price": 365000,         // SOURCE: Redfin neighborhood page
    "median_price_per_sqft": 285,        // SOURCE: Redfin neighborhood page
    "median_renovated_price_per_sqft": 310, // SOURCE: Filter Redfin comps to recently renovated
    "price_change_1yr_pct": 3.2,         // SOURCE: Redfin or Zillow Research
    "price_change_3yr_pct": 12.5,        // SOURCE: Redfin or Zillow Research ZHVI
    "avg_days_on_market": 28,            // SOURCE: Redfin neighborhood stats
    "active_listings": 45,               // SOURCE: Redfin (snapshot count)
    "distressed_listing_pct": 8.5,       // SOURCE: Foreclosure.com count / active listings
    "foreclosure_rate_pct": 1.2,         // SOURCE: County recorder lis pendens
    "months_of_inventory": 2.1           // SOURCE: active_listings / (closed_per_month)
  },
  "demographics": {
    "population": 20500,                 // SOURCE: Census ACS table B01001 by ZCTA
    "median_household_income": 52000,    // SOURCE: Census ACS table B19013 by ZCTA
    "owner_occupied_pct": 55,            // SOURCE: Census ACS table B25003 by ZCTA
    "renter_pct": 45                     // SOURCE: 100 - owner_occupied_pct
  },
  "characteristics": {
    "housing_stock": "...",              // SOURCE: Narrative — keep existing or update
    "typical_sqft_range": [900, 1400],   // SOURCE: Redfin or derived from comps
    "typical_lot_sqft": 5000,            // SOURCE: County assessor bulk data
    "typical_beds": [2, 3],              // SOURCE: Redfin or derived from comps
    "typical_year_built_range": [1940, 1965], // SOURCE: County assessor bulk data
    "transit_access": "...",             // SOURCE: Narrative from Walk Score
    "walkability_score": 62,             // SOURCE: Walk Score API or walkscore.com
    "school_rating_avg": 4.5,            // SOURCE: GreatSchools
    "crime_trend": "Improving — down 8% YoY", // SOURCE: Portland Police open data
    "development_pipeline": "..."        // SOURCE: Narrative — Portland BPS / news
  },
  "investment_thesis": "...",            // SOURCE: Keep existing (Reeves-authored)
  "risk_factors": ["..."],               // SOURCE: Keep existing (Reeves-authored)
  "data_sources": [
    "Multnomah County Assessor (public records)",
    "PortlandMaps.com",
    "Redfin sold data (April 2025 - April 2026)",
    "Walk Score (walkscore.com)",
    "GreatSchools.org",
    "U.S. Census ACS 2024",
    "Portland Police Bureau open data"
  ],
  "last_updated": "2026-04-08"
}
```

### 3C. Metro Summary JSON

**Overwrite:** `data/portland-neighborhoods/metro-summary.json`

Same schema as current file. Key fields to update with real data:

```
metro_market_data:
  median_home_price        → Redfin Portland metro page
  median_price_per_sqft    → Redfin
  avg_days_on_market       → Redfin
  months_of_inventory      → Redfin
  price_change_1yr_pct     → Redfin or Zillow ZHVI
  price_change_3yr_pct     → Zillow ZHVI
  total_active_listings    → Redfin
  new_listings_per_month   → Redfin
  closed_sales_per_month   → Redfin
  list_to_sale_ratio_pct   → Redfin
  pct_selling_above_asking → Redfin

distressed_market:
  distressed_listing_pct_metro → Foreclosure.com / ATTOM
  foreclosure_rate_pct         → County recorder data
  pre_foreclosure_count        → County recorder lis pendens
  bank_owned_reo_count         → Foreclosure.com
  short_sale_count             → Foreclosure.com
  
financing_environment:
  avg_30yr_fixed_rate    → Freddie Mac PMMS (https://www.freddiemac.com/pmms)
  avg_15yr_fixed_rate    → Freddie Mac PMMS
  fha_limit_multnomah    → HUD (https://entp.hud.gov/idapp/html/hicostlook.cfm)
  conforming_limit       → FHFA (https://www.fhfa.gov/data/conforming-loan-limit)
```

### 3D. Distressed Listings JSON

**Overwrite:** `data/property-listings/distressed-listings.json`

Keep same schema. Source each field:

```json
{
  "id": "PDX-2026-001",                  // Our internal ID
  "address": "4523 SE 92nd Ave",          // Listing source
  "city": "Portland",
  "state": "OR",
  "zip": "97266",                         // Address lookup
  "neighborhood": "Lents",               // Address → neighborhood mapping
  "quadrant": "SE",
  "list_price": 245000,                   // Listing source
  "original_list_price": 265000,          // Listing source (price history)
  "status": "active",                     // Listing source
  "listing_type": "REO",                  // Listing source / county recorder
  "days_on_market": 45,                   // Listing source
  "sqft": 1050,                           // Listing or assessor records
  "beds": 3,                              // Listing source
  "baths": 1.0,                           // Listing source
  "lot_sqft": 5000,                       // Assessor records
  "year_built": 1952,                     // Assessor records
  "stories": 1.0,                         // Listing source
  "garage": "detached 1-car",             // Listing source
  "condition": "poor",                    // Listing description interpretation
  "condition_notes": "...",               // Listing description / photos
  "estimated_rehab_range": [60000, 85000], // Manual estimate by Harlan
  "zoning": "R5",                         // PortlandMaps
  "property_type": "Single Family",       // Listing / assessor
  "tax_assessed_value": 210000,           // County assessor
  "annual_property_tax": 3150.00,         // County assessor
  "hoa": null,                            // Listing source
  "title_notes": "Clean title...",        // County recorder / title company
  "source": "Redfin + County Assessor",   // Actual source attribution
  "last_updated": "2026-04-08"
}
```

### 3E. Watchlist JSON

**Overwrite:** `data/property-listings/watchlist.json`

Same schema. Sources: county tax delinquency records, Portland BDS code enforcement, county recorder lis pendens.

---

## 4. Gaps and Bridges

### Gap 1: Condition Data
- **Problem:** Public records and most listing sources do NOT provide a standardized condition rating. County assessor has no condition field. Redfin/Zillow descriptions are free-text.
- **Bridge:** Default all comps to `"average"` unless the listing explicitly mentions renovation status. For distressed listings, use listing photos and description to manually assign `"poor"` or `"fair"`. Document the methodology.
- **Impact:** Low. The comp-analyzer adjustment engine is designed to work with condition as one of many signals. A uniform `"average"` default still produces usable adjusted values.

### Gap 2: Distance Between Properties
- **Problem:** `comp_analyzer.py` currently generates synthetic `distance_miles`. Real data needs real distances.
- **Bridge options (pick one):**
  1. **Geocode addresses → compute Haversine distance at runtime.** Use the free Nominatim/OpenStreetMap geocoder (https://nominatim.openstreetmap.org/search?q=ADDRESS&format=json) to get lat/lon, then compute distance. 1 request/second rate limit.
  2. **Assign approximate distance based on block grid.** Portland's grid is ~20 blocks/mile NS, ~16 blocks/mile EW. Parse street numbers and compute approximate distance. No API needed.
  3. **Pre-compute and store as a field.** Geocode all comps once, compute distances to centroid of each neighborhood, store in the JSON.
- **Recommendation:** Option 3 — geocode once, add `"lat"` and `"lon"` fields to each comp record. Modify `comp_analyzer.py` to compute distance at runtime using Haversine formula. Minimal code change (~10 lines).
- **New fields to add to comp schema:**
  ```json
  { "lat": 45.4828, "lon": -122.5772 }
  ```

### Gap 3: Interior Sqft / Beds / Baths from Assessor
- **Problem:** Multnomah County assessor bulk download includes lot_sqft, year_built, and value — but NOT interior sqft, beds, or baths reliably.
- **Bridge:** Use Redfin or Zillow as primary source for sqft/beds/baths, cross-reference with assessor data for value/lot/year_built. Merge the two datasets by address.
- **Merge strategy:**
  ```
  Redfin provides:  address, sale_price, sale_date, sqft, beds, baths, lot_sqft, year_built
  Assessor provides: address, assessed_value, market_value, annual_tax, lot_sqft, year_built, zoning, owner, property_id
  PortlandMaps:      zoning, permits, liens, flood_zone, comprehensive_plan
  
  Join on: normalized address
  ```

### Gap 4: Crime Rate as Numeric Score
- **Problem:** Portland Police data gives raw offense counts. Our deal-scorer wants a numeric trend value on a -10 to +10 scale.
- **Bridge:** Compute YoY change in total offenses per neighborhood:
  ```
  crime_rate_trend = -1 * (offenses_2025 - offenses_2024) / offenses_2024 * 100
  ```
  Then map to scale: 0% change = 0, -10% (improving) = +5, -20% = +10, +10% (worsening) = -5, etc. Cap at [-10, +10].

### Gap 5: Development Pipeline Score
- **Problem:** No public API provides a 0-100 "development pipeline" score.
- **Bridge:** Manual assessment by Reeves. Score 0-100 based on:
  - Active construction permits in area (PortlandMaps)
  - Major development projects announced (Portland BPS: https://www.portland.gov/bps/planning/projects)
  - Infrastructure investment (PBOT: https://www.portland.gov/transportation/capital-projects)
  - Zoning changes in progress
- **This is the one field that requires human judgment. Everything else can be automated.**

### Gap 6: RMLS (Regional Multiple Listing Service) Data
- **Problem:** RMLS is the definitive source for Portland sales data, but access requires a licensed real estate agent or broker. No public API.
- **Bridge:** Use Redfin as proxy. Redfin sources from RMLS and provides most of the same data publicly. For any data validation, ask a licensed agent contact to pull specific comps (verify a sample of 10-20 records against RMLS to calibrate).

### Gap 7: Renovated Price Per Square Foot
- **Problem:** `median_renovated_price_per_sqft` is needed for neighborhood profiles and the ARV calculator, but there's no standard "renovated" filter in public data.
- **Bridge:** On Redfin, filter sold homes to those with "Remodeled" or "Updated" in description, or filter by year of last renovation. Take median price/sqft of those results. If insufficient data, use: `median_renovated_ppsf = median_ppsf * 1.08 to 1.12` (8-12% renovation premium, calibrated from current synthetic data).

---

## 5. Drop-In File Manifest

When you fetch the data, create/overwrite these files:

```
data/
├── comp-sales/                          ← NEW DIRECTORY
│   ├── lents-comps.json                 ← 30-50 records
│   ├── cully-comps.json                 ← 30-50 records
│   ├── foster-powell-comps.json         ← 30-50 records
│   ├── st-johns-comps.json             ← 30-50 records
│   ├── woodstock-comps.json            ← 30-50 records
│   ├── montavilla-comps.json           ← 30-50 records
│   └── parkrose-comps.json             ← 30-50 records
│
├── portland-neighborhoods/
│   ├── lents.json                       ← UPDATE with real market stats
│   ├── cully.json                       ← UPDATE
│   ├── foster-powell.json               ← UPDATE
│   ├── st-johns.json                    ← UPDATE
│   ├── woodstock.json                   ← UPDATE
│   ├── montavilla.json                  ← UPDATE
│   ├── parkrose.json                    ← UPDATE
│   └── metro-summary.json              ← UPDATE
│
├── property-listings/
│   ├── distressed-listings.json         ← UPDATE with real listings
│   └── watchlist.json                   ← UPDATE with real leads
│
└── assessor/                            ← NEW DIRECTORY (optional but recommended)
    └── multnomah-bulk-extract.csv       ← County assessor bulk download
```

### Code Changes Required

After data drop, `tools/comp-analyzer/data_sources.py` needs modification:

1. **Add `RealCompLoader` class** that reads from `data/comp-sales/{neighborhood}-comps.json` instead of generating synthetic data
2. **Replace `SyntheticMLSGenerator` calls** in `comp_analyzer.py` with `RealCompLoader` calls
3. **Add geocoding/distance computation** if lat/lon fields are included in comp data
4. **Replace `MultnomahAssessor` stub** with a loader that reads from `data/assessor/` or performs live PortlandMaps API lookups
5. **Replace `PortlandMapsLookup` stub** with live API calls to `https://www.portlandmaps.com/api/`

Estimated code changes: ~100 lines in `data_sources.py`, ~20 lines in `comp_analyzer.py`. No changes needed to `arv_calculator.py`, `deal_scorer.py`, or `scoring_rubric.py` — they consume the same JSON schema regardless of whether the data is real or synthetic.

---

## Fetch Priority Order

If doing this incrementally, prioritize in this order:

| Priority | Data | Impact | Effort |
|----------|------|--------|--------|
| **P0** | Comp sales (Redfin sold data, 7 neighborhoods) | Unlocks real comp analysis + ARV | Medium — manual download + format |
| **P0** | Neighborhood market stats (Redfin + Zillow) | Unlocks real deal scoring | Low — available on web pages |
| **P1** | Assessor bulk data (Multnomah County download) | Enables real property lookups | Low — single CSV download |
| **P1** | Walk Score + GreatSchools | Real neighborhood scores | Low — API calls or web scrape |
| **P2** | Distressed listings (Redfin + Foreclosure.com) | Real deal pipeline | Medium — manual curation |
| **P2** | Crime data (Portland Police) | Real crime trends | Low — CSV download |
| **P3** | PortlandMaps API integration | Live property lookups | Medium — code changes needed |
| **P3** | Geocoding for distance computation | Accurate comp distances | Medium — API + code changes |

---

*This spec was produced as a coordination between Maven (project direction), Reeves (real estate data expertise), and Ledger (financial model requirements). All three tools — comp-analyzer, arv-calculator, and deal-scorer — were audited for exact schema requirements.*
