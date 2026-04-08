#!/usr/bin/env python3
"""
Portland Housing Co-op — Labor Hour Tracker
Author: Ledger (CFO)
Date: 2026-04-08

Records, weights, and reports member labor hours per project. Output feeds
directly into the profit-splitter tool for distribution calculations.

Data persistence: JSON files in a configurable data directory.

Usage:
    python labor_tracker.py                        # Run with sample data
    python labor_tracker.py --json                 # Output as JSON
    python labor_tracker.py --data-dir ./my_data   # Custom data directory
"""

import argparse
import json
import os
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional, Tuple


# ============================================================================
# TRADE MULTIPLIERS — From profit-split-model.md
# ============================================================================

TRADE_MULTIPLIERS: Dict[str, float] = {
    "GEN": 1.0,     # General Labor
    "PNT": 1.0,     # Painting / Finish Work
    "FRM": 1.2,     # Framing
    "CRP": 1.2,     # Carpentry
    "ROF": 1.2,     # Roofing
    "PLB": 1.3,     # Plumbing
    "ELC": 1.3,     # Electrical
    "HVC": 1.3,     # HVAC
    "PM":  1.15,    # Project Management
    "OPS": 1.0,     # Operations / Admin
}

TRADE_NAMES: Dict[str, str] = {
    "GEN": "General Labor",
    "PNT": "Painting / Finish",
    "FRM": "Framing",
    "CRP": "Carpentry",
    "ROF": "Roofing",
    "PLB": "Plumbing",
    "ELC": "Electrical",
    "HVC": "HVAC",
    "PM":  "Project Management",
    "OPS": "Operations / Admin",
}


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class LaborEntry:
    """A single labor log entry -- one member, one trade, one day."""
    member: str
    date: str
    hours: float
    trade: str        # Trade code (GEN, PLB, CRP, etc.)
    project: str
    description: str
    verified: bool = False
    verified_by: Optional[str] = None

    @property
    def multiplier(self) -> float:
        return TRADE_MULTIPLIERS.get(self.trade, 1.0)

    @property
    def weighted_hours(self) -> float:
        return self.hours * self.multiplier

    def to_dict(self) -> dict:
        return {
            "member": self.member,
            "date": self.date,
            "hours": self.hours,
            "trade": self.trade,
            "project": self.project,
            "description": self.description,
            "verified": self.verified,
            "verified_by": self.verified_by,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "LaborEntry":
        return cls(**d)


@dataclass
class LaborLedger:
    """All labor entries across all projects."""
    entries: List[LaborEntry] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"entries": [e.to_dict() for e in self.entries]}

    @classmethod
    def from_dict(cls, d: dict) -> "LaborLedger":
        entries = [LaborEntry.from_dict(e) for e in d.get("entries", [])]
        return cls(entries=entries)


# ============================================================================
# CORE TRACKER
# ============================================================================

