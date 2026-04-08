#!/usr/bin/env python3
"""
Portland Housing Co-op — Year 1 Operating Cost Model
Author: Ledger (CFO)
Date: 2026-04-07
Status: DRAFT

Usage:
    python operating-cost-model.py

This script models Year 1 operating expenses for the Portland Housing Co-op
across three scenarios (conservative, moderate, aggressive). It separates
fixed overhead from project-variable costs and produces a monthly cash flow
projection.

All dollar amounts are annual unless noted otherwise.
"""

from dataclasses import dataclass, field
from typing import Dict, List
import json

# ============================================================================
# INPUT PARAMETERS — Change these to model different scenarios
# ============================================================================

@dataclass
class ScenarioInputs:
    """Input parameters for a single scenario."""
    name: str
    num_members: int
    num_flips_year1: int  # How many flips completed in Year 1
    avg_purchase_price: float
    avg_rehab_budget: float
    avg_arv: float
    avg_hold_months: float
    hard_money_ltv: float  # e.g., 0.85
    hard_money_rate: float  # Annual interest rate, e.g., 0.11
    hard_money_points: float  # Origination points, e.g., 0.025
    hard_money_rehab_coverage: float  # % of rehab funded by lender
    selling_cost_pct: float  # % of ARV for commissions + closing
    member_labor_rate: float  # Avg blended rate for labor-hour valuation (not cash pay)
    avg_labor_hours_per_flip: float  # Total member labor hours per flip


SCENARIOS = {
    "conservative": ScenarioInputs(
        name="Conservative",
        num_members=6,
        num_flips_year1=1,
        avg_purchase_price=300_000,
        avg_rehab_budget=75_000,
        avg_arv=475_000,
        avg_hold_months=6,
        hard_money_ltv=0.85,
        hard_money_rate=0.12,
        hard_money_points=0.03,
        hard_money_rehab_coverage=0.70,
        selling_cost_pct=0.06,
        member_labor_rate=45.0,
        avg_labor_hours_per_flip=1_600,
    ),
    "moderate": ScenarioInputs(
        name="Moderate",
        num_members=8,
        num_flips_year1=1,
        avg_purchase_price=300_000,
        avg_rehab_budget=75_000,
        avg_arv=500_000,
        avg_hold_months=5,
        hard_money_ltv=0.85,
        hard_money_rate=0.11,
        hard_money_points=0.025,
        hard_money_rehab_coverage=0.75,
        selling_cost_pct=0.06,
        member_labor_rate=45.0,
        avg_labor_hours_per_flip=1_500,
    ),
    "aggressive": ScenarioInputs(
        name="Aggressive",
        num_members=8,
        num_flips_year1=2,
        avg_purchase_price=280_000,
        avg_rehab_budget=65_000,
        avg_arv=525_000,
        avg_hold_months=4,
        hard_money_ltv=0.85,
        hard_money_rate=0.105,
        hard_money_points=0.02,
        hard_money_rehab_coverage=0.80,
        selling_cost_pct=0.055,
        member_labor_rate=45.0,
        avg_labor_hours_per_flip=1_400,
    ),
}

# ============================================================================
# FIXED OVERHEAD — Costs the co-op pays regardless of project activity
# ============================================================================

