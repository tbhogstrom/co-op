# Labor Tracker

Portland Housing Co-op tool for recording and reporting member labor hours per project.

## What It Does

Records daily labor hours by member, applies trade-based skill multipliers, and calculates each member's share of the weighted labor pool. Output feeds directly into the profit-splitter tool for distribution calculations.

## How Weighting Works

Not all hours count the same. A licensed plumber's hour generates more value than a general laborer's hour on a rehab project. The multiplier adjusts each member's share of the labor pool (40% of gross profit), not a dollar-per-hour rate.

### Trade Codes and Multipliers

| Code | Trade | Multiplier |
|------|-------|-----------|
| GEN | General Labor | 1.00x |
| PNT | Painting / Finish | 1.00x |
| OPS | Operations / Admin | 1.00x |
| PM | Project Management | 1.15x |
| FRM | Framing | 1.20x |
| CRP | Carpentry | 1.20x |
| ROF | Roofing | 1.20x |
| PLB | Plumbing | 1.30x |
| ELC | Electrical | 1.30x |
| HVC | HVAC | 1.30x |

### Example

Birch logs 400 hours of carpentry (1.2x) = 480 weighted hours. Member F logs 400 hours of painting (1.0x) = 400 weighted hours. Birch gets a larger share of the labor pool even though they worked the same raw hours, because carpentry commands a higher market rate.

## Usage

### Run with sample data

```
python labor_tracker.py
```

Loads 3 weeks of sample entries for a 6-member project with realistic task descriptions.

### JSON output

```
python labor_tracker.py --json
```

### Custom data directory

```
python labor_tracker.py --data-dir /path/to/your/data
```

## Logging Rules

These rules match the labor-tracking-template.md policy:

1. **Log same day.** Do not batch a week of entries on Friday.
2. **Round to nearest 0.25 hour** (15-minute increments).
3. **One row per trade type per day.** If you do 4 hours of plumbing and 2 of general labor, that is two entries.
4. **Description is required.** Must be at least 10 characters. "Worked on the house" is not acceptable.
5. **Minimum loggable block: 1 hour.** No logging 15 minutes of checking on the site.
6. **Travel time: not logged.** Getting to the job site is on you.
7. **Verified weekly.** PM reviews and signs off on all hours weekly.

## Outputs

### Member Summary

Per-member breakdown showing:
- Total raw hours
- Total weighted hours
- Percentage of the labor pool
- Hours broken down by trade

### Profit Splitter Input

Call `tracker.profit_splitter_input("project_name")` to get data formatted for `tools/profit-splitter/profit_splitter.py`. Returns a dict mapping each member to their trade/hours tuples.

## Data Persistence

All data is stored in `labor_ledger.json` in the configured data directory. No database needed for Year 1.

```
data/
  labor_ledger.json    # All entries across all projects
```

## How This Connects to the Profit Split

```
Labor Tracker                      Profit Splitter
-----------                        ---------------
Records hours per member    --->   Receives weighted hours
Applies trade multipliers   --->   Calculates % of labor pool
                                   Splits 40% of GP accordingly
                                   Deducts advances
                                   Outputs net distribution
```

1. Members log hours daily in the labor tracker.
2. PM verifies hours weekly.
3. At project close, run `tracker.profit_splitter_input(project)`.
4. Feed that data into `profit_splitter.py` to calculate distributions.
5. Advances (from advance-tracker) are deducted from each member's labor share.