class LaborTracker:
    """
    Tracks member labor hours per project with trade-based weighting.

    Validates:
    - Hours are rounded to 0.25 (15-minute increments)
    - Minimum loggable block is 1.0 hour
    - One row per trade per day per member
    - Trade code is valid
    """

    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        self.ledger_file = os.path.join(data_dir, "labor_ledger.json")
        self.ledger = self._load_ledger()

    def _load_ledger(self) -> LaborLedger:
        if os.path.exists(self.ledger_file):
            with open(self.ledger_file, "r") as f:
                return LaborLedger.from_dict(json.load(f))
        return LaborLedger()

    def _save_ledger(self) -> None:
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self.ledger_file, "w") as f:
            json.dump(self.ledger.to_dict(), f, indent=2)

    # ------------------------------------------------------------------
    # Logging hours
    # ------------------------------------------------------------------

    def log_hours(
        self,
        member: str,
        log_date: str,
        hours: float,
        trade: str,
        project: str,
        description: str,
    ) -> Tuple[bool, str]:
        """
        Log labor hours for a member.

        Args:
            member: Member name.
            log_date: Date (YYYY-MM-DD).
            hours: Hours worked (must be >= 1.0, rounded to 0.25).
            trade: Trade code (GEN, PLB, CRP, etc.).
            project: Project identifier.
            description: What was done (required, must be substantive).

        Returns:
            Tuple of (success: bool, message: str).
        """
        # Validate trade code
        if trade not in TRADE_MULTIPLIERS:
            valid_codes = ", ".join(sorted(TRADE_MULTIPLIERS.keys()))
            return False, f"Invalid trade code '{trade}'. Valid codes: {valid_codes}"

        # Validate minimum hours
        if hours < 1.0:
            return False, f"Minimum loggable block is 1.0 hour. Got {hours}."

        # Round to nearest 0.25
        rounded = round(hours * 4) / 4
        if abs(rounded - hours) > 0.001:
            hours = rounded

        # Validate description
        if not description or len(description.strip()) < 10:
            return False, "Description is required and must be at least 10 characters."

        # Check for duplicate (same member, date, trade, project)
        for entry in self.ledger.entries:
            if (
                entry.member == member
                and entry.date == log_date
                and entry.trade == trade
                and entry.project == project
            ):
                return (
                    False,
                    f"Duplicate: {member} already has {trade} hours logged for "
                    f"{log_date} on {project}. Edit the existing entry instead.",
                )

        entry = LaborEntry(
            member=member,
            date=log_date,
            hours=hours,
            trade=trade,
            project=project,
            description=description,
        )
        self.ledger.entries.append(entry)
        self._save_ledger()

        mult = TRADE_MULTIPLIERS[trade]
        weighted = hours * mult
        return (
            True,
            f"Logged {hours:.2f}h {TRADE_NAMES.get(trade, trade)} for {member} "
            f"on {log_date} ({weighted:.2f} weighted hrs @ {mult}x).",
        )

    def verify_week(
        self,
        project: str,
        week_start: str,
        week_end: str,
        verified_by: str,
    ) -> int:
        """
        Mark all entries in a date range as verified (PM weekly sign-off).

        Returns the number of entries verified.
        """
        count = 0
        for entry in self.ledger.entries:
            if (
                entry.project == project
                and week_start <= entry.date <= week_end
                and not entry.verified
            ):
                entry.verified = True
                entry.verified_by = verified_by
                count += 1
        self._save_ledger()
        return count

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def project_entries(self, project: str) -> List[LaborEntry]:
        """All entries for a project."""
        return [e for e in self.ledger.entries if e.project == project]

    def member_entries(self, member: str, project: Optional[str] = None) -> List[LaborEntry]:
        """All entries for a member, optionally filtered by project."""
        entries = [e for e in self.ledger.entries if e.member == member]
        if project:
            entries = [e for e in entries if e.project == project]
        return entries

    def projects(self) -> List[str]:
        """List of all projects with logged hours."""
        return sorted(set(e.project for e in self.ledger.entries))

    def members_on_project(self, project: str) -> List[str]:
        """List of all members who have logged hours on a project."""
        return sorted(set(e.member for e in self.ledger.entries if e.project == project))

    # ------------------------------------------------------------------
    # Reports
    # ------------------------------------------------------------------

    def member_summary(self, project: str) -> List[Dict]:
        """
        Per-member summary for a project.

        Returns list of dicts with:
        - member, total_hours, weighted_hours, pct_of_pool, hours_by_trade
        """
        entries = self.project_entries(project)
        members: Dict[str, Dict] = {}

        for e in entries:
            if e.member not in members:
                members[e.member] = {
                    "member": e.member,
                    "total_hours": 0.0,
                    "weighted_hours": 0.0,
                    "trades": {},
                }
            m = members[e.member]
            m["total_hours"] += e.hours
            m["weighted_hours"] += e.weighted_hours

            if e.trade not in m["trades"]:
                m["trades"][e.trade] = {"raw": 0.0, "weighted": 0.0}
            m["trades"][e.trade]["raw"] += e.hours
            m["trades"][e.trade]["weighted"] += e.weighted_hours

        # Calculate percentages
        total_weighted = sum(m["weighted_hours"] for m in members.values())
        result = []
        for m in sorted(members.values(), key=lambda x: x["weighted_hours"], reverse=True):
            pct = m["weighted_hours"] / total_weighted * 100 if total_weighted > 0 else 0
            result.append({
                "member": m["member"],
                "total_hours": round(m["total_hours"], 2),
                "weighted_hours": round(m["weighted_hours"], 2),
                "pct_of_pool": round(pct, 1),
                "hours_by_trade": {
                    k: {
                        "raw": round(v["raw"], 2),
                        "weighted": round(v["weighted"], 2),
                        "multiplier": TRADE_MULTIPLIERS[k],
                    }
                    for k, v in m["trades"].items()
                },
            })

        return result

    def profit_splitter_input(self, project: str) -> Dict:
        """
        Generate input data formatted for tools/profit-splitter/profit_splitter.py.

        Returns a dict that can be passed directly to the profit splitter's
        Member dataclass: {member_name: [(trade, hours), ...]}
        """
        entries = self.project_entries(project)
        members: Dict[str, List[Tuple[str, float]]] = {}

        # Map trade codes to profit_splitter.py trade names
        code_to_splitter: Dict[str, str] = {
            "GEN": "general_labor",
            "PNT": "painting",
            "FRM": "framing",
            "CRP": "carpentry",
            "ROF": "roofing",
            "PLB": "plumbing",
            "ELC": "electrical",
            "HVC": "hvac",
            "PM":  "project_management",
            "OPS": "operations",
        }

        for e in entries:
            if e.member not in members:
                members[e.member] = {}
            trade_key = code_to_splitter.get(e.trade, "general_labor")
            if trade_key not in members[e.member]:
                members[e.member][trade_key] = 0.0
            members[e.member][trade_key] += e.hours

        # Format as list of (trade, total_hours) tuples per member
        result = {}
        for member, trades in members.items():
            result[member] = [(trade, hours) for trade, hours in trades.items()]

        return result

    def print_report(self, project: str) -> None:
        """Print a human-readable labor report for a project."""
        summary = self.member_summary(project)
        w = 88

        total_raw = sum(m["total_hours"] for m in summary)
        total_weighted = sum(m["weighted_hours"] for m in summary)

        print("=" * w)
        print(f"  LABOR HOURS REPORT")
        print(f"  Project: {project}")
        print(f"  Report Date: {date.today().isoformat()}")
        print("=" * w)

        print(f"\n  Totals:")
        print(f"    Total Raw Hours:        {total_raw:,.1f}")
        print(f"    Total Weighted Hours:   {total_weighted:,.1f}")
        print(f"    Members Tracked:        {len(summary)}")

        # Entries logged / verified
        entries = self.project_entries(project)
        verified = sum(1 for e in entries if e.verified)
        print(f"    Total Entries:          {len(entries)}")
        print(f"    Verified:               {verified} ({verified/len(entries)*100:.0f}%)" if entries else "")

        print(f"\n  Per-Member Summary:")
        print(
            f"  {'Member':<14s} {'Raw Hrs':>9s} {'Weighted':>10s} "
            f"{'% Pool':>8s} {'Primary Trade':<18s}"
        )
        print(
            f"  {'---':<14s} {'---':>9s} {'---':>10s} "
            f"{'---':>8s} {'---':<18s}"
        )

        for m in summary:
            # Find primary trade (most weighted hours)
            primary = max(m["hours_by_trade"].items(), key=lambda x: x[1]["weighted"])
            trade_name = TRADE_NAMES.get(primary[0], primary[0])
            print(
                f"  {m['member']:<14s} {m['total_hours']:>9.1f} "
                f"{m['weighted_hours']:>10.1f} {m['pct_of_pool']:>7.1f}% "
                f"{trade_name:<18s}"
            )

        # Detailed breakdown by trade per member
        print(f"\n  Hours by Trade:")
        print(
            f"  {'Member':<14s} {'Trade':<18s} {'Raw':>8s} "
            f"{'Mult':>6s} {'Weighted':>10s}"
        )
        print(
            f"  {'---':<14s} {'---':<18s} {'---':>8s} "
            f"{'---':>6s} {'---':>10s}"
        )

        for m in summary:
            for trade_code, data in sorted(m["hours_by_trade"].items()):
                trade_name = TRADE_NAMES.get(trade_code, trade_code)
                print(
                    f"  {m['member']:<14s} {trade_name:<18s} "
                    f"{data['raw']:>8.1f} {data['multiplier']:>5.2f}x "
                    f"{data['weighted']:>10.1f}"
                )

        # Profit splitter integration
        print(f"\n  Profit Splitter Integration:")
        print(f"  To use these hours in the profit split calculation:")
        print(f"    splitter_data = tracker.profit_splitter_input(\"{project}\")")
        print(f"    # Returns: {{member: [(trade, hours), ...]}}")

        print(f"\n{'=' * w}")