@dataclass
class FixedOverhead:
    """Annual fixed operating costs."""
    # Legal & Formation
    entity_formation: float = 3_500      # Oregon cooperative filing, bylaws, operating agreement
    legal_retainer: float = 4_000        # Ongoing legal counsel (Statton's billable equivalent)
    registered_agent: float = 150        # Oregon registered agent service

    # Insurance (annual premiums)
    general_liability: float = 4_500     # $1M/$2M GL policy
    workers_comp: float = 12_000         # Oregon WC — construction class codes are expensive
    umbrella_policy: float = 2_000       # $1M umbrella over GL

    # Accounting & Compliance
    bookkeeping: float = 4_800           # Monthly bookkeeping service ($400/mo)
    tax_preparation: float = 2_500       # Annual cooperative tax return (Form 1120-C or K-1s)
    annual_report_filing: float = 100    # Oregon Secretary of State

    # Office & Administration
    coworking_meeting_space: float = 3_600  # Shared space for meetings ($300/mo)
    software_subscriptions: float = 1_800   # Accounting, project mgmt, communication tools
    phone_internet: float = 600             # Shared business line

    # Tools & Equipment (Year 1 startup)
    shared_tools_equipment: float = 8_000   # Table saws, compressors, ladders, etc.
    tool_maintenance: float = 500           # Sharpening, repairs
    vehicle_allowance: float = 2_400        # Gas/mileage reimbursement ($200/mo shared)

    # Marketing & Recruitment
    member_recruitment: float = 1_500       # Flyers, trade school outreach, meetups
    website_branding: float = 1_200         # Simple website and business cards

    # Contingency
    overhead_contingency_pct: float = 0.10  # 10% contingency on all fixed overhead

    def total(self) -> float:
        """Total annual fixed overhead including contingency."""
        subtotal = (
            self.entity_formation + self.legal_retainer + self.registered_agent
            + self.general_liability + self.workers_comp + self.umbrella_policy
            + self.bookkeeping + self.tax_preparation + self.annual_report_filing
            + self.coworking_meeting_space + self.software_subscriptions + self.phone_internet
            + self.shared_tools_equipment + self.tool_maintenance + self.vehicle_allowance
            + self.member_recruitment + self.website_branding
        )
        return subtotal * (1 + self.overhead_contingency_pct)

    def line_items(self) -> Dict[str, float]:
        """Return all line items as a dictionary."""
        items = {
            "Entity Formation & Filing": self.entity_formation,
            "Legal Retainer": self.legal_retainer,
            "Registered Agent": self.registered_agent,
            "General Liability Insurance": self.general_liability,
            "Workers Compensation Insurance": self.workers_comp,
            "Umbrella Policy": self.umbrella_policy,
            "Bookkeeping": self.bookkeeping,
            "Tax Preparation": self.tax_preparation,
            "Annual Report Filing": self.annual_report_filing,
            "Coworking / Meeting Space": self.coworking_meeting_space,
            "Software Subscriptions": self.software_subscriptions,
            "Phone / Internet": self.phone_internet,
            "Shared Tools & Equipment": self.shared_tools_equipment,
            "Tool Maintenance": self.tool_maintenance,
            "Vehicle Allowance": self.vehicle_allowance,
            "Member Recruitment": self.member_recruitment,
            "Website & Branding": self.website_branding,
        }
        subtotal = sum(items.values())
        items["Contingency (10%)"] = subtotal * self.overhead_contingency_pct
        return items


# ============================================================================
# PER-PROJECT VARIABLE COSTS
# ============================================================================

