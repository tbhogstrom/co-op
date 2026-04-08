#!/usr/bin/env python3
"""
Portland Housing Co-op — Labor Advance Tracker
Author: Ledger (CFO)
Date: 2026-04-08

Tracks labor advances per member per project. Enforces M1-approved advance
policy: 50% of conservative-scenario labor share, available only after 30%
project completion, board-approved.

Data persistence: JSON files in a configurable data directory.

Usage:
    python advance_tracker.py                          # Run with sample data
    python advance_tracker.py --data-dir ./my_data     # Use custom data directory
    python advance_tracker.py --json                   # Output as JSON
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass, field, asdict
from datetime import date
from typing import Dict, List, Optional, Tuple


# ============================================================================
# CONSTANTS — M1 Approved Policy
# ============================================================================

MAX_ADVANCE_PCT: float = 0.50       # 50% of estimated labor share
LABOR_POOL_PCT: float = 0.40        # 40% of gross profit goes to labor
MIN_COMPLETION_PCT: float = 0.30    # 30% completion gate

# Trade rate multipliers (from profit-split-model.md)
TRADE_MULTIPLIERS: Dict[str, float] = {
    "general_labor": 1.0,
    "painting": 1.0,
    "finish_work": 1.0,
    "operations": 1.0,
    "admin": 1.0,
    "framing": 1.2,
    "carpentry": 1.2,
    "roofing": 1.2,
    "plumbing": 1.3,
    "electrical": 1.3,
    "hvac": 1.3,
    "project_management": 1.15,
}


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class AdvanceDraw:
    """A single advance draw by a member on a project."""
    member: str
    amount: float
    date: str
    project: str
    board_approval_ref: str   # e.g., "Board Minutes 2026-08-15, Item 4"
    status: str = "outstanding"  # outstanding | repaid | deducted | clawback

    def to_dict(self) -> dict:
        return {
            "member": self.member,
            "amount": self.amount,
            "date": self.date,
            "project": self.project,
            "board_approval_ref": self.board_approval_ref,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "AdvanceDraw":
        return cls(**d)


@dataclass
class MemberLaborEstimate:
    """Estimated labor contribution for a member on a project."""
    member: str
    estimated_hours: float
    trade: str
    multiplier: float = 1.0

    @property
    def weighted_hours(self) -> float:
        return self.estimated_hours * self.multiplier

    def to_dict(self) -> dict:
        return {
            "member": self.member,
            "estimated_hours": self.estimated_hours,
            "trade": self.trade,
            "multiplier": self.multiplier,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "MemberLaborEstimate":
        return cls(**d)


@dataclass
class ProjectAdvanceConfig:
    """Advance configuration for a specific project."""
    project_name: str
    conservative_gross_profit: float
    completion_pct: float = 0.0  # Current completion percentage (0.0 to 1.0)
    labor_estimates: List[MemberLaborEstimate] = field(default_factory=list)
    actual_labor_shares: Optional[Dict[str, float]] = None  # Set at project close

    @property
    def labor_pool(self) -> float:
        """Total labor pool based on conservative gross profit."""
        return max(0.0, self.conservative_gross_profit * LABOR_POOL_PCT)

    @property
    def total_estimated_weighted_hours(self) -> float:
        return sum(e.weighted_hours for e in self.labor_estimates)

    def estimated_labor_share(self, member: str) -> float:
        """Calculate a member's estimated labor share."""
        total_wh = self.total_estimated_weighted_hours
        if total_wh == 0:
            return 0.0
        member_wh = sum(
            e.weighted_hours for e in self.labor_estimates if e.member == member
        )
        return self.labor_pool * (member_wh / total_wh)

    def max_advance(self, member: str) -> float:
        """Maximum advance a member can draw (50% of estimated labor share)."""
        return self.estimated_labor_share(member) * MAX_ADVANCE_PCT

    def to_dict(self) -> dict:
        return {
            "project_name": self.project_name,
            "conservative_gross_profit": self.conservative_gross_profit,
            "completion_pct": self.completion_pct,
            "labor_estimates": [e.to_dict() for e in self.labor_estimates],
            "actual_labor_shares": self.actual_labor_shares,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ProjectAdvanceConfig":
        estimates = [MemberLaborEstimate.from_dict(e) for e in d.get("labor_estimates", [])]
        return cls(
            project_name=d["project_name"],
            conservative_gross_profit=d["conservative_gross_profit"],
            completion_pct=d.get("completion_pct", 0.0),
            labor_estimates=estimates,
            actual_labor_shares=d.get("actual_labor_shares"),
        )


@dataclass
class AdvanceLedger:
    """Master ledger tracking all advance draws across all projects."""
    draws: List[AdvanceDraw] = field(default_factory=list)
    projects: Dict[str, ProjectAdvanceConfig] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "draws": [d.to_dict() for d in self.draws],
            "projects": {k: v.to_dict() for k, v in self.projects.items()},
        }

    @classmethod
    def from_dict(cls, d: dict) -> "AdvanceLedger":
        draws = [AdvanceDraw.from_dict(x) for x in d.get("draws", [])]
        projects = {
            k: ProjectAdvanceConfig.from_dict(v)
            for k, v in d.get("projects", {}).items()
        }
        return cls(draws=draws, projects=projects)