# ============================================================================
# SAMPLE DATA — 6-member rehab project
# ============================================================================

def build_sample_tracker() -> LaborTracker:
    """
    Build a tracker with sample data for a 6-member rehab project.

    Simulates 6 weeks of work on 123 SE Foster Rd with realistic
    hours and trade distributions matching our profit-split-model.md examples.
    """
    tracker = LaborTracker(data_dir="/tmp/labor_tracker_demo")

    project = "123 SE Foster Rd"

    # Week 1 (2026-07-06 to 2026-07-10)
    week1 = [
        ("Maven",    "2026-07-07", 3.0,  "PM",  "Coordinated material delivery, met with inspector"),
        ("Maven",    "2026-07-08", 2.5,  "PM",  "Reviewed permit status with BDS, scheduled sub"),
        ("Maven",    "2026-07-10", 2.0,  "PM",  "Met with hard money lender, reviewed draw schedule"),
        ("Birch",    "2026-07-07", 8.0,  "CRP", "Framed bedroom closet and hallway linen closet"),
        ("Birch",    "2026-07-08", 7.5,  "CRP", "Installed subfloor patches in kitchen and living room"),
        ("Birch",    "2026-07-09", 8.0,  "CRP", "Built and installed kitchen cabinet framing"),
        ("Birch",    "2026-07-10", 7.0,  "CRP", "Installed new interior doors in bedrooms and bath"),
        ("Copper",   "2026-07-07", 7.5,  "PLB", "Rough-in plumbing for master bath supply and drain"),
        ("Copper",   "2026-07-08", 8.0,  "PLB", "Ran new copper supply lines to kitchen, pressure tested"),
        ("Copper",   "2026-07-09", 6.0,  "PLB", "Installed water heater and connected gas line"),
        ("Copper",   "2026-07-09", 2.0,  "GEN", "Helped with drywall hanging in hallway"),
        ("Copper",   "2026-07-10", 7.0,  "PLB", "Final connections on bathroom fixtures, toilet, vanity"),
        ("Slate",    "2026-07-07", 8.0,  "ROF", "Tore off existing comp shingles on south face"),
        ("Slate",    "2026-07-08", 7.5,  "ROF", "Installed ice and water shield and felt on south face"),
        ("Slate",    "2026-07-09", 8.0,  "ROF", "Installed comp shingles on south face, 60% complete"),
        ("Slate",    "2026-07-10", 7.5,  "ROF", "Completed south face shingles, started flashing"),
        ("Member E", "2026-07-07", 6.0,  "GEN", "Demo kitchen cabinets and hauled debris to dumpster"),
        ("Member E", "2026-07-08", 7.0,  "GEN", "Prepped walls in bedrooms, patched holes, sanded, primed"),
        ("Member E", "2026-07-09", 8.0,  "GEN", "Hung drywall in hallway and front bedroom"),
        ("Member E", "2026-07-10", 7.0,  "GEN", "Taped and mudded drywall joints first coat"),
        ("Member F", "2026-07-07", 7.0,  "GEN", "Assisted with roof tear-off ground crew"),
        ("Member F", "2026-07-08", 6.0,  "GEN", "Cleaned site, organized tool crib, received lumber"),
        ("Member F", "2026-07-09", 7.0,  "PNT", "Primed bedroom walls two coats"),
        ("Member F", "2026-07-10", 7.5,  "PNT", "Painted master bedroom two coats finish color"),
    ]

    # Week 2 (2026-07-14 to 2026-07-18)
    week2 = [
        ("Maven",    "2026-07-14", 2.5,  "PM",  "Inspected framing, ordered trim materials"),
        ("Maven",    "2026-07-16", 3.0,  "PM",  "Met with electrician sub re panel upgrade timeline"),
        ("Maven",    "2026-07-18", 1.5,  "PM",  "Reviewed budget vs actuals, updated cash flow"),
        ("Birch",    "2026-07-14", 8.0,  "CRP", "Installed window trim and casing front of house"),
        ("Birch",    "2026-07-15", 7.5,  "CRP", "Built custom pantry shelving in kitchen"),
        ("Birch",    "2026-07-16", 8.0,  "CRP", "Installed deck rail posts and balusters"),
        ("Birch",    "2026-07-17", 7.0,  "CRP", "Replaced rotted fascia boards on north side"),
        ("Birch",    "2026-07-18", 6.5,  "CRP", "Installed crown molding in living room"),
        ("Copper",   "2026-07-14", 8.0,  "PLB", "Installed kitchen sink and garbage disposal"),
        ("Copper",   "2026-07-15", 7.5,  "PLB", "Ran dishwasher supply and drain lines"),
        ("Copper",   "2026-07-16", 6.5,  "PLB", "Installed laundry hookups in basement"),
        ("Copper",   "2026-07-17", 8.0,  "PLB", "Replaced main sewer cleanout and tested drainage"),
        ("Copper",   "2026-07-18", 7.0,  "PLB", "Installed hose bibs and pressure tested all lines"),
        ("Slate",    "2026-07-14", 6.0,  "ROF", "Installed ridge vent and capped ridge"),
        ("Slate",    "2026-07-15", 7.5,  "ROF", "North face tear-off and prep"),
        ("Slate",    "2026-07-16", 8.0,  "ROF", "North face shingle install"),
        ("Slate",    "2026-07-17", 7.0,  "ROF", "Completed north face, installed flashing at chimney"),
        ("Slate",    "2026-07-18", 4.0,  "ROF", "Final inspection prep, cleaned gutters"),
        ("Member E", "2026-07-14", 7.0,  "GEN", "Sanded drywall second coat of mud"),
        ("Member E", "2026-07-15", 8.0,  "GEN", "Installed baseboards in living room and hallway"),
        ("Member E", "2026-07-16", 7.5,  "GEN", "Laid tile backer board in bathroom"),
        ("Member E", "2026-07-17", 8.0,  "GEN", "Installed bathroom floor tile"),
        ("Member E", "2026-07-18", 6.5,  "GEN", "Grouted bathroom tile, cleaned and sealed"),
        ("Member F", "2026-07-14", 7.5,  "PNT", "Painted second bedroom and hallway"),
        ("Member F", "2026-07-15", 8.0,  "PNT", "Painted kitchen walls and ceiling"),
        ("Member F", "2026-07-16", 7.0,  "PNT", "Painted living room two coats"),
        ("Member F", "2026-07-17", 6.5,  "PNT", "Painted exterior trim south side"),
        ("Member F", "2026-07-18", 7.0,  "PNT", "Painted front porch deck and railing"),
    ]

    # Week 3 (2026-07-21 to 2026-07-25)
    week3 = [
        ("Maven",    "2026-07-21", 2.0,  "PM",  "Met with stager, scheduled photographer for listing"),
        ("Maven",    "2026-07-23", 3.0,  "PM",  "Final walkthrough with inspector, punch list review"),
        ("Birch",    "2026-07-21", 7.5,  "CRP", "Installed kitchen countertop and backsplash trim"),
        ("Birch",    "2026-07-22", 8.0,  "CRP", "Built closet organizer system for master bedroom"),
        ("Birch",    "2026-07-23", 6.5,  "CRP", "Installed bathroom vanity and mirror frame"),
        ("Birch",    "2026-07-24", 7.0,  "CRP", "Final trim work and punch list items"),
        ("Birch",    "2026-07-25", 5.0,  "CRP", "Touch up carpentry, installed hardware throughout"),
        ("Copper",   "2026-07-21", 6.0,  "PLB", "Connected dishwasher, tested all fixtures under pressure"),
        ("Copper",   "2026-07-22", 4.0,  "PLB", "Fixed slow drain in hall bath, replaced P-trap"),
        ("Copper",   "2026-07-23", 3.0,  "PLB", "Final plumbing inspection prep and walkthrough"),
        ("Slate",    "2026-07-21", 3.0,  "GEN", "Helped with kitchen countertop install"),
        ("Slate",    "2026-07-22", 6.0,  "GEN", "Installed light fixtures and outlet covers"),
        ("Slate",    "2026-07-23", 4.0,  "GEN", "Landscaping cleanup, weeded beds, mowed lawn"),
        ("Member E", "2026-07-21", 7.0,  "GEN", "Installed kitchen backsplash tile"),
        ("Member E", "2026-07-22", 6.5,  "GEN", "Installed closet rods and shelving"),
        ("Member E", "2026-07-23", 5.0,  "GEN", "Final cleanup interior, vacuumed all rooms"),
        ("Member E", "2026-07-24", 4.0,  "GEN", "Hauled last dumpster, cleaned exterior"),
        ("Member F", "2026-07-21", 7.0,  "PNT", "Touch up paint throughout house"),
        ("Member F", "2026-07-22", 6.5,  "PNT", "Painted exterior north side and back fence"),
        ("Member F", "2026-07-23", 5.0,  "PNT", "Final touch ups, stain on deck, sealed concrete"),
    ]

    all_entries = week1 + week2 + week3

    print("  Loading sample labor entries...")
    for member, log_date, hours, trade, desc in all_entries:
        ok, msg = tracker.log_hours(member, log_date, hours, trade, project, desc)
        if not ok:
            print(f"    WARNING: {msg}")

    # Verify weeks 1 and 2 (PM sign-off)
    v1 = tracker.verify_week(project, "2026-07-07", "2026-07-11", "Harlan (PM)")
    v2 = tracker.verify_week(project, "2026-07-14", "2026-07-18", "Harlan (PM)")
    print(f"  Verified: {v1} entries (week 1), {v2} entries (week 2)")

    print(f"  Total entries loaded: {len(all_entries)}")
    return tracker


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Portland Housing Co-op — Labor Hour Tracker"
    )
    parser.add_argument(
        "--data-dir", type=str, default="./data",
        help="Directory for JSON data files (default: ./data)",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output member summary as JSON",
    )
    parser.add_argument(
        "--project", type=str, default="123 SE Foster Rd",
        help="Project to report on",
    )
    args = parser.parse_args()

    print("\n  Building sample data...\n")
    tracker = build_sample_tracker()

    project = args.project

    if args.json:
        summary = tracker.member_summary(project)
        splitter_input = tracker.profit_splitter_input(project)
        output = {
            "project": project,
            "report_date": date.today().isoformat(),
            "member_summary": summary,
            "profit_splitter_input": splitter_input,
        }
        print(json.dumps(output, indent=2))
    else:
        print()
        tracker.print_report(project)

    print()


if __name__ == "__main__":
    main()