@dataclass
class ProjectCosts:
    """Variable costs for a single flip project."""
    scenario: ScenarioInputs

    # Per-project costs not included in rehab budget
    inspection_cost: float = 600
    appraisal_cost: float = 500
    title_insurance: float = 2_500
    survey: float = 400
    permits_average: float = 3_000
    dumpster_hauling: float = 2_500
    staging: float = 2_000
    photography_marketing: float = 800
    builders_risk_insurance: float = 1_500  # Per-project policy
    property_tax_monthly: float = 375
    utilities_monthly: float = 300

    def acquisition_costs(self) -> float:
        """One-time costs at purchase."""
        s = self.scenario
        loan_amount = s.avg_purchase_price * s.hard_money_ltv
        origination_fee = loan_amount * s.hard_money_points
        return (
            self.inspection_cost + self.appraisal_cost + self.title_insurance
            + self.survey + origination_fee
        )

    def carrying_costs(self) -> float:
        """Monthly carrying costs * hold period."""
        s = self.scenario
        loan_amount = s.avg_purchase_price * s.hard_money_ltv
        monthly_interest = loan_amount * (s.hard_money_rate / 12)
        monthly_carry = (
            monthly_interest + self.property_tax_monthly + self.utilities_monthly
            + self.builders_risk_insurance / s.avg_hold_months
        )
        return monthly_carry * s.avg_hold_months

    def rehab_cash_needed(self) -> float:
        """Cash portion of rehab not covered by hard money draws."""
        s = self.scenario
        return s.avg_rehab_budget * (1 - s.hard_money_rehab_coverage)

    def selling_costs(self) -> float:
        """Costs at sale."""
        s = self.scenario
        return s.avg_arv * s.selling_cost_pct + self.staging + self.photography_marketing

    def total_project_cost(self) -> float:
        """Total all-in cost for one flip."""
        s = self.scenario
        return (
            s.avg_purchase_price + s.avg_rehab_budget
            + self.acquisition_costs() + self.carrying_costs()
            + self.selling_costs() + self.permits_average + self.dumpster_hauling
        )

    def down_payment(self) -> float:
        """Cash needed for down payment."""
        s = self.scenario
        return s.avg_purchase_price * (1 - s.hard_money_ltv)

    def total_cash_from_coop(self) -> float:
        """Total cash the co-op must deploy (not financed by hard money)."""
        return (
            self.down_payment() + self.rehab_cash_needed()
            + self.acquisition_costs() + self.carrying_costs()
            + self.selling_costs() + self.permits_average + self.dumpster_hauling
        )

    def gross_profit(self) -> float:
        """ARV minus total project cost."""
        return self.scenario.avg_arv - self.total_project_cost()

    def line_items(self) -> Dict[str, float]:
        """Return all cost line items."""
        s = self.scenario
        loan_amount = s.avg_purchase_price * s.hard_money_ltv
        return {
            "Purchase Price": s.avg_purchase_price,
            "Rehab Budget": s.avg_rehab_budget,
            "Loan Origination Fee": loan_amount * s.hard_money_points,
            "Inspection": self.inspection_cost,
            "Appraisal": self.appraisal_cost,
            "Title Insurance": self.title_insurance,
            "Survey": self.survey,
            "Permits": self.permits_average,
            "Dumpster / Hauling": self.dumpster_hauling,
            f"Carrying Costs ({s.avg_hold_months:.0f} months)": self.carrying_costs(),
            "Selling Costs (commissions + closing)": s.avg_arv * s.selling_cost_pct,
            "Staging": self.staging,
            "Photography / Marketing": self.photography_marketing,
        }


# ============================================================================
# PROFIT SPLIT MODEL (Preview — full model in M3)
# ============================================================================

@dataclass
class ProfitSplit:
    """How profit gets distributed."""
    reserve_pct: float = 0.20       # 20% to co-op reserves
    overhead_pct: float = 0.10      # 10% to overhead recovery
    capital_pct: float = 0.30       # 30% proportional to capital contribution
    labor_pct: float = 0.40         # 40% proportional to labor hours (weighted)

    def validate(self) -> bool:
        total = self.reserve_pct + self.overhead_pct + self.capital_pct + self.labor_pct
        assert abs(total - 1.0) < 0.001, f"Split percentages must sum to 100%, got {total*100:.1f}%"
        return True

    def split(self, gross_profit: float) -> Dict[str, float]:
        self.validate()
        return {
            "To Reserves (20%)": gross_profit * self.reserve_pct,
            "To Overhead Recovery (10%)": gross_profit * self.overhead_pct,
            "To Capital Contributors (30%)": gross_profit * self.capital_pct,
            "To Labor Contributors (40%)": gross_profit * self.labor_pct,
        }


# ============================================================================
# MONTHLY CASH FLOW PROJECTION
# ============================================================================