# ============================================================================
# CORE LOGIC
# ============================================================================

class AdvanceTracker:
    """
    Tracks and enforces labor advance policy.

    Business rules enforced:
    1. No advances until project is >= 30% complete.
    2. Maximum advance = 50% of conservative-scenario labor share.
    3. Each draw requires a board approval reference.
    4. At project close, advances are reconciled against actual labor share.
    5. Over-draws are flagged for clawback.
    """

    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        self.ledger_file = os.path.join(data_dir, "advance_ledger.json")
        self.ledger = self._load_ledger()

    def _load_ledger(self) -> AdvanceLedger:
        """Load ledger from JSON file, or create empty ledger."""
        if os.path.exists(self.ledger_file):
            with open(self.ledger_file, "r") as f:
                return AdvanceLedger.from_dict(json.load(f))
        return AdvanceLedger()

    def _save_ledger(self) -> None:
        """Persist ledger to JSON file."""
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self.ledger_file, "w") as f:
            json.dump(self.ledger.to_dict(), f, indent=2)

    # ------------------------------------------------------------------
    # Project configuration
    # ------------------------------------------------------------------

    def configure_project(
        self,
        project_name: str,
        conservative_gross_profit: float,
        labor_estimates: List[MemberLaborEstimate],
        completion_pct: float = 0.0,
    ) -> ProjectAdvanceConfig:
        """
        Set up or update advance parameters for a project.

        Args:
            project_name: Identifier for the project (e.g., "123 SE Foster Rd").
            conservative_gross_profit: Conservative GP estimate used for advance caps.
            labor_estimates: List of per-member labor estimates with trade/hours.
            completion_pct: Current project completion (0.0 to 1.0).

        Returns:
            The configured ProjectAdvanceConfig.
        """
        config = ProjectAdvanceConfig(
            project_name=project_name,
            conservative_gross_profit=conservative_gross_profit,
            labor_estimates=labor_estimates,
            completion_pct=completion_pct,
        )
        self.ledger.projects[project_name] = config
        self._save_ledger()
        return config

    def update_completion(self, project_name: str, completion_pct: float) -> None:
        """Update the project's completion percentage."""
        if project_name not in self.ledger.projects:
            raise ValueError(f"Project '{project_name}' not configured.")
        self.ledger.projects[project_name].completion_pct = completion_pct
        self._save_ledger()

    # ------------------------------------------------------------------
    # Drawing advances
    # ------------------------------------------------------------------

    def request_advance(
        self,
        member: str,
        amount: float,
        project_name: str,
        board_approval_ref: str,
        draw_date: Optional[str] = None,
    ) -> Tuple[bool, str, Optional[AdvanceDraw]]:
        """
        Request a labor advance. Validates all business rules.

        Args:
            member: Member name.
            amount: Requested advance amount in dollars.
            project_name: Project identifier.
            board_approval_ref: Reference to board approval (minutes, resolution).
            draw_date: Date of the draw (defaults to today).

        Returns:
            Tuple of (approved: bool, message: str, draw: AdvanceDraw or None).
        """
        if draw_date is None:
            draw_date = date.today().isoformat()

        # Validate project exists
        if project_name not in self.ledger.projects:
            return False, f"Project '{project_name}' not configured in advance tracker.", None

        config = self.ledger.projects[project_name]

        # Rule 1: 30% completion gate
        if config.completion_pct < MIN_COMPLETION_PCT:
            return (
                False,
                f"DENIED: Project is {config.completion_pct:.0%} complete. "
                f"Advances require >= {MIN_COMPLETION_PCT:.0%} completion.",
                None,
            )

        # Rule 2: Check member has labor estimate
        max_adv = config.max_advance(member)
        if max_adv == 0:
            return False, f"DENIED: No labor estimate found for '{member}' on this project.", None

        # Rule 3: Check remaining allowance
        already_drawn = self.total_drawn(member, project_name)
        remaining = max_adv - already_drawn

        if amount > remaining + 0.01:  # small tolerance for rounding
            return (
                False,
                f"DENIED: Requested ${amount:,.2f} exceeds remaining allowance of "
                f"${remaining:,.2f}. (Max: ${max_adv:,.2f}, already drawn: ${already_drawn:,.2f}).",
                None,
            )

        if amount <= 0:
            return False, "DENIED: Advance amount must be positive.", None

        # All checks pass — record the draw
        draw = AdvanceDraw(
            member=member,
            amount=amount,
            date=draw_date,
            project=project_name,
            board_approval_ref=board_approval_ref,
            status="outstanding",
        )
        self.ledger.draws.append(draw)
        self._save_ledger()

        new_total = already_drawn + amount
        return (
            True,
            f"APPROVED: ${amount:,.2f} advance to {member}. "
            f"Total drawn: ${new_total:,.2f} of ${max_adv:,.2f} max.",
            draw,
        )

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def total_drawn(self, member: str, project_name: str) -> float:
        """Total advances drawn by a member on a project (outstanding only)."""
        return sum(
            d.amount
            for d in self.ledger.draws
            if d.member == member
            and d.project == project_name
            and d.status == "outstanding"
        )

    def total_drawn_all_statuses(self, member: str, project_name: str) -> float:
        """Total advances ever drawn by a member on a project (any status)."""
        return sum(
            d.amount
            for d in self.ledger.draws
            if d.member == member and d.project == project_name
        )

    def remaining_allowance(self, member: str, project_name: str) -> float:
        """How much more a member can draw on a project."""
        if project_name not in self.ledger.projects:
            return 0.0
        config = self.ledger.projects[project_name]
        return max(0.0, config.max_advance(member) - self.total_drawn(member, project_name))

    def members_on_project(self, project_name: str) -> List[str]:
        """List all members with labor estimates on a project."""
        if project_name not in self.ledger.projects:
            return []
        return [e.member for e in self.ledger.projects[project_name].labor_estimates]

    # ------------------------------------------------------------------
    # Reconciliation at project close
    # ------------------------------------------------------------------

    def reconcile_project(
        self,
        project_name: str,
        actual_labor_shares: Dict[str, float],
    ) -> List[Dict]:
        """
        Reconcile advances against actual labor shares at project close.

        Args:
            project_name: Project identifier.
            actual_labor_shares: Dict of {member_name: actual_labor_share_dollars}.

        Returns:
            List of reconciliation records, one per member.
        """
        if project_name not in self.ledger.projects:
            raise ValueError(f"Project '{project_name}' not configured.")

        config = self.ledger.projects[project_name]
        config.actual_labor_shares = actual_labor_shares

        results = []
        members = set(
            d.member for d in self.ledger.draws if d.project == project_name
        ) | set(actual_labor_shares.keys())

        for member in sorted(members):
            drawn = self.total_drawn(member, project_name)
            actual_share = actual_labor_shares.get(member, 0.0)
            overage = max(0.0, drawn - actual_share)
            net_distribution = actual_share - drawn

            status = "settled"
            if overage > 0.01:
                status = "OVERAGE — clawback required"
            elif drawn > 0 and net_distribution >= 0:
                status = "settled — deducted from distribution"

            # Mark draws as deducted
            if drawn > 0:
                for d in self.ledger.draws:
                    if d.member == member and d.project == project_name and d.status == "outstanding":
                        d.status = "clawback" if overage > 0.01 else "deducted"

            results.append({
                "member": member,
                "total_advances_drawn": round(drawn, 2),
                "actual_labor_share": round(actual_share, 2),
                "net_distribution": round(net_distribution, 2),
                "overage": round(overage, 2),
                "status": status,
            })

        self._save_ledger()
        return results

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def summary_report(self, project_name: str) -> Dict:
        """
        Generate a summary report for a project.

        Returns dict with:
        - project config
        - per-member: estimated share, max advance, drawn, remaining, overage risk
        """
        if project_name not in self.ledger.projects:
            raise ValueError(f"Project '{project_name}' not configured.")

        config = self.ledger.projects[project_name]
        members_data = []

        for est in config.labor_estimates:
            member = est.member
            est_share = config.estimated_labor_share(member)
            max_adv = config.max_advance(member)
            drawn = self.total_drawn(member, project_name)
            remaining = max(0.0, max_adv - drawn)
            utilization = drawn / max_adv if max_adv > 0 else 0.0

            # Overage risk: flag if drawn > 80% of max
            if utilization > 0.80:
                risk = "HIGH"
            elif utilization > 0.50:
                risk = "MEDIUM"
            elif drawn > 0:
                risk = "LOW"
            else:
                risk = "NONE"

            members_data.append({
                "member": member,
                "trade": est.trade,
                "estimated_hours": est.estimated_hours,
                "multiplier": est.multiplier,
                "weighted_hours": round(est.weighted_hours, 1),
                "estimated_labor_share": round(est_share, 2),
                "max_advance": round(max_adv, 2),
                "total_drawn": round(drawn, 2),
                "remaining_allowance": round(remaining, 2),
                "utilization_pct": round(utilization * 100, 1),
                "overage_risk": risk,
            })

        total_drawn = sum(m["total_drawn"] for m in members_data)
        total_max = sum(m["max_advance"] for m in members_data)

        return {
            "project_name": project_name,
            "conservative_gross_profit": config.conservative_gross_profit,
            "labor_pool": round(config.labor_pool, 2),
            "completion_pct": round(config.completion_pct * 100, 1),
            "advances_eligible": config.completion_pct >= MIN_COMPLETION_PCT,
            "total_max_advances": round(total_max, 2),
            "total_drawn": round(total_drawn, 2),
            "total_remaining": round(total_max - total_drawn, 2),
            "members": members_data,
        }

    def print_report(self, project_name: str) -> None:
        """Print a human-readable advance tracking report."""
        report = self.summary_report(project_name)
        w = 90

        print("=" * w)
        print(f"  LABOR ADVANCE TRACKING REPORT")
        print(f"  Project: {report['project_name']}")
        print(f"  Report Date: {date.today().isoformat()}")
        print("=" * w)

        print(f"\n  Project Parameters:")
        print(f"    Conservative Gross Profit:  ${report['conservative_gross_profit']:,.2f}")
        print(f"    Labor Pool (40%):           ${report['labor_pool']:,.2f}")
        print(f"    Project Completion:         {report['completion_pct']:.0f}%")

        gate_status = "OPEN" if report["advances_eligible"] else "CLOSED (< 30%)"
        print(f"    Advance Gate:               {gate_status}")

        print(f"\n  Advance Summary:")
        print(f"    Total Max Advances:         ${report['total_max_advances']:,.2f}")
        print(f"    Total Drawn:                ${report['total_drawn']:,.2f}")
        print(f"    Total Remaining:            ${report['total_remaining']:,.2f}")

        print(f"\n  Per-Member Detail:")
        header = (
            f"  {'Member':<14s} {'Trade':<14s} {'Est.Share':>10s} "
            f"{'Max Adv':>10s} {'Drawn':>10s} {'Remaining':>10s} {'Risk':>6s}"
        )
        print(header)
        print(f"  {'---':<14s} {'---':<14s} {'---':>10s} {'---':>10s} {'---':>10s} {'---':>10s} {'---':>6s}")

        for m in report["members"]:
            print(
                f"  {m['member']:<14s} {m['trade']:<14s} "
                f"${m['estimated_labor_share']:>9,.2f} "
                f"${m['max_advance']:>9,.2f} "
                f"${m['total_drawn']:>9,.2f} "
                f"${m['remaining_allowance']:>9,.2f} "
                f"{m['overage_risk']:>6s}"
            )

        # Draw history
        project_draws = [
            d for d in self.ledger.draws if d.project == project_name
        ]
        if project_draws:
            print(f"\n  Draw History:")
            print(f"  {'Date':<12s} {'Member':<14s} {'Amount':>10s} {'Status':<14s} {'Board Ref'}")
            print(f"  {'---':<12s} {'---':<14s} {'---':>10s} {'---':<14s} {'---'}")
            for d in sorted(project_draws, key=lambda x: x.date):
                print(
                    f"  {d.date:<12s} {d.member:<14s} "
                    f"${d.amount:>9,.2f} {d.status:<14s} {d.board_approval_ref}"
                )

        print(f"\n{'=' * w}")


