#!/usr/bin/env python3
"""
Portland Housing Co-op — Member Equity & Advance Tracker
Author: Ledger (CFO)
Date: 2026-04-08

Tracks member capital accounts, labor hours, and labor advances across projects.
Designed to be the single source of truth for member equity positions.

Usage:
    python equity_tracker.py                # Show current state with example data
    python equity_tracker.py --json         # Output as JSON
"""

import argparse
import json
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Dict, List, Optional


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Transaction:
    """A single transaction on a member's capital account."""
    date: str
    type: str  # "buy_in", "additional_contribution", "profit_allocation", "loss_allocation", "withdrawal", "advance", "advance_repayment"
    amount: float
    description: str
    project: Optional[str] = None


@dataclass
class LaborLog:
    """A daily labor log entry."""
    date: str
    project: str
    trade: str
    hours: float
    description: str


@dataclass
class AdvanceRecord:
    """A labor advance drawn by a member."""
    date: str
    project: str
    amount: float
    status: str = "outstanding"  # "outstanding", "repaid", "deducted"
    repayment_date: Optional[str] = None


@dataclass
class MemberAccount:
    """Complete financial record for a co-op member."""
    name: str
    member_id: str
    join_date: str
    role: str
    primary_trade: str
    transactions: List[Transaction] = field(default_factory=list)
    labor_logs: List[LaborLog] = field(default_factory=list)
    advances: List[AdvanceRecord] = field(default_factory=list)

    @property
    def capital_balance(self) -> float:
        """Current capital account balance."""
        return sum(t.amount for t in self.transactions)

    @property
    def initial_buyin(self) -> float:
        """Original buy-in amount."""
        return sum(t.amount for t in self.transactions if t.type == "buy_in")

    @property
    def total_profit_allocated(self) -> float:
        """Total profit allocated to this member across all projects."""
        return sum(t.amount for t in self.transactions if t.type == "profit_allocation")

    @property
    def total_distributed(self) -> float:
        """Total cash distributed to this member."""
        return sum(abs(t.amount) for t in self.transactions if t.type == "withdrawal")

    @property
    def outstanding_advances(self) -> float:
        """Total advances not yet repaid/deducted."""
        return sum(a.amount for a in self.advances if a.status == "outstanding")

    @property
    def total_hours_all_projects(self) -> float:
        """Total labor hours across all projects."""
        return sum(log.hours for log in self.labor_logs)

    def hours_by_project(self) -> Dict[str, float]:
        """Hours worked per project."""
        result: Dict[str, float] = {}
        for log in self.labor_logs:
            result[log.project] = result.get(log.project, 0) + log.hours
        return result

    def hours_by_trade(self) -> Dict[str, float]:
        """Hours worked per trade category."""
        result: Dict[str, float] = {}
        for log in self.labor_logs:
            result[log.trade] = result.get(log.trade, 0) + log.hours
        return result

    def add_buyin(self, amount: float, dt: str = "") -> None:
        """Record initial buy-in."""
        if not dt:
            dt = date.today().isoformat()
        self.transactions.append(Transaction(
            date=dt, type="buy_in", amount=amount,
            description=f"Initial member buy-in"
        ))

    def add_contribution(self, amount: float, dt: str = "", desc: str = "") -> None:
        """Record additional capital contribution."""
        if not dt:
            dt = date.today().isoformat()
        self.transactions.append(Transaction(
            date=dt, type="additional_contribution", amount=amount,
            description=desc or "Additional capital contribution"
        ))

    def allocate_profit(self, amount: float, project: str, dt: str = "") -> None:
        """Record profit allocation from a completed project."""
        if not dt:
            dt = date.today().isoformat()
        self.transactions.append(Transaction(
            date=dt, type="profit_allocation", amount=amount,
            description=f"Profit allocation from {project}",
            project=project,
        ))

    def allocate_loss(self, amount: float, project: str, dt: str = "") -> None:
        """Record loss allocation (negative amount)."""
        if not dt:
            dt = date.today().isoformat()
        self.transactions.append(Transaction(
            date=dt, type="loss_allocation", amount=-abs(amount),
            description=f"Loss allocation from {project}",
            project=project,
        ))

    def record_distribution(self, amount: float, dt: str = "", desc: str = "") -> None:
        """Record cash distribution to member."""
        if not dt:
            dt = date.today().isoformat()
        self.transactions.append(Transaction(
            date=dt, type="withdrawal", amount=-abs(amount),
            description=desc or "Member distribution"
        ))

    def log_hours(self, project: str, trade: str, hours: float, dt: str = "", desc: str = "") -> None:
        """Log labor hours for a project."""
        if not dt:
            dt = date.today().isoformat()
        self.labor_logs.append(LaborLog(
            date=dt, project=project, trade=trade, hours=hours,
            description=desc or f"{trade} work on {project}"
        ))

    def draw_advance(self, project: str, amount: float, dt: str = "") -> None:
        """Record a labor advance draw."""
        if not dt:
            dt = date.today().isoformat()
        self.advances.append(AdvanceRecord(
            date=dt, project=project, amount=amount,
        ))
        self.transactions.append(Transaction(
            date=dt, type="advance", amount=-abs(amount),
            description=f"Labor advance draw — {project}",
            project=project,
        ))

    def repay_advance(self, project: str, amount: float, dt: str = "", from_distribution: bool = True) -> None:
        """Record advance repayment (typically deducted from distribution)."""
        if not dt:
            dt = date.today().isoformat()
        # Mark advances as repaid
        remaining = amount
        for adv in self.advances:
            if adv.project == project and adv.status == "outstanding" and remaining > 0:
                if remaining >= adv.amount:
                    remaining -= adv.amount
                    adv.status = "deducted" if from_distribution else "repaid"
                    adv.repayment_date = dt
                else:
                    # Partial repayment — split the record
                    adv.amount -= remaining
                    remaining = 0
        self.transactions.append(Transaction(
            date=dt, type="advance_repayment", amount=abs(amount),
            description=f"Advance repayment — {project} ({'deducted from distribution' if from_distribution else 'cash repayment'})",
            project=project,
        ))


