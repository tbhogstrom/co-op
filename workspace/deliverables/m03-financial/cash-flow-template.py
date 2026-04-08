#!/usr/bin/env python3
"""
Portland Housing Co-op — Per-Project Cash Flow Projection Tool
Author: Ledger (CFO)
Date: 2026-04-08

Projects monthly cash flows for a single flip, including labor advances.

Usage:
    python cash-flow-template.py
    python cash-flow-template.py --purchase 280000 --rehab 65000 --arv 500000 --hold 5
"""

import argparse
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class FlipCashFlow:
    """Cash flow projector for a single flip."""
    purchase_price: float = 300_000
    rehab_budget: float = 75_000
    arv: float = 475_000
    hold_months: int = 6
    hard_money_ltv: float = 0.85
    hard_money_rate: float = 0.12
    hard_money_points: float = 0.03
    hard_money_rehab_pct: float = 0.70
    selling_commission_pct: float = 0.06
    monthly_overhead_alloc: float = 4_872  # $58,465 / 12
    max_labor_advances: float = 6_000  # Total advances across all members
    coop_starting_cash: float = 120_000  # Based on approved $120K capitalization

    @property
    def loan_amount(self) -> float:
        return self.purchase_price * self.hard_money_ltv

    @property
    def down_payment(self) -> float:
        return self.purchase_price * (1 - self.hard_money_ltv)

    @property
    def origination_fee(self) -> float:
        return self.loan_amount * self.hard_money_points

    @property
    def monthly_interest(self) -> float:
        return self.loan_amount * (self.hard_money_rate / 12)

    @property
    def rehab_cash_portion(self) -> float:
        return self.rehab_budget * (1 - self.hard_money_rehab_pct)

    def project(self) -> List[Dict]:
        """
        Generate month-by-month cash flow.
        Timeline: Month 1 = acquisition, Months 2-N = rehab, Month N+1 = sale.
        """
        months = []
        balance = self.coop_starting_cash
        total_months = self.hold_months + 1  # +1 for sale month

        acq_costs = self.origination_fee + 600 + 500 + 2500 + 400 + 3000  # origination, insp, appr, title, survey, permits
        monthly_carry = self.monthly_interest + 375 + 250 + 300  # interest, tax, ins, util
        monthly_rehab_cash = self.rehab_cash_portion / self.hold_months
        monthly_dumpster = 2500 / self.hold_months

        # Advance schedule: spread across months 3 to hold_months-1
        advance_months = max(1, self.hold_months - 3)
        monthly_advance = self.max_labor_advances / advance_months if advance_months > 0 else 0

        for month in range(1, total_months + 1):
            row = {
                "month": month,
                "phase": "",
                "down_payment": 0.0,
                "acquisition": 0.0,
                "rehab_materials": 0.0,
                "carrying_costs": 0.0,
                "overhead": -self.monthly_overhead_alloc,
                "labor_advances": 0.0,
                "sale_proceeds": 0.0,
                "loan_payoff": 0.0,
                "selling_costs": 0.0,
                "total_out": 0.0,
                "total_in": 0.0,
                "net": 0.0,
                "balance": 0.0,
            }

            if month == 1:
                # Acquisition month
                row["phase"] = "ACQUIRE"
                row["down_payment"] = -self.down_payment
                row["acquisition"] = -acq_costs
                row["carrying_costs"] = -monthly_carry
                row["rehab_materials"] = -monthly_rehab_cash
            elif month <= self.hold_months:
                # Rehab months
                row["phase"] = "REHAB"
                row["carrying_costs"] = -monthly_carry
                row["rehab_materials"] = -(monthly_rehab_cash + monthly_dumpster)
                # Labor advances start after month 3
                if 3 <= month <= self.hold_months - 1:
                    row["labor_advances"] = -monthly_advance
            else:
                # Sale month
                row["phase"] = "SELL"
                selling = self.arv * self.selling_commission_pct + 2000 + 800 + 2500  # comm + staging + photo + closing
                loan_payoff = self.loan_amount + (self.rehab_budget * self.hard_money_rehab_pct)
                row["sale_proceeds"] = self.arv
                row["loan_payoff"] = -loan_payoff
                row["selling_costs"] = -selling

            row["total_out"] = (
                row["down_payment"] + row["acquisition"] + row["rehab_materials"]
                + row["carrying_costs"] + row["overhead"] + row["labor_advances"]
                + row["loan_payoff"] + row["selling_costs"]
            )
            row["total_in"] = row["sale_proceeds"]
            row["net"] = row["total_in"] + row["total_out"]
            balance += row["net"]
            row["balance"] = balance
            months.append(row)

        return months