# ============================================================================
# SAMPLE DATA — 6-member project demonstration
# ============================================================================

def build_sample_tracker() -> AdvanceTracker:
    """
    Build a tracker with sample data showing a 6-member rehab project.

    Scenario: 123 SE Foster Rd
    - Conservative GP: $30,700
    - Labor pool (40%): $12,280
    - Project is at 55% completion (advances are eligible)
    - Three members have drawn advances; three have not.
    """
    tracker = AdvanceTracker(data_dir="/tmp/advance_tracker_demo")

    # Configure project with labor estimates
    estimates = [
        MemberLaborEstimate("Maven", 200, "project_management", 1.15),
        MemberLaborEstimate("Birch", 400, "carpentry", 1.2),
        MemberLaborEstimate("Copper", 350, "plumbing", 1.3),
        MemberLaborEstimate("Slate", 300, "roofing", 1.2),
        MemberLaborEstimate("Member E", 250, "electrical", 1.3),
        MemberLaborEstimate("Member F", 300, "painting", 1.0),
    ]

    tracker.configure_project(
        project_name="123 SE Foster Rd",
        conservative_gross_profit=30_700.0,
        labor_estimates=estimates,
        completion_pct=0.55,
    )

    # --- Draw advances ---
    # Birch draws two advances
    ok, msg, _ = tracker.request_advance(
        member="Birch",
        amount=600.0,
        project_name="123 SE Foster Rd",
        board_approval_ref="Board Minutes 2026-08-15, Item 3",
        draw_date="2026-08-15",
    )
    print(f"  Draw 1: {msg}")

    ok, msg, _ = tracker.request_advance(
        member="Birch",
        amount=600.0,
        project_name="123 SE Foster Rd",
        board_approval_ref="Board Minutes 2026-09-01, Item 2",
        draw_date="2026-09-01",
    )
    print(f"  Draw 2: {msg}")

    # Copper draws one advance
    ok, msg, _ = tracker.request_advance(
        member="Copper",
        amount=1_000.0,
        project_name="123 SE Foster Rd",
        board_approval_ref="Board Minutes 2026-09-01, Item 3",
        draw_date="2026-09-01",
    )
    print(f"  Draw 3: {msg}")

    # Slate draws one advance
    ok, msg, _ = tracker.request_advance(
        member="Slate",
        amount=500.0,
        project_name="123 SE Foster Rd",
        board_approval_ref="Board Minutes 2026-08-15, Item 4",
        draw_date="2026-08-15",
    )
    print(f"  Draw 4: {msg}")

    # Maven does not draw (no need)
    # Member E does not draw
    # Member F does not draw

    # --- Demonstrate a denied request (completion gate) ---
    # Set up a second project at only 20% completion
    tracker.configure_project(
        project_name="456 NE Cully Blvd",
        conservative_gross_profit=45_000.0,
        labor_estimates=[
            MemberLaborEstimate("Maven", 150, "project_management", 1.15),
            MemberLaborEstimate("Birch", 300, "carpentry", 1.2),
        ],
        completion_pct=0.20,
    )

    ok, msg, _ = tracker.request_advance(
        member="Birch",
        amount=500.0,
        project_name="456 NE Cully Blvd",
        board_approval_ref="N/A",
        draw_date="2026-10-01",
    )
    print(f"  Draw 5 (should be denied): {msg}")

    return tracker