# ============================================================================
# CO-OP LEDGER (all members)
# ============================================================================

@dataclass
class CoopLedger:
    """Master ledger tracking all member accounts and co-op reserves."""
    members: List[MemberAccount] = field(default_factory=list)
    reserve_balance: float = 0.0
    overhead_recovered: float = 0.0

    @property
    def total_capital(self) -> float:
        return sum(m.capital_balance for m in self.members)

    @property
    def total_outstanding_advances(self) -> float:
        return sum(m.outstanding_advances for m in self.members)

    def add_member(self, member: MemberAccount) -> None:
        self.members.append(member)

    def get_member(self, name: str) -> Optional[MemberAccount]:
        for m in self.members:
            if m.name == name:
                return m
        return None

    def fund_reserves(self, amount: float) -> None:
        self.reserve_balance += amount

    def draw_reserves(self, amount: float) -> None:
        self.reserve_balance -= amount

    def recover_overhead(self, amount: float) -> None:
        self.overhead_recovered += amount

    def capital_percentages(self) -> Dict[str, float]:
        total = self.total_capital
        if total == 0:
            return {m.name: 0 for m in self.members}
        return {m.name: m.capital_balance / total for m in self.members}


# ============================================================================
# OUTPUT
# ============================================================================

def fmt(amount: float) -> str:
    if amount < 0:
        return f"-${abs(amount):,.2f}"
    return f"${amount:,.2f}"


