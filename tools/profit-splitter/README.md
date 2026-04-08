# Profit Splitter — Portland Housing Co-op

Financial tools for calculating profit distributions, tracking member equity, and managing labor advances.

## Tools

### `profit_splitter.py`

Main profit distribution calculator. Implements the approved 20/10/30/40 formula.

```bash
python3 profit_splitter.py              # Human-readable report with example data
python3 profit_splitter.py --json       # JSON output
python3 profit_splitter.py --sale-price 500000 --total-cost 420000  # Custom deal
```

**Inputs:** Gross profit, member capital accounts, member labor hours (by trade), trade multipliers.

**Outputs:** Per-member distribution breakdown showing reserves (20%), overhead (10%), capital share (30%), labor share (40%). Includes advance tracking — deducts advances from distributions and flags overdraws.

### `equity_tracker.py`

Member capital account ledger and advance tracking system.

```bash
python3 equity_tracker.py               # Full equity report with example lifecycle
python3 equity_tracker.py --json        # JSON output
```

**Tracks:** Buy-ins, additional contributions, profit allocations, distributions, labor advances, repayments.

## Formula

```
Gross Profit = Sale Price - Total Project Cost

  20% → Co-op Reserves
  10% → Overhead Recovery
  30% → Capital Contributors (proportional to capital account balance)
  40% → Labor Contributors (proportional to weighted hours)
```

## Trade Multipliers

| Trade | Multiplier |
|-------|-----------|
| General Labor / Painting / Admin | 1.00x |
| Project Management | 1.15x |
| Carpentry / Framing / Roofing | 1.20x |
| Plumbing / Electrical / HVAC | 1.30x |

## Example Members (Approved Scenario)

| Member | Capital | Hours | Trade | Multiplier |
|--------|---------|-------|-------|-----------|
| Maven | $50,000 | 200 | PM | 1.15x |
| Birch | $15,000 | 500 | Carpentry | 1.20x |
| Slate | $10,000 | 400 | Roofing | 1.20x |
| Copper | $25,000 | 350 | Plumbing | 1.30x |
| Member E | $15,000 | 300 | General | 1.00x |
| Member F | $5,000 | 250 | General | 1.00x |
