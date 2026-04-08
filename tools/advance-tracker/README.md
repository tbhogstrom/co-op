# Advance Tracker

Portland Housing Co-op tool for tracking labor advances per member per project.

## What It Does

Tracks, validates, and reports on labor advances drawn by co-op members during rehab projects. Enforces all M1-approved advance policy rules automatically.

## Business Rules Enforced

1. **30% Completion Gate** -- No advances are issued until the project reaches 30% completion.
2. **50% Cap** -- Maximum advance per member is 50% of their estimated labor share, calculated using the conservative gross profit scenario.
3. **Board Approval** -- Every draw requires a board approval reference (meeting minutes, resolution number).
4. **Reconciliation** -- At project close, advances are reconciled against actual labor shares. Over-draws are flagged for clawback from the member's capital account.

## Usage

### Run with sample data

```
python advance_tracker.py
```

This builds a demo scenario: 6 members on a $30,700 GP project at 55% completion, with four draws recorded and one denied request (completion gate).

### JSON output

```
python advance_tracker.py --json
```

### Custom data directory

```
python advance_tracker.py --data-dir /path/to/your/data
```

## Inputs

### Project configuration

- `project_name` -- Property address or identifier.
- `conservative_gross_profit` -- The conservative-scenario GP estimate from your deal analysis. This is the number the advance cap is based on. Always use the conservative number, never moderate or aggressive.
- `labor_estimates` -- Per-member list of estimated hours and trade classification (determines the multiplier).
- `completion_pct` -- Current project completion (0.0 to 1.0). Must be >= 0.30 for advances to be approved.

### Advance draws

- `member` -- Member name.
- `amount` -- Dollar amount requested.
- `project_name` -- Which project.
- `board_approval_ref` -- Free-text reference to the board action approving this draw (e.g., "Board Minutes 2026-08-15, Item 4").
- `draw_date` -- Date of the draw (defaults to today).

## Outputs

### Summary report

Per-member breakdown showing:

- Estimated labor share (based on conservative GP and projected hours)
- Maximum advance allowed (50% of estimated share)
- Amount drawn to date
- Remaining allowance
- Overage risk flag (NONE / LOW / MEDIUM / HIGH)

### Draw history

Chronological list of all draws with dates, amounts, board references, and status.

### Reconciliation report

Generated at project close. Compares total advances drawn against actual labor shares. Flags over-draws that require clawback.

## Data Persistence

All data is stored in `advance_ledger.json` in the configured data directory. No database needed for Year 1.

### File structure

```
data/
  advance_ledger.json    # All projects, draws, and configurations
```

## How It Connects

- **Inputs from:** Deal analysis (conservative GP estimate), labor tracker (estimated hours), project management (completion percentage).
- **Outputs to:** Profit splitter (advances deducted from distributions), equity tracker (clawbacks affect capital accounts).

## Advance Calculation Math

```
Labor Pool         = Conservative GP x 40%
Member Est. Share  = Labor Pool x (Member Weighted Hours / Total Weighted Hours)
Max Advance        = Member Est. Share x 50%

Example (Birch on a $30,700 GP project):
  Labor Pool       = $30,700 x 0.40 = $12,280
  Birch est. hours = 400 hrs x 1.2 (carpentry) = 480 weighted
  Total weighted   = 2,165 hrs
  Birch share      = $12,280 x (480 / 2,165) = $2,722
  Max advance      = $2,722 x 0.50 = $1,361
```