def print_ledger_report(ledger: CoopLedger):
    w = 80
    print("=" * w)
    print("  PORTLAND HOUSING CO-OP — MEMBER EQUITY REPORT")
    print(f"  Report Date: {date.today().isoformat()}")
    print("=" * w)

    print(f"\n  Co-op Summary:")
    print(f"    Total Member Capital:       {fmt(ledger.total_capital)}")
    print(f"    Reserve Balance:            {fmt(ledger.reserve_balance)}")
    print(f"    Overhead Recovered YTD:     {fmt(ledger.overhead_recovered)}")
    print(f"    Outstanding Advances:       {fmt(ledger.total_outstanding_advances)}")
    print(f"    Active Members:             {len(ledger.members)}")

    print(f"\n  Capital Accounts:")
    print(f"  {'Member':<14s} {'Buy-In':>10s} {'Profit':>10s} {'Distrib.':>10s} {'Advances':>10s} {'Balance':>10s} {'%':>7s}")
    print(f"  {'─'*14} {'─'*10} {'─'*10} {'─'*10} {'─'*10} {'─'*10} {'─'*7}")

    pcts = ledger.capital_percentages()
    for m in ledger.members:
        print(
            f"  {m.name:<14s} "
            f"{fmt(m.initial_buyin):>10s} "
            f"{fmt(m.total_profit_allocated):>10s} "
            f"{fmt(m.total_distributed):>10s} "
            f"{fmt(m.outstanding_advances):>10s} "
            f"{fmt(m.capital_balance):>10s} "
            f"{pcts[m.name]*100:>6.1f}%"
        )

    print(f"\n  Labor Summary (All Projects):")
    print(f"  {'Member':<14s} {'Total Hours':>12s} {'Primary Trade':<18s}")
    print(f"  {'─'*14} {'─'*12} {'─'*18}")
    for m in ledger.members:
        print(f"  {m.name:<14s} {m.total_hours_all_projects:>11.1f}h {m.primary_trade:<18s}")

    # Advance detail
    has_advances = any(m.outstanding_advances > 0 for m in ledger.members)
    if has_advances:
        print(f"\n  Outstanding Advances:")
        print(f"  {'Member':<14s} {'Project':<25s} {'Date':>12s} {'Amount':>10s} {'Status':<12s}")
        print(f"  {'─'*14} {'─'*25} {'─'*12} {'─'*10} {'─'*12}")
        for m in ledger.members:
            for adv in m.advances:
                if adv.status == "outstanding":
                    print(
                        f"  {m.name:<14s} "
                        f"{adv.project:<25s} "
                        f"{adv.date:>12s} "
                        f"{fmt(adv.amount):>10s} "
                        f"{adv.status:<12s}"
                    )

    # Transaction history
    print(f"\n  Recent Transactions (last 20):")
    print(f"  {'Date':>12s} {'Member':<14s} {'Type':<22s} {'Amount':>12s} {'Description'}")
    print(f"  {'─'*12} {'─'*14} {'─'*22} {'─'*12} {'─'*30}")

    all_txns = []
    for m in ledger.members:
        for t in m.transactions:
            all_txns.append((t.date, m.name, t))
    all_txns.sort(key=lambda x: x[0], reverse=True)

    for dt, name, t in all_txns[:20]:
        print(
            f"  {dt:>12s} "
            f"{name:<14s} "
            f"{t.type:<22s} "
            f"{fmt(t.amount):>12s} "
            f"{t.description[:40]}"
        )

    print(f"\n{'=' * w}")


def ledger_to_json(ledger: CoopLedger) -> dict:
    """Export ledger to JSON."""
    return {
        "report_date": date.today().isoformat(),
        "summary": {
            "total_capital": round(ledger.total_capital, 2),
            "reserve_balance": round(ledger.reserve_balance, 2),
            "overhead_recovered": round(ledger.overhead_recovered, 2),
            "outstanding_advances": round(ledger.total_outstanding_advances, 2),
            "member_count": len(ledger.members),
        },
        "members": [
            {
                "name": m.name,
                "member_id": m.member_id,
                "join_date": m.join_date,
                "role": m.role,
                "primary_trade": m.primary_trade,
                "capital_balance": round(m.capital_balance, 2),
                "initial_buyin": round(m.initial_buyin, 2),
                "total_profit_allocated": round(m.total_profit_allocated, 2),
                "total_distributed": round(m.total_distributed, 2),
                "outstanding_advances": round(m.outstanding_advances, 2),
                "total_hours": m.total_hours_all_projects,
                "capital_pct": round(m.capital_balance / ledger.total_capital * 100, 2) if ledger.total_capital > 0 else 0,
                "hours_by_project": m.hours_by_project(),
                "hours_by_trade": m.hours_by_trade(),
            }
            for m in ledger.members
        ],
    }


# ============================================================================
# EXAMPLE: Simulate co-op lifecycle through first flip
# ============================================================================