def fmt(v: float) -> str:
    if v == 0:
        return "—"
    if v < 0:
        return f"-${abs(v):,.0f}"
    return f"${v:,.0f}"


def main():
    parser = argparse.ArgumentParser(description="Per-project cash flow projection")
    parser.add_argument("--purchase", type=float, default=300_000)
    parser.add_argument("--rehab", type=float, default=75_000)
    parser.add_argument("--arv", type=float, default=475_000)
    parser.add_argument("--hold", type=int, default=6)
    parser.add_argument("--cash", type=float, default=120_000, help="Co-op starting cash")
    args = parser.parse_args()

    cf = FlipCashFlow(
        purchase_price=args.purchase,
        rehab_budget=args.rehab,
        arv=args.arv,
        hold_months=args.hold,
        coop_starting_cash=args.cash,
    )

    months = cf.project()

    print()
    print("=" * 100)
    print("  PORTLAND HOUSING CO-OP — PROJECT CASH FLOW PROJECTION")
    print(f"  Purchase: {fmt(cf.purchase_price)} | Rehab: {fmt(cf.rehab_budget)} | ARV: {fmt(cf.arv)} | Hold: {cf.hold_months}mo")
    print(f"  Starting Cash: {fmt(cf.coop_starting_cash)}")
    print("=" * 100)

    header = (
        f"  {'Mo':>3s} {'Phase':<8s} {'Down Pmt':>10s} {'Acquis.':>10s} {'Rehab':>10s} "
        f"{'Carry':>10s} {'OH':>8s} {'Advances':>10s} {'Sale':>10s} {'LoanPay':>10s} "
        f"{'SellCost':>10s} {'NET':>12s} {'BALANCE':>12s}"
    )
    print(header)
    print("  " + "─" * 96)

    min_bal = float('inf')
    min_mo = 0
    for row in months:
        print(
            f"  {row['month']:>3d} {row['phase']:<8s} "
            f"{fmt(row['down_payment']):>10s} {fmt(row['acquisition']):>10s} "
            f"{fmt(row['rehab_materials']):>10s} {fmt(row['carrying_costs']):>10s} "
            f"{fmt(row['overhead']):>8s} {fmt(row['labor_advances']):>10s} "
            f"{fmt(row['sale_proceeds']):>10s} {fmt(row['loan_payoff']):>10s} "
            f"{fmt(row['selling_costs']):>10s} {fmt(row['net']):>12s} {fmt(row['balance']):>12s}"
        )
        if row['balance'] < min_bal:
            min_bal = row['balance']
            min_mo = row['month']

    print("  " + "─" * 96)
    print(f"\n  Lowest balance: {fmt(min_bal)} in month {min_mo}")

    if min_bal < 0:
        print(f"  🚨 CASH SHORTFALL — Co-op runs out of money! Need additional capital or smaller deal.")
    elif min_bal < 10_000:
        print(f"  🚨 CRITICAL — Balance drops below $10K. Extremely risky.")
    elif min_bal < 20_000:
        print(f"  ⚠ WARNING — Balance drops below $20K safety threshold.")
    else:
        print(f"  ✅ Cash position remains above $20K minimum throughout project.")

    # Gross profit
    total_in = sum(r['total_in'] for r in months)
    total_out = sum(abs(r['total_out']) for r in months)
    gp = months[-1]['balance'] - cf.coop_starting_cash + sum(r['overhead'] for r in months) * -1  # add back overhead
    final = months[-1]['balance']
    print(f"\n  Final cash balance: {fmt(final)}")
    print(f"  Net change from starting cash: {fmt(final - cf.coop_starting_cash)}")
    print(f"  (Includes overhead draw of {fmt(abs(sum(r['overhead'] for r in months)))})")

    print(f"\n{'=' * 100}\n")


if __name__ == "__main__":
    main()