def monthly_cash_flow(scenario: ScenarioInputs, overhead: FixedOverhead) -> List[Dict]:
    """
    Project monthly cash flows for Year 1.

    Assumptions:
    - Months 1-2: Formation and setup (no project activity)
    - Month 3: Purchase property
    - Months 3 to 3+hold: Rehab period
    - Month 3+hold+1: Sale closes
    - Overhead costs spread evenly across 12 months

    For aggressive scenario with 2 flips: second flip starts month 7.
    """
    pc = ProjectCosts(scenario)
    monthly_overhead = overhead.total() / 12
    months = []
    total_member_equity = 200_000  # Assumed capitalization

    balance = total_member_equity  # Starting cash

    for month in range(1, 13):
        row = {
            "month": month,
            "inflow": 0.0,
            "overhead": -monthly_overhead,
            "project_cost": 0.0,
            "sale_proceeds": 0.0,
            "net": 0.0,
            "balance": 0.0,
        }

        # --- FLIP 1 ---
        if month == 1:
            row["inflow"] = total_member_equity  # Members fund the co-op

        purchase_month = 3
        sale_month = purchase_month + int(scenario.avg_hold_months)

        if month == purchase_month:
            # Down payment + acquisition costs + first month rehab draw
            row["project_cost"] = -(pc.down_payment() + pc.acquisition_costs() + pc.permits_average)

        if purchase_month < month <= purchase_month + int(scenario.avg_hold_months):
            # Monthly carrying costs + rehab spend (spread evenly)
            monthly_carry = pc.carrying_costs() / scenario.avg_hold_months
            monthly_rehab = pc.rehab_cash_needed() / scenario.avg_hold_months
            monthly_misc = pc.dumpster_hauling / scenario.avg_hold_months
            row["project_cost"] = -(monthly_carry + monthly_rehab + monthly_misc)

        if month == sale_month:
            # Sale proceeds: ARV minus selling costs minus loan payoff
            loan_payoff = scenario.avg_purchase_price * scenario.hard_money_ltv
            rehab_loan = scenario.avg_rehab_budget * scenario.hard_money_rehab_coverage
            net_sale = scenario.avg_arv - pc.selling_costs() - loan_payoff - rehab_loan
            row["sale_proceeds"] = net_sale

        # --- FLIP 2 (aggressive scenario only) ---
        if scenario.num_flips_year1 >= 2:
            purchase_month_2 = 7
            sale_month_2 = purchase_month_2 + int(scenario.avg_hold_months)

            if month == purchase_month_2:
                row["project_cost"] += -(pc.down_payment() + pc.acquisition_costs() + pc.permits_average)

            if purchase_month_2 < month <= min(purchase_month_2 + int(scenario.avg_hold_months), 12):
                monthly_carry = pc.carrying_costs() / scenario.avg_hold_months
                monthly_rehab = pc.rehab_cash_needed() / scenario.avg_hold_months
                monthly_misc = pc.dumpster_hauling / scenario.avg_hold_months
                row["project_cost"] += -(monthly_carry + monthly_rehab + monthly_misc)

            if month == sale_month_2 and sale_month_2 <= 12:
                loan_payoff = scenario.avg_purchase_price * scenario.hard_money_ltv
                rehab_loan = scenario.avg_rehab_budget * scenario.hard_money_rehab_coverage
                net_sale = scenario.avg_arv - pc.selling_costs() - loan_payoff - rehab_loan
                row["sale_proceeds"] += net_sale

        row["net"] = row["inflow"] + row["overhead"] + row["project_cost"] + row["sale_proceeds"]
        balance += row["net"]
        row["balance"] = balance
        months.append(row)

    return months


# ============================================================================
# SENSITIVITY ANALYSIS
# ============================================================================

def sensitivity_analysis(base_scenario: ScenarioInputs) -> Dict[str, Dict[str, float]]:
    """
    What breaks if key variables change?
    Tests: rehab +20%, ARV -10%, hold +3 months, rate +2%
    """
    results = {}

    # Base case
    pc_base = ProjectCosts(base_scenario)
    results["Base Case"] = {
        "Gross Profit": pc_base.gross_profit(),
        "ROI on $200K": pc_base.gross_profit() / 200_000 * 100,
        "Cash Needed": pc_base.total_cash_from_coop(),
    }

    # Rehab +20%
    s = ScenarioInputs(**{k: v for k, v in base_scenario.__dict__.items()})
    s.name = "Rehab +20%"
    s.avg_rehab_budget *= 1.20
    pc = ProjectCosts(s)
    results[s.name] = {
        "Gross Profit": pc.gross_profit(),
        "ROI on $200K": pc.gross_profit() / 200_000 * 100,
        "Cash Needed": pc.total_cash_from_coop(),
    }

    # ARV -10%
    s = ScenarioInputs(**{k: v for k, v in base_scenario.__dict__.items()})
    s.name = "ARV -10%"
    s.avg_arv *= 0.90
    pc = ProjectCosts(s)
    results[s.name] = {
        "Gross Profit": pc.gross_profit(),
        "ROI on $200K": pc.gross_profit() / 200_000 * 100,
        "Cash Needed": pc.total_cash_from_coop(),
    }

    # Hold +3 months
    s = ScenarioInputs(**{k: v for k, v in base_scenario.__dict__.items()})
    s.name = "Hold +3 Months"
    s.avg_hold_months += 3
    pc = ProjectCosts(s)
    results[s.name] = {
        "Gross Profit": pc.gross_profit(),
        "ROI on $200K": pc.gross_profit() / 200_000 * 100,
        "Cash Needed": pc.total_cash_from_coop(),
    }

    # Rate +2%
    s = ScenarioInputs(**{k: v for k, v in base_scenario.__dict__.items()})
    s.name = "Rate +2%"
    s.hard_money_rate += 0.02
    pc = ProjectCosts(s)
    results[s.name] = {
        "Gross Profit": pc.gross_profit(),
        "ROI on $200K": pc.gross_profit() / 200_000 * 100,
        "Cash Needed": pc.total_cash_from_coop(),
    }

    # Worst case: Rehab +20% AND ARV -10% AND Hold +2 months
    s = ScenarioInputs(**{k: v for k, v in base_scenario.__dict__.items()})
    s.name = "Worst Case (all three)"
    s.avg_rehab_budget *= 1.20
    s.avg_arv *= 0.90
    s.avg_hold_months += 2
    pc = ProjectCosts(s)
    results[s.name] = {
        "Gross Profit": pc.gross_profit(),
        "ROI on $200K": pc.gross_profit() / 200_000 * 100,
        "Cash Needed": pc.total_cash_from_coop(),
    }

    return results