def build_example_ledger() -> CoopLedger:
    """Build a ledger with example data showing the full lifecycle."""
    ledger = CoopLedger()

    # --- Formation (Month 1) ---
    members_data = [
        ("Maven", "M001", "Founder/Operations", "operations", 50_000),
        ("Member B", "M002", "Plumber", "plumbing", 35_000),
        ("Member C", "M003", "Carpenter", "carpentry", 30_000),
        ("Member D", "M004", "Roofer", "roofing", 30_000),
        ("Member E", "M005", "Electrician", "electrical", 30_000),
        ("Member F", "M006", "Painter", "painting", 25_000),
    ]

    for name, mid, role, trade, buyin in members_data:
        m = MemberAccount(name=name, member_id=mid, join_date="2026-05-01", role=role, primary_trade=trade)
        m.add_buyin(buyin, "2026-05-01")
        ledger.add_member(m)

    # --- Rehab Phase (Months 3-8): Log labor hours ---
    labor_data = [
        ("Maven", "123 SE Foster", "operations", [
            ("2026-07-01", 40), ("2026-07-15", 35), ("2026-08-01", 40),
            ("2026-08-15", 35), ("2026-09-01", 30), ("2026-09-15", 20),
        ]),
        ("Member B", "123 SE Foster", "plumbing", [
            ("2026-07-01", 50), ("2026-07-15", 60), ("2026-08-01", 70),
            ("2026-08-15", 60), ("2026-09-01", 55), ("2026-09-15", 55),
        ]),
        ("Member C", "123 SE Foster", "carpentry", [
            ("2026-07-01", 65), ("2026-07-15", 70), ("2026-08-01", 65),
            ("2026-08-15", 60), ("2026-09-01", 70), ("2026-09-15", 70),
        ]),
        ("Member D", "123 SE Foster", "roofing", [
            ("2026-07-15", 80), ("2026-08-01", 75), ("2026-08-15", 70),
            ("2026-09-01", 45), ("2026-09-15", 30),
        ]),
        ("Member E", "123 SE Foster", "electrical", [
            ("2026-07-15", 40), ("2026-08-01", 55), ("2026-08-15", 50),
            ("2026-09-01", 55), ("2026-09-15", 50),
        ]),
        ("Member F", "123 SE Foster", "painting", [
            ("2026-08-15", 40), ("2026-09-01", 80), ("2026-09-15", 90),
            ("2026-10-01", 90),
        ]),
    ]

    for name, project, trade, entries in labor_data:
        m = ledger.get_member(name)
        if m:
            for dt, hrs in entries:
                m.log_hours(project, trade, hrs, dt, f"Biweekly log — {trade}")

    # --- Advances (Month 4-5 of rehab) ---
    member_b = ledger.get_member("Member B")
    if member_b:
        member_b.draw_advance("123 SE Foster", 500, "2026-08-15")
        member_b.draw_advance("123 SE Foster", 500, "2026-09-15")

    member_c = ledger.get_member("Member C")
    if member_c:
        member_c.draw_advance("123 SE Foster", 800, "2026-09-01")

    member_d = ledger.get_member("Member D")
    if member_d:
        member_d.draw_advance("123 SE Foster", 500, "2026-08-15")

    # --- Project Complete (Month 10): Allocate profit ---
    # Gross profit: $30,700 (conservative scenario)
    # This would be calculated by profit_splitter.py in production;
    # here we hard-code the results for demonstration.

    profit_allocations = [
        ("Maven", 3_436.00),
        ("Member B", 4_193.00),
        ("Member C", 4_106.00),
        ("Member D", 3_424.00),
        ("Member E", 3_225.00),
        ("Member F", 2_855.00),
    ]

    for name, alloc in profit_allocations:
        m = ledger.get_member(name)
        if m:
            m.allocate_profit(alloc, "123 SE Foster", "2026-11-15")

    # Reserve and overhead from this flip
    ledger.fund_reserves(6_140.00)  # 20% of $30,700
    ledger.recover_overhead(3_070.00)  # 10% of $30,700

    # Repay advances from distributions
    if member_b:
        member_b.repay_advance("123 SE Foster", 1_000, "2026-11-15")
    if member_c:
        member_c.repay_advance("123 SE Foster", 800, "2026-11-15")
    if member_d:
        member_d.repay_advance("123 SE Foster", 500, "2026-11-15")

    return ledger


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Portland Housing Co-op Equity Tracker")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    ledger = build_example_ledger()

    if args.json:
        print(json.dumps(ledger_to_json(ledger), indent=2))
    else:
        print_ledger_report(ledger)


if __name__ == "__main__":
    main()