def demonstrate_reconciliation(tracker: AdvanceTracker) -> None:
    """Demonstrate project-close reconciliation."""
    print("\n" + "=" * 90)
    print("  PROJECT CLOSE — RECONCILIATION")
    print("=" * 90)

    # Actual labor shares from profit_splitter.py after project completes
    actual_shares = {
        "Maven": 1_134.00,
        "Birch": 2_724.00,
        "Copper": 2_581.00,
        "Slate": 2_043.00,
        "Member E": 1_844.00,
        "Member F": 1_704.00,
    }

    results = tracker.reconcile_project("123 SE Foster Rd", actual_shares)

    print(f"\n  {'Member':<14s} {'Advances':>10s} {'Actual Share':>13s} {'Net Distrib':>12s} {'Overage':>10s} {'Status'}")
    print(f"  {'---':<14s} {'---':>10s} {'---':>13s} {'---':>12s} {'---':>10s} {'---'}")
    for r in results:
        print(
            f"  {r['member']:<14s} "
            f"${r['total_advances_drawn']:>9,.2f} "
            f"${r['actual_labor_share']:>12,.2f} "
            f"${r['net_distribution']:>11,.2f} "
            f"${r['overage']:>9,.2f} "
            f"{r['status']}"
        )


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Portland Housing Co-op — Labor Advance Tracker"
    )
    parser.add_argument(
        "--data-dir", type=str, default="./data",
        help="Directory for JSON data files (default: ./data)",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output summary report as JSON",
    )
    parser.add_argument(
        "--project", type=str, default="123 SE Foster Rd",
        help="Project name to report on",
    )
    args = parser.parse_args()

    print("\n  Building sample data...\n")
    tracker = build_sample_tracker()

    print()
    if args.json:
        report = tracker.summary_report("123 SE Foster Rd")
        print(json.dumps(report, indent=2))
    else:
        tracker.print_report("123 SE Foster Rd")
        demonstrate_reconciliation(tracker)

    print()


if __name__ == "__main__":
    main()