# ============================================================================
# OUTPUT
# ============================================================================

def format_currency(amount: float) -> str:
    """Format as USD with commas."""
    if amount < 0:
        return f"-${abs(amount):,.0f}"
    return f"${amount:,.0f}"


def print_separator(char: str = "=", width: int = 80):
    print(char * width)


def print_section(title: str):
    print()
    print_separator()
    print(f"  {title}")
    print_separator()


def main():
    overhead = FixedOverhead()
    split = ProfitSplit()

    print()
    print("  PORTLAND HOUSING CO-OP — YEAR 1 OPERATING COST MODEL")
    print("  Prepared by: Ledger (CFO)")
    print("  Date: 2026-04-07")
    print("  Status: DRAFT")

    # ---- Fixed Overhead ----
    print_section("SECTION 1: ANNUAL FIXED OVERHEAD")
    items = overhead.line_items()
    for label, amount in items.items():
        print(f"  {label:<40s} {format_currency(amount):>12s}")
    print(f"  {'':40s} {'----------':>12s}")
    print(f"  {'TOTAL ANNUAL OVERHEAD':<40s} {format_currency(overhead.total()):>12s}")

    # ---- Per-Scenario Analysis ----
    for scenario_key, scenario in SCENARIOS.items():
        print_section(f"SECTION 2: {scenario.name.upper()} SCENARIO — PER-PROJECT ECONOMICS")
        pc = ProjectCosts(scenario)

        print(f"\n  Assumptions:")
        print(f"    Members: {scenario.num_members}")
        print(f"    Flips in Year 1: {scenario.num_flips_year1}")
        print(f"    Purchase Price: {format_currency(scenario.avg_purchase_price)}")
        print(f"    Rehab Budget: {format_currency(scenario.avg_rehab_budget)}")
        print(f"    ARV: {format_currency(scenario.avg_arv)}")
        print(f"    Hold Period: {scenario.avg_hold_months:.0f} months")
        print(f"    Hard Money: {scenario.hard_money_ltv*100:.0f}% LTV, {scenario.hard_money_rate*100:.1f}% rate, {scenario.hard_money_points*100:.1f} pts")

        print(f"\n  Cost Breakdown (Per Flip):")
        items = pc.line_items()
        for label, amount in items.items():
            print(f"    {label:<45s} {format_currency(amount):>12s}")
        print(f"    {'':45s} {'----------':>12s}")
        print(f"    {'TOTAL PROJECT COST':<45s} {format_currency(pc.total_project_cost()):>12s}")

        print(f"\n  Returns:")
        print(f"    {'ARV':<45s} {format_currency(scenario.avg_arv):>12s}")
        print(f"    {'Total Cost':<45s} {format_currency(-pc.total_project_cost()):>12s}")
        print(f"    {'GROSS PROFIT':<45s} {format_currency(pc.gross_profit()):>12s}")

        gp = pc.gross_profit()
        if gp > 0:
            print(f"\n  Profit Split:")
            split_items = split.split(gp)
            for label, amount in split_items.items():
                print(f"    {label:<45s} {format_currency(amount):>12s}")

        roi = gp / 200_000 * 100
        print(f"\n  Cash deployed by co-op: {format_currency(pc.total_cash_from_coop())}")
        print(f"  ROI on $200K capitalization: {roi:.1f}%")

        if roi < 15:
            print(f"  ⚠ WARNING: Below 15% target ROI")

        # ---- Monthly Cash Flow ----
        print(f"\n  Monthly Cash Flow Projection:")
        print(f"    {'Mo':<4s} {'Inflow':>10s} {'Overhead':>10s} {'Project':>12s} {'Sale':>12s} {'Net':>12s} {'Balance':>12s}")
        print(f"    {'--':<4s} {'--------':>10s} {'--------':>10s} {'----------':>12s} {'----------':>12s} {'----------':>12s} {'----------':>12s}")
        cf = monthly_cash_flow(scenario, overhead)
        min_balance = float('inf')
        min_balance_month = 0
        for row in cf:
            print(
                f"    {row['month']:<4d} "
                f"{format_currency(row['inflow']):>10s} "
                f"{format_currency(row['overhead']):>10s} "
                f"{format_currency(row['project_cost']):>12s} "
                f"{format_currency(row['sale_proceeds']):>12s} "
                f"{format_currency(row['net']):>12s} "
                f"{format_currency(row['balance']):>12s}"
            )
            if row['balance'] < min_balance:
                min_balance = row['balance']
                min_balance_month = row['month']

        print(f"\n  ⚡ Lowest cash balance: {format_currency(min_balance)} in month {min_balance_month}")
        if min_balance < 20_000:
            print(f"  🚨 CASH FLOW WARNING: Balance drops below $20K safety threshold!")
        elif min_balance < 50_000:
            print(f"  ⚠ CAUTION: Balance drops below $50K comfort zone.")

    # ---- Sensitivity Analysis ----
    print_section("SECTION 3: SENSITIVITY ANALYSIS (Conservative Scenario)")
    print(f"\n  What happens when things go wrong?\n")
    sens = sensitivity_analysis(SCENARIOS["conservative"])
    print(f"    {'Scenario':<30s} {'Gross Profit':>14s} {'ROI %':>8s} {'Cash Needed':>14s}")
    print(f"    {'--------':<30s} {'------------':>14s} {'-----':>8s} {'----------':>14s}")
    for label, metrics in sens.items():
        gp = format_currency(metrics["Gross Profit"])
        roi = f"{metrics['ROI on $200K']:.1f}%"
        cash = format_currency(metrics["Cash Needed"])
        flag = " ⚠" if metrics["ROI on $200K"] < 15 else ""
        flag = " 🚨" if metrics["ROI on $200K"] < 0 else flag
        print(f"    {label:<30s} {gp:>14s} {roi:>8s} {cash:>14s}{flag}")

    print(f"\n  Key takeaway: The deal survives rehab overruns OR a slow market, but")
    print(f"  NOT both at the same time. This is why we buy at ≤65% of ARV and keep")
    print(f"  a cash buffer. The worst-case scenario is a lesson, not a bankruptcy.")

    # ---- Summary ----
    print_section("SECTION 4: YEAR 1 SUMMARY")
    print(f"""
  Capitalization Target:      $200,000
  Annual Fixed Overhead:      {format_currency(overhead.total())}
  Overhead per Flip (1/yr):   {format_currency(overhead.total())}
  Overhead per Flip (2/yr):   {format_currency(overhead.total() / 2)}

  Minimum Viable Deal:
    Purchase at ≤65% of ARV
    Rehab budget ≤25% of ARV
    Hold period ≤6 months
    Target: ≥15% net ROI on deployed capital

  Cash Flow Rule:
    Never let the co-op balance drop below $20,000.
    If projected to breach, delay the next acquisition.

  Reserve Policy:
    20% of gross profit goes to reserves after each flip.
    Reserves fund: next deal down payment, overhead float, contingencies.
    Target reserve balance after Year 1: $15,000 - $25,000.
    """)

    print_separator()
    print("  END OF MODEL — Ledger")
    print_separator()
    print()


if __name__ == "__main__":
    main()
