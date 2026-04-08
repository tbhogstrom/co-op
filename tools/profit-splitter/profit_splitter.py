#!/usr/bin/env python3
"""
Portland Housing Co-op — Profit Splitter
Author: Ledger (CFO)
Date: 2026-04-08

Main calculator for the co-op's profit distribution formula.
Takes project P&L and member data, outputs per-member distributions.

Usage:
    python profit_splitter.py                    # Run with example data
    python profit_splitter.py --json             # Output as JSON
    python profit_splitter.py --sale-price 500000 --total-cost 420000  # Custom deal
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ============================================================================
# CONFIGURATION — Approved M1 profit split percentages
# ============================================================================

RESERVE_PCT = 0.20      # 20% to co-op reserves
OVERHEAD_PCT = 0.10     # 10% to overhead recovery
CAPITAL_PCT = 0.30      # 30% to capital contributors
LABOR_PCT = 0.40        # 40% to labor contributors

# Trade rate multipliers for labor weighting
TRADE_MULTIPLIERS = {
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

# Advance policy
MAX_ADVANCE_PCT = 0.50  # 50% of estimated labor share


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class LaborEntry:
    """A block of hours worked by a member in a specific trade."""
    trade: str
    hours: float

    @property
    def multiplier(self) -> float:
        return TRADE_MULTIPLIERS.get(self.trade, 1.0)

    @property
    def weighted_hours(self) -> float:
        return self.hours * self.multiplier


@dataclass
class Member:
    """A co-op member with capital and labor contributions."""
    name: str
    capital_account: float  # Current capital account balance
    labor_entries: List[LaborEntry] = field(default_factory=list)
    advances_drawn: float = 0.0  # Total advances drawn during this project

    @property
    def total_hours(self) -> float:
        return sum(e.hours for e in self.labor_entries)

    @property
    def total_weighted_hours(self) -> float:
        return sum(e.weighted_hours for e in self.labor_entries)

    def labor_by_trade(self) -> Dict[str, Tuple[float, float]]:
        """Returns {trade: (raw_hours, weighted_hours)}."""
        result = {}
        for e in self.labor_entries:
            if e.trade not in result:
                result[e.trade] = (0.0, 0.0)
            raw, weighted = result[e.trade]
            result[e.trade] = (raw + e.hours, weighted + e.weighted_hours)
        return result


@dataclass
class ProjectResult:
    """Financial result of a completed flip."""
    project_name: str
    sale_price: float
    total_cost: float  # All-in cost (purchase + rehab + carry + acquisition + selling)

    @property
    def gross_profit(self) -> float:
        return self.sale_price - self.total_cost


@dataclass
class Distribution:
    """Calculated distribution for a single member."""
    member_name: str
    capital_share: float
    labor_share: float
    gross_distribution: float
    advances_deducted: float
    net_distribution: float
    capital_pct: float
    labor_pct: float
    labor_weighted_hours: float
    total_hours: float


@dataclass
class SplitResult:
    """Full result of the profit split calculation."""
    project_name: str
    gross_profit: float
    to_reserves: float
    to_overhead: float
    capital_pool: float
    labor_pool: float
    total_capital: float
    total_weighted_hours: float
    distributions: List[Distribution]
    is_loss: bool = False


# ============================================================================
# CALCULATOR
# ============================================================================

def calculate_split(
    project: ProjectResult,
    members: List[Member],
) -> SplitResult:
    """
    Calculate the profit split for a completed project.

    Args:
        project: Financial result of the flip.
        members: List of members with capital and labor data.

    Returns:
        SplitResult with per-member distributions.
    """
    gp = project.gross_profit
    is_loss = gp <= 0

    if is_loss:
        # Loss scenario: allocate loss to capital accounts proportionally
        total_capital = sum(m.capital_account for m in members)
        distributions = []
        for m in members:
            cap_pct = m.capital_account / total_capital if total_capital > 0 else 0
            loss_share = gp * cap_pct  # Negative number
            distributions.append(Distribution(
                member_name=m.name,
                capital_share=loss_share,
                labor_share=0.0,
                gross_distribution=loss_share,
                advances_deducted=m.advances_drawn,
                net_distribution=loss_share - m.advances_drawn,
                capital_pct=cap_pct,
                labor_pct=0.0,
                labor_weighted_hours=m.total_weighted_hours,
                total_hours=m.total_hours,
            ))
        return SplitResult(
            project_name=project.project_name,
            gross_profit=gp,
            to_reserves=0.0,
            to_overhead=0.0,
            capital_pool=gp,
            labor_pool=0.0,
            total_capital=total_capital,
            total_weighted_hours=sum(m.total_weighted_hours for m in members),
            distributions=distributions,
            is_loss=True,
        )

    # Normal profit scenario
    to_reserves = gp * RESERVE_PCT
    to_overhead = gp * OVERHEAD_PCT
    capital_pool = gp * CAPITAL_PCT
    labor_pool = gp * LABOR_PCT

    total_capital = sum(m.capital_account for m in members)
    total_weighted_hours = sum(m.total_weighted_hours for m in members)

    distributions = []
    for m in members:
        # Capital share
        cap_pct = m.capital_account / total_capital if total_capital > 0 else 0
        cap_share = capital_pool * cap_pct

        # Labor share
        lab_pct = m.total_weighted_hours / total_weighted_hours if total_weighted_hours > 0 else 0
        lab_share = labor_pool * lab_pct

        gross = cap_share + lab_share
        net = gross - m.advances_drawn

        distributions.append(Distribution(
            member_name=m.name,
            capital_share=cap_share,
            labor_share=lab_share,
            gross_distribution=gross,
            advances_deducted=m.advances_drawn,
            net_distribution=net,
            capital_pct=cap_pct,
            labor_pct=lab_pct,
            labor_weighted_hours=m.total_weighted_hours,
            total_hours=m.total_hours,
        ))

    return SplitResult(
        project_name=project.project_name,
        gross_profit=gp,
        to_reserves=to_reserves,
        to_overhead=to_overhead,
        capital_pool=capital_pool,
        labor_pool=labor_pool,
        total_capital=total_capital,
        total_weighted_hours=total_weighted_hours,
        distributions=distributions,
    )


def calculate_max_advance(
    member: Member,
    conservative_gross_profit: float,
    all_members: List[Member],
) -> float:
    """
    Calculate the maximum advance a member can draw.

    Uses conservative gross profit estimate and current labor hour projections.
    """
    if conservative_gross_profit <= 0:
        return 0.0

    labor_pool = conservative_gross_profit * LABOR_PCT
    total_wh = sum(m.total_weighted_hours for m in all_members)
    if total_wh == 0:
        return 0.0

    member_share = labor_pool * (member.total_weighted_hours / total_wh)
    return member_share * MAX_ADVANCE_PCT


# ============================================================================
# OUTPUT FORMATTERS
# ============================================================================

def fmt(amount: float) -> str:
    """Format as USD."""
    if amount < 0:
        return f"-${abs(amount):,.2f}"
    return f"${amount:,.2f}"


def print_split_report(result: SplitResult):
    """Print a human-readable distribution report."""
    w = 78
    print("=" * w)
    print(f"  PROFIT DISTRIBUTION REPORT — {result.project_name}")
    print("=" * w)

    if result.is_loss:
        print(f"\n  ⚠ PROJECT LOSS: {fmt(result.gross_profit)}")
        print(f"  Loss allocated to member capital accounts proportionally.\n")
    else:
        print(f"\n  Gross Profit:           {fmt(result.gross_profit)}")
        print(f"  To Reserves (20%):      {fmt(result.to_reserves)}")
        print(f"  To Overhead (10%):      {fmt(result.to_overhead)}")
        print(f"  Capital Pool (30%):     {fmt(result.capital_pool)}")
        print(f"  Labor Pool (40%):       {fmt(result.labor_pool)}")

    print(f"\n  Total Member Capital:   {fmt(result.total_capital)}")
    print(f"  Total Weighted Hours:   {result.total_weighted_hours:,.1f}")

    print(f"\n  {'Member':<14s} {'Capital%':>8s} {'CapShare':>10s} {'Labor%':>8s} {'LabShare':>10s} {'Gross':>10s} {'Advances':>10s} {'Net':>10s}")
    print(f"  {'─'*14} {'─'*8} {'─'*10} {'─'*8} {'─'*10} {'─'*10} {'─'*10} {'─'*10}")

    for d in result.distributions:
        print(
            f"  {d.member_name:<14s} "
            f"{d.capital_pct*100:>7.1f}% "
            f"{fmt(d.capital_share):>10s} "
            f"{d.labor_pct*100:>7.1f}% "
            f"{fmt(d.labor_share):>10s} "
            f"{fmt(d.gross_distribution):>10s} "
            f"{fmt(d.advances_deducted):>10s} "
            f"{fmt(d.net_distribution):>10s}"
        )

    total_gross = sum(d.gross_distribution for d in result.distributions)
    total_advances = sum(d.advances_deducted for d in result.distributions)
    total_net = sum(d.net_distribution for d in result.distributions)

    print(f"  {'─'*14} {'─'*8} {'─'*10} {'─'*8} {'─'*10} {'─'*10} {'─'*10} {'─'*10}")
    print(
        f"  {'TOTAL':<14s} {'':>8s} {'':>10s} {'':>8s} {'':>10s} "
        f"{fmt(total_gross):>10s} {fmt(total_advances):>10s} {fmt(total_net):>10s}"
    )

    if not result.is_loss:
        print(f"\n  Accounting Check:")
        total_allocated = result.to_reserves + result.to_overhead + total_gross
        print(f"    Reserves + Overhead + Distributions = {fmt(total_allocated)}")
        print(f"    Gross Profit                        = {fmt(result.gross_profit)}")
        diff = abs(total_allocated - result.gross_profit)
        if diff < 0.01:
            print(f"    ✅ Balanced (difference: {fmt(diff)})")
        else:
            print(f"    ⚠ Rounding difference: {fmt(diff)}")

    # Per-member ROI
    print(f"\n  Per-Member Returns:")
    print(f"  {'Member':<14s} {'Buy-In':>10s} {'Distribution':>14s} {'ROI':>8s} {'Hours':>8s} {'$/Hour':>8s}")
    print(f"  {'─'*14} {'─'*10} {'─'*14} {'─'*8} {'─'*8} {'─'*8}")
    for d in result.distributions:
        roi = d.gross_distribution / d.capital_pct / result.total_capital * 100 if d.capital_pct > 0 else 0
        per_hour = d.gross_distribution / d.total_hours if d.total_hours > 0 else 0
        cap_amt = d.capital_pct * result.total_capital
        print(
            f"  {d.member_name:<14s} "
            f"{fmt(cap_amt):>10s} "
            f"{fmt(d.gross_distribution):>14s} "
            f"{roi:>7.1f}% "
            f"{d.total_hours:>7.0f}h "
            f"{fmt(per_hour):>8s}"
        )

    print(f"\n{'=' * w}")


def to_json(result: SplitResult) -> dict:
    """Convert result to JSON-serializable dict."""
    return {
        "project_name": result.project_name,
        "gross_profit": round(result.gross_profit, 2),
        "is_loss": result.is_loss,
        "allocation": {
            "to_reserves": round(result.to_reserves, 2),
            "to_overhead": round(result.to_overhead, 2),
            "capital_pool": round(result.capital_pool, 2),
            "labor_pool": round(result.labor_pool, 2),
        },
        "totals": {
            "total_capital": round(result.total_capital, 2),
            "total_weighted_hours": round(result.total_weighted_hours, 2),
        },
        "distributions": [
            {
                "member": d.member_name,
                "capital_pct": round(d.capital_pct, 4),
                "capital_share": round(d.capital_share, 2),
                "labor_pct": round(d.labor_pct, 4),
                "labor_share": round(d.labor_share, 2),
                "gross_distribution": round(d.gross_distribution, 2),
                "advances_deducted": round(d.advances_deducted, 2),
                "net_distribution": round(d.net_distribution, 2),
                "total_hours": d.total_hours,
                "weighted_hours": round(d.labor_weighted_hours, 2),
            }
            for d in result.distributions
        ],
    }


# ============================================================================
# EXAMPLE DATA
# ============================================================================

def example_members() -> List[Member]:
    """
    Return example member data matching Maven's approved 6-member scenario:
    Maven $50K/200hrs/1.15x PM, Birch $15K/500hrs/1.0x carpentry,
    Slate $10K/400hrs/1.1x roofing, Copper $25K/350hrs/1.2x plumbing,
    Member E $15K/300hrs/1.0x general, Member F $5K/250hrs/1.0x general.
    """
    return [
        Member(
            name="Maven",
            capital_account=50_000,
            labor_entries=[LaborEntry("project_management", 200)],
            advances_drawn=0,
        ),
        Member(
            name="Birch",
            capital_account=15_000,
            labor_entries=[LaborEntry("carpentry", 500)],
            advances_drawn=1_200,
        ),
        Member(
            name="Slate",
            capital_account=10_000,
            labor_entries=[LaborEntry("roofing", 400)],
            advances_drawn=800,
        ),
        Member(
            name="Copper",
            capital_account=25_000,
            labor_entries=[LaborEntry("plumbing", 350)],
            advances_drawn=1_000,
        ),
        Member(
            name="Member E",
            capital_account=15_000,
            labor_entries=[LaborEntry("general_labor", 300)],
            advances_drawn=500,
        ),
        Member(
            name="Member F",
            capital_account=5_000,
            labor_entries=[LaborEntry("general_labor", 250)],
            advances_drawn=0,
        ),
    ]


def example_project(sale_price: float = 475_000, total_cost: float = 444_300) -> ProjectResult:
    """Return example project data."""
    return ProjectResult(
        project_name="123 SE Foster Rd (Example)",
        sale_price=sale_price,
        total_cost=total_cost,
    )


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Portland Housing Co-op Profit Splitter")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--sale-price", type=float, default=475_000, help="Sale price (ARV)")
    parser.add_argument("--total-cost", type=float, default=444_300, help="Total project cost")
    args = parser.parse_args()

    project = example_project(args.sale_price, args.total_cost)
    members = example_members()

    result = calculate_split(project, members)

    if args.json:
        print(json.dumps(to_json(result), indent=2))
    else:
        print_split_report(result)

        # Also show advance eligibility
        print(f"\n  ADVANCE ELIGIBILITY (based on conservative GP estimate)")
        print(f"  {'Member':<14s} {'Est. Labor Share':>16s} {'Max Advance':>14s} {'Already Drawn':>14s} {'Remaining':>14s}")
        print(f"  {'─'*14} {'─'*16} {'─'*14} {'─'*14} {'─'*14}")
        for m in members:
            max_adv = calculate_max_advance(m, project.gross_profit, members)
            remaining = max(0, max_adv - m.advances_drawn)
            est_share = result.labor_pool * (m.total_weighted_hours / result.total_weighted_hours) if result.total_weighted_hours > 0 else 0
            print(
                f"  {m.name:<14s} "
                f"{fmt(est_share):>16s} "
                f"{fmt(max_adv):>14s} "
                f"{fmt(m.advances_drawn):>14s} "
                f"{fmt(remaining):>14s}"
            )
        print()


if __name__ == "__main__":
    main()
