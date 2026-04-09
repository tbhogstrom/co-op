#!/usr/bin/env python3
"""
Portland Housing Co-op — 5-Year Monte Carlo Simulation
Author: Maven (Founder) + Ledger (CFO)
Date: 2026-04-09

Simulates 5 years of co-op operations with 7 members, realistic deal flow,
random events, and per-member profit tracking.

Usage:
    python simulate.py              # Run simulation with default seed
    python simulate.py --seed 42    # Reproducible run
    python simulate.py --quiet      # Summary only
"""

import random
import argparse
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum

# ============================================================================
# CO-OP FINANCIAL CONSTANTS (from M1-approved model)
# ============================================================================

RESERVE_PCT = 0.20
OVERHEAD_PCT = 0.10
CAPITAL_PCT = 0.30
LABOR_PCT = 0.40

TRADE_MULTIPLIERS = {
    "project_management": 1.15,
    "general_labor": 1.0,
    "painting": 1.0,
    "carpentry": 1.2,
    "framing": 1.2,
    "roofing": 1.2,
    "foundation": 1.2,   # concrete, hardscaping
    "plumbing": 1.3,
    "electrical": 1.3,
    "hvac": 1.3,
    "finish_work": 1.0,
    "admin": 1.0,
}


# ============================================================================
# MEMBER DEFINITIONS
# ============================================================================

@dataclass
class Member:
    name: str
    role: str
    trade: str               # primary trade for labor
    capital_contribution: float
    active: bool = True
    joined_quarter: int = 0  # Q0 = founding
    left_quarter: int = -1   # -1 = still active

    # Running totals
    total_labor_hours: float = 0.0
    total_weighted_hours: float = 0.0
    total_capital_earnings: float = 0.0
    total_labor_earnings: float = 0.0
    total_distributions: float = 0.0
    projects_worked: int = 0
    capital_account: float = 0.0  # current capital account (buy-in + retained)

    def __post_init__(self):
        self.capital_account = self.capital_contribution


def build_founding_members() -> List[Member]:
    return [
        Member("Harlan",   "General Contractor",        "project_management", 25_000),
        Member("Bristow",  "Painter",                   "painting",           25_000),
        Member("Quinn",    "Non-Trade Investor A",      "general_labor",      50_000),
        Member("Masonry",  "Foundation/Concrete/Hardsc", "foundation",         15_000),
        Member("Copper",   "Plumber",                   "plumbing",           12_000),
        Member("Volt",     "Electrician",               "electrical",         20_000),
        Member("Devlin",   "Non-Trade Investor B",      "general_labor",      60_000),
    ]


# ============================================================================
# DEAL / PROJECT MODEL
# ============================================================================

class DealOutcome(Enum):
    COMPLETED = "completed"
    OVER_BUDGET = "over_budget"
    LOSS = "loss"
    ABANDONED = "abandoned"


@dataclass
class Deal:
    name: str
    address: str
    neighborhood: str
    quarter: int              # Q when acquired (0-19)
    purchase_price: float
    rehab_budget: float
    projected_arv: float
    actual_rehab_cost: float = 0.0
    actual_sale_price: float = 0.0
    holding_months: int = 4
    outcome: DealOutcome = DealOutcome.COMPLETED
    event_notes: List[str] = field(default_factory=list)

    # Labor hours per member on this deal
    labor_hours: Dict[str, float] = field(default_factory=dict)

    @property
    def carry_cost(self) -> float:
        """Hard money interest + insurance + utilities + property tax."""
        monthly_rate = 0.12 / 12  # 12% annual hard money
        loan_amount = self.purchase_price * 0.85  # 85% LTV
        interest = loan_amount * monthly_rate * self.holding_months
        insurance = 150 * self.holding_months
        utilities = 200 * self.holding_months
        prop_tax = (self.purchase_price * 0.012) / 12 * self.holding_months
        return interest + insurance + utilities + prop_tax

    @property
    def acquisition_cost(self) -> float:
        """Closing costs on purchase."""
        return self.purchase_price * 0.02  # ~2% closing

    @property
    def selling_cost(self) -> float:
        """Agent commission + closing costs on sale."""
        return self.actual_sale_price * 0.07  # 6% commission + 1% closing

    @property
    def total_cost(self) -> float:
        return (self.purchase_price + self.actual_rehab_cost +
                self.carry_cost + self.acquisition_cost + self.selling_cost)

    @property
    def gross_profit(self) -> float:
        return self.actual_sale_price - self.total_cost


# ============================================================================
# PORTLAND MARKET MODEL
# ============================================================================

NEIGHBORHOODS = [
    # (name, median_price_2026, annual_appreciation, distress_probability)
    ("Lents",          320_000, 0.04, 0.15),
    ("Cully",          340_000, 0.05, 0.12),
    ("Parkrose",       290_000, 0.03, 0.18),
    ("Foster-Powell",  380_000, 0.05, 0.08),
    ("St. Johns",      360_000, 0.04, 0.10),
    ("Montavilla",     400_000, 0.04, 0.07),
    ("Woodstock",      420_000, 0.05, 0.06),
    ("Kenton",         370_000, 0.04, 0.09),
    ("Portsmouth",     310_000, 0.03, 0.14),
    ("Brentwood-Darlington", 280_000, 0.03, 0.16),
]

PORTLAND_STREETS = [
    "SE Foster Rd", "NE Killingsworth St", "N Lombard St", "SE Division St",
    "NE Alberta St", "SE Woodstock Blvd", "N Interstate Ave", "SE Powell Blvd",
    "NE Sandy Blvd", "SE Holgate Blvd", "N Williams Ave", "SE 82nd Ave",
    "NE Prescott St", "SE Steele St", "N Fessenden St", "NE Fremont St",
    "SE Duke St", "N Willamette Blvd", "NE Dekum St", "SE Flavel St",
]


def generate_address(rng: random.Random) -> str:
    num = rng.randint(100, 12999)
    street = rng.choice(PORTLAND_STREETS)
    return f"{num} {street}"


# ============================================================================
# RANDOM EVENTS ENGINE
# ============================================================================

@dataclass
class Event:
    name: str
    description: str
    quarter: int
    severity: str  # "minor", "moderate", "major"

    # Effects
    cost_multiplier: float = 1.0     # multiplied into rehab cost
    time_add_months: int = 0         # added to holding period
    arv_multiplier: float = 1.0      # multiplied into sale price
    member_affected: str = ""        # member name if applicable
    member_leaves: bool = False
    market_shift: float = 0.0        # permanent market shift (applied to all future deals)
    deal_killed: bool = False


def generate_events(rng: random.Random, quarter: int, members: List[Member],
                    deal: Optional[Deal] = None) -> List[Event]:
    """Generate random events for a quarter. ~30% chance of something happening per deal."""
    events = []

    # Per-deal events (only if there's an active deal)
    if deal:
        roll = rng.random()

        if roll < 0.03:
            # 3% — Foundation issues discovered
            events.append(Event(
                "Foundation Surprise",
                f"Structural cracks found during demo at {deal.address}. "
                f"Engineer report required. Additional $18K-$25K in foundation work.",
                quarter, "major",
                cost_multiplier=1.0,  # we add a fixed cost instead
                time_add_months=2,
            ))
            deal.actual_rehab_cost += rng.randint(18_000, 25_000)

        elif roll < 0.08:
            # 5% — Permit delays
            months = rng.randint(1, 3)
            events.append(Event(
                "Permit Delays",
                f"BDS permit review backlog delays {deal.address} by {months} month(s). "
                f"Inspector availability limited.",
                quarter, "moderate",
                time_add_months=months,
            ))

        elif roll < 0.13:
            # 5% — Material cost spike
            pct = rng.uniform(0.12, 0.25)
            events.append(Event(
                "Material Cost Spike",
                f"Lumber/materials price spike hits {deal.address}. "
                f"Rehab budget increases {pct*100:.0f}%.",
                quarter, "moderate",
                cost_multiplier=1.0 + pct,
            ))

        elif roll < 0.17:
            # 4% — Weather delays (PNW rain)
            months = rng.choice([1, 1, 2])
            events.append(Event(
                "Weather Delays",
                f"Extended rain/ice storm delays exterior work at {deal.address} "
                f"by {months} month(s).",
                quarter, "minor",
                time_add_months=months,
            ))

        elif roll < 0.20:
            # 3% — Asbestos/lead paint
            cost = rng.randint(5_000, 15_000)
            events.append(Event(
                "Hazmat Abatement",
                f"Asbestos/lead paint discovered at {deal.address}. "
                f"Licensed abatement required: ${cost:,}.",
                quarter, "moderate",
                time_add_months=1,
            ))
            deal.actual_rehab_cost += cost

        elif roll < 0.23:
            # 3% — Sewer line replacement
            cost = rng.randint(8_000, 18_000)
            events.append(Event(
                "Sewer Line Failure",
                f"Camera inspection reveals collapsed sewer lateral at {deal.address}. "
                f"Full replacement: ${cost:,}.",
                quarter, "moderate",
            ))
            deal.actual_rehab_cost += cost

        elif roll < 0.26:
            # 3% — Subcontractor no-show / quality issues
            cost = rng.randint(3_000, 8_000)
            events.append(Event(
                "Sub Quality Issues",
                f"Subcontractor work at {deal.address} fails inspection. "
                f"Rework cost: ${cost:,}.",
                quarter, "minor",
                time_add_months=1,
            ))
            deal.actual_rehab_cost += cost

        elif roll < 0.29:
            # 3% — Neighbor dispute / HOA issue
            events.append(Event(
                "Neighbor Complaint",
                f"Neighbor files noise/dust complaint at {deal.address}. "
                f"Work hours restricted for 2 weeks.",
                quarter, "minor",
                time_add_months=1,
            ))

        elif roll < 0.32:
            # 3% — Great deal: under-ARV comp pushes price up
            bump = rng.uniform(0.03, 0.08)
            events.append(Event(
                "Hot Market Pocket",
                f"Multiple offers on {deal.address} area comps. "
                f"ARV revised up {bump*100:.1f}%.",
                quarter, "minor",
                arv_multiplier=1.0 + bump,
            ))

        elif roll < 0.34:
            # 2% — Theft/vandalism
            cost = rng.randint(2_000, 10_000)
            events.append(Event(
                "Job Site Theft",
                f"Tools and materials stolen from {deal.address}. "
                f"Loss: ${cost:,}.",
                quarter, "moderate",
            ))
            deal.actual_rehab_cost += cost

        elif roll < 0.36:
            # 2% — Electrical panel needs full replacement
            cost = rng.randint(6_000, 12_000)
            events.append(Event(
                "Panel Upgrade Required",
                f"100A panel at {deal.address} must be upgraded to 200A per code. "
                f"Cost: ${cost:,}.",
                quarter, "moderate",
            ))
            deal.actual_rehab_cost += cost

    # Market-wide events (checked once per quarter, ~5% chance)
    market_roll = rng.random()
    if market_roll < 0.02:
        shift = rng.uniform(-0.08, -0.04)
        events.append(Event(
            "Market Correction",
            f"Portland housing market corrects {abs(shift)*100:.1f}%. "
            f"Interest rate hike dampens buyer demand.",
            quarter, "major",
            market_shift=shift,
        ))
    elif market_roll < 0.035:
        shift = rng.uniform(0.04, 0.08)
        events.append(Event(
            "Market Surge",
            f"Tech hiring boom pushes Portland prices up {shift*100:.1f}%. "
            f"Buyer demand exceeds inventory.",
            quarter, "moderate",
            market_shift=shift,
        ))
    elif market_roll < 0.045:
        shift = rng.uniform(-0.12, -0.08)
        events.append(Event(
            "Recession Impact",
            f"Economic recession hits Portland. Home values drop {abs(shift)*100:.1f}%. "
            f"Hard money rates increase to 14%.",
            quarter, "major",
            market_shift=shift,
        ))

    # Member events (~4% chance per quarter)
    member_roll = rng.random()
    active_members = [m for m in members if m.active]
    if active_members:
        if member_roll < 0.015:
            affected = rng.choice(active_members)
            events.append(Event(
                "Member Injury",
                f"{affected.name} suffers a job-site injury. Out for 1 quarter. "
                f"Workers comp claim filed.",
                quarter, "moderate",
                member_affected=affected.name,
            ))
        elif member_roll < 0.025:
            # Member departure (not the GC or heavy investors)
            eligible = [m for m in active_members
                       if m.capital_contribution <= 25_000 and m.role != "General Contractor"]
            if eligible:
                leaving = rng.choice(eligible)
                events.append(Event(
                    "Member Departure",
                    f"{leaving.name} leaves the co-op. Personal reasons. "
                    f"Capital account of ${leaving.capital_account:,.0f} to be returned within 120 days.",
                    quarter, "major",
                    member_affected=leaving.name,
                    member_leaves=True,
                ))
        elif member_roll < 0.035:
            affected = rng.choice(active_members)
            events.append(Event(
                "Member Dispute",
                f"Disagreement between {affected.name} and another member over project priorities. "
                f"Resolved at board meeting. Minor productivity loss.",
                quarter, "minor",
                time_add_months=0,
            ))

    return events


# ============================================================================
# DEAL GENERATION
# ============================================================================

def generate_deal(rng: random.Random, quarter: int, deal_num: int,
                  market_adjustment: float) -> Deal:
    """Generate a realistic Portland flip deal."""
    hood_name, median, appreciation, _ = rng.choice(NEIGHBORHOODS)

    # Apply market-wide adjustments and time-based appreciation
    years_in = quarter / 4
    time_adjusted_median = median * (1 + appreciation) ** years_in * (1 + market_adjustment)

    # Distressed properties are 55-75% of median
    discount = rng.uniform(0.55, 0.75)
    purchase_price = round(time_adjusted_median * discount / 1000) * 1000

    # Rehab budget: 15-30% of purchase price for cosmetic-plus
    rehab_pct = rng.uniform(0.15, 0.30)
    rehab_budget = round(purchase_price * rehab_pct / 500) * 500

    # ARV: time-adjusted median + some variance
    arv_variance = rng.uniform(-0.05, 0.10)
    projected_arv = round(time_adjusted_median * (1 + arv_variance) / 1000) * 1000

    address = generate_address(rng)

    return Deal(
        name=f"Deal #{deal_num}",
        address=address,
        neighborhood=hood_name,
        quarter=quarter,
        purchase_price=purchase_price,
        rehab_budget=rehab_budget,
        projected_arv=projected_arv,
    )


# ============================================================================
# LABOR HOUR ALLOCATION
# ============================================================================

def allocate_labor(deal: Deal, members: List[Member], rng: random.Random) -> Dict[str, float]:
    """
    Allocate labor hours to active members based on their trade and the deal's scope.
    Returns {member_name: hours}.
    """
    active = [m for m in members if m.active]
    hours = {}

    # Base hours scale with rehab budget (~1 hour per $100-$150 of rehab)
    total_labor_hours = deal.actual_rehab_cost / rng.uniform(100, 150)

    for m in active:
        if m.trade == "project_management":
            # GC does PM + some hands-on
            h = total_labor_hours * rng.uniform(0.12, 0.18)
        elif m.trade in ("plumbing", "electrical"):
            # Specialists: focused bursts
            h = total_labor_hours * rng.uniform(0.08, 0.14)
        elif m.trade == "foundation":
            # Foundation/concrete: depends on deal (some deals need a lot, some minimal)
            if rng.random() < 0.4:  # 40% of deals have significant foundation work
                h = total_labor_hours * rng.uniform(0.10, 0.18)
            else:
                h = total_labor_hours * rng.uniform(0.03, 0.06)
        elif m.trade == "painting":
            # Painter: consistent across deals
            h = total_labor_hours * rng.uniform(0.10, 0.16)
        elif m.trade == "general_labor":
            # Non-trade members: demo, cleanup, hauling, light assist
            if m.capital_contribution >= 50_000:
                # Higher investor, less time on site
                h = total_labor_hours * rng.uniform(0.02, 0.06)
            else:
                h = total_labor_hours * rng.uniform(0.04, 0.08)
        else:
            h = total_labor_hours * rng.uniform(0.05, 0.10)

        hours[m.name] = round(h, 1)

    return hours


# ============================================================================
# SIMULATION ENGINE
# ============================================================================

@dataclass
class QuarterReport:
    quarter: int
    year: int
    q_in_year: int
    deals_completed: List[Deal]
    deals_in_progress: List[Deal]
    events: List[Event]
    member_earnings_this_q: Dict[str, Dict[str, float]]  # {name: {capital: x, labor: y}}
    coop_reserves: float
    coop_overhead_fund: float
    coop_total_value: float
    member_snapshots: Dict[str, Dict]  # {name: {capital_account, total_earnings, etc.}}


def run_simulation(seed: int = 2026, quiet: bool = False) -> List[QuarterReport]:
    rng = random.Random(seed)
    members = build_founding_members()

    # State tracking
    total_reserves = 0.0
    total_overhead = 0.0
    market_adjustment = 0.0  # cumulative market shift
    deals_completed: List[Deal] = []
    deals_in_progress: List[Deal] = []
    all_events: List[Event] = []
    quarter_reports: List[QuarterReport] = []
    deal_counter = 0
    injured_members: Dict[str, int] = {}  # {name: quarter_when_returns}

    # Replacement member pool (if someone leaves)
    replacement_pool = [
        ("Forge",   "HVAC Technician",     "hvac",         18_000),
        ("Reed",    "Finish Carpenter",    "carpentry",    15_000),
        ("Clay",    "Concrete/Mason",      "foundation",   12_000),
        ("Niles",   "Non-Trade Investor",  "general_labor", 35_000),
    ]

    total_capital = sum(m.capital_contribution for m in members)

    if not quiet:
        print("=" * 100)
        print("  PORTLAND HOUSING CO-OP — 5-YEAR SIMULATION")
        print("=" * 100)
        print(f"\n  Founding Members ({len(members)}):")
        print(f"  {'Name':<12s} {'Role':<30s} {'Trade':<22s} {'Capital':>10s}")
        print(f"  {'─'*12} {'─'*30} {'─'*22} {'─'*10}")
        for m in members:
            print(f"  {m.name:<12s} {m.role:<30s} {m.trade:<22s} ${m.capital_contribution:>9,.0f}")
        print(f"  {'─'*12} {'─'*30} {'─'*22} {'─'*10}")
        print(f"  {'TOTAL':<12s} {'':30s} {'':22s} ${total_capital:>9,.0f}")
        print()

    # ── Main Loop: 20 Quarters (5 Years) ──

    for q in range(20):
        year = q // 4 + 1
        q_in_year = q % 4 + 1
        quarter_events = []
        q_member_earnings: Dict[str, Dict[str, float]] = {m.name: {"capital": 0, "labor": 0} for m in members}

        # Check if injured members return
        for name, return_q in list(injured_members.items()):
            if q >= return_q:
                for m in members:
                    if m.name == name:
                        m.active = True
                del injured_members[name]
                quarter_events.append(Event(
                    "Member Returns",
                    f"{name} returns to work after injury recovery.",
                    q, "minor",
                ))

        if not quiet:
            print(f"\n{'━'*100}")
            print(f"  YEAR {year} — Q{q_in_year}  (Quarter {q+1} of 20)")
            print(f"{'━'*100}")

        # ── Generate new deals ──
        # Ramp up: Y1=1-2 deals/yr, Y2=2-3, Y3-5=3-4
        if year == 1:
            deals_per_q = 0.4  # ~1.6/year
        elif year == 2:
            deals_per_q = 0.6  # ~2.4/year
        elif year <= 4:
            deals_per_q = 0.8  # ~3.2/year
        else:
            deals_per_q = 1.0  # ~4/year

        # Check if co-op has enough capital for a new deal
        available_cash = total_capital + total_reserves * 0.5  # can deploy half reserves
        min_deal_cash = 30_000  # minimum down payment + initial rehab

        if rng.random() < deals_per_q and available_cash > min_deal_cash:
            deal_counter += 1
            new_deal = generate_deal(rng, q, deal_counter, market_adjustment)

            # Determine holding period
            new_deal.holding_months = rng.randint(3, 6)

            # Initial rehab cost estimate (will be modified by events)
            new_deal.actual_rehab_cost = new_deal.rehab_budget * rng.uniform(0.90, 1.15)

            deals_in_progress.append(new_deal)

            if not quiet:
                print(f"\n  NEW DEAL ACQUIRED: {new_deal.name}")
                print(f"    Address:        {new_deal.address}")
                print(f"    Neighborhood:   {new_deal.neighborhood}")
                print(f"    Purchase:       ${new_deal.purchase_price:,.0f}")
                print(f"    Rehab Budget:   ${new_deal.rehab_budget:,.0f}")
                print(f"    Projected ARV:  ${new_deal.projected_arv:,.0f}")
                print(f"    Est. Hold:      {new_deal.holding_months} months")

        # ── Process events for in-progress deals ──
        for deal in deals_in_progress:
            events = generate_events(rng, q, members, deal)
            for e in events:
                quarter_events.append(e)

                # Apply event effects
                if e.cost_multiplier != 1.0:
                    deal.actual_rehab_cost *= e.cost_multiplier
                if e.time_add_months > 0:
                    deal.holding_months += e.time_add_months
                if e.arv_multiplier != 1.0:
                    deal.projected_arv *= e.arv_multiplier

        # Market-wide events (separate from deal events)
        market_events = generate_events(rng, q, members, None)
        for e in market_events:
            if e.market_shift != 0:
                market_adjustment += e.market_shift
                quarter_events.append(e)
            elif e.member_affected:
                quarter_events.append(e)
                if e.member_leaves:
                    for m in members:
                        if m.name == e.member_affected:
                            m.active = False
                            m.left_quarter = q
                            # Return capital over time (reduce co-op capital)
                            total_capital -= m.capital_account
                            # Try to recruit replacement
                            if replacement_pool:
                                rep = replacement_pool.pop(0)
                                new_member = Member(rep[0], rep[1], rep[2], rep[3],
                                                   joined_quarter=q+1)
                                members.append(new_member)
                                total_capital += new_member.capital_contribution
                                q_member_earnings[new_member.name] = {"capital": 0, "labor": 0}
                                quarter_events.append(Event(
                                    "New Member Recruited",
                                    f"{new_member.name} ({new_member.role}) joins the co-op "
                                    f"with ${new_member.capital_contribution:,.0f} buy-in.",
                                    q+1, "minor",
                                ))
                elif "Injury" in e.name:
                    for m in members:
                        if m.name == e.member_affected:
                            m.active = False
                            injured_members[m.name] = q + 1  # out for 1 quarter
            else:
                quarter_events.append(e)

        all_events.extend(quarter_events)

        # ── Complete deals that have finished their holding period ──
        still_in_progress = []
        for deal in deals_in_progress:
            quarters_held = q - deal.quarter
            months_elapsed = quarters_held * 3

            if months_elapsed >= deal.holding_months:
                # Deal completes — determine actual sale price
                base_arv = deal.projected_arv * (1 + market_adjustment * 0.3)  # partial market effect
                sale_variance = rng.uniform(-0.05, 0.05)
                deal.actual_sale_price = round(base_arv * (1 + sale_variance) / 1000) * 1000

                # Allocate labor hours
                deal.labor_hours = allocate_labor(deal, members, rng)

                # Determine outcome
                if deal.gross_profit < -10_000:
                    deal.outcome = DealOutcome.LOSS
                elif deal.actual_rehab_cost > deal.rehab_budget * 1.25:
                    deal.outcome = DealOutcome.OVER_BUDGET
                else:
                    deal.outcome = DealOutcome.COMPLETED

                # ── PROFIT SPLIT ──
                gp = deal.gross_profit
                is_loss = gp <= 0

                if not quiet:
                    print(f"\n  DEAL COMPLETED: {deal.name} — {deal.address}")
                    print(f"    Neighborhood:   {deal.neighborhood}")
                    print(f"    Purchase:       ${deal.purchase_price:,.0f}")
                    print(f"    Rehab (actual): ${deal.actual_rehab_cost:,.0f}  (budget was ${deal.rehab_budget:,.0f})")
                    print(f"    Carry Cost:     ${deal.carry_cost:,.0f}")
                    print(f"    Acq. Cost:      ${deal.acquisition_cost:,.0f}")
                    print(f"    Sale Price:     ${deal.actual_sale_price:,.0f}")
                    print(f"    Selling Cost:   ${deal.selling_cost:,.0f}")
                    print(f"    TOTAL COST:     ${deal.total_cost:,.0f}")
                    if is_loss:
                        print(f"    GROSS PROFIT:   -${abs(gp):,.0f}  *** LOSS ***")
                    else:
                        roi = gp / (deal.purchase_price + deal.actual_rehab_cost) * 100
                        print(f"    GROSS PROFIT:   ${gp:,.0f}  ({roi:.1f}% ROI)")
                    print(f"    Outcome:        {deal.outcome.value}")
                    if deal.event_notes:
                        for note in deal.event_notes:
                            print(f"    Event:          {note}")
                    print(f"    Hold Period:    {deal.holding_months} months")

                if is_loss:
                    # Loss allocated to capital accounts proportionally
                    active_capital = sum(m.capital_account for m in members if m.active)
                    for m in members:
                        if m.active and active_capital > 0:
                            loss_share = gp * (m.capital_account / active_capital)
                            m.capital_account += loss_share  # negative
                            q_member_earnings[m.name]["capital"] += loss_share
                else:
                    to_reserves = gp * RESERVE_PCT
                    to_overhead = gp * OVERHEAD_PCT
                    capital_pool = gp * CAPITAL_PCT
                    labor_pool = gp * LABOR_PCT

                    total_reserves += to_reserves
                    total_overhead += to_overhead

                    # Capital distribution (pro-rata)
                    active_capital = sum(m.capital_account for m in members if m.active)
                    for m in members:
                        if m.active and active_capital > 0:
                            cap_pct = m.capital_account / active_capital
                            cap_share = capital_pool * cap_pct
                            m.total_capital_earnings += cap_share
                            m.capital_account += cap_share  # retained earnings grow account
                            q_member_earnings[m.name]["capital"] += cap_share

                    # Labor distribution (pro-rata weighted hours)
                    total_weighted = 0
                    member_weighted: Dict[str, float] = {}
                    for m in members:
                        if m.active and m.name in deal.labor_hours:
                            hrs = deal.labor_hours[m.name]
                            mult = TRADE_MULTIPLIERS.get(m.trade, 1.0)
                            wh = hrs * mult
                            member_weighted[m.name] = wh
                            total_weighted += wh
                            m.total_labor_hours += hrs
                            m.total_weighted_hours += wh
                            m.projects_worked += 1

                    if total_weighted > 0:
                        for m in members:
                            if m.name in member_weighted:
                                lab_pct = member_weighted[m.name] / total_weighted
                                lab_share = labor_pool * lab_pct
                                m.total_labor_earnings += lab_share
                                m.total_distributions += lab_share
                                q_member_earnings[m.name]["labor"] += lab_share

                    # Show labor allocation
                    if not quiet:
                        print(f"\n    Labor Allocation:")
                        print(f"    {'Member':<12s} {'Trade':<22s} {'Hours':>8s} {'Mult':>6s} {'Weighted':>10s} {'Lab Share':>10s}")
                        print(f"    {'─'*12} {'─'*22} {'─'*8} {'─'*6} {'─'*10} {'─'*10}")
                        for m in members:
                            if m.name in deal.labor_hours:
                                hrs = deal.labor_hours[m.name]
                                mult = TRADE_MULTIPLIERS.get(m.trade, 1.0)
                                wh = hrs * mult
                                lab_pct = wh / total_weighted if total_weighted > 0 else 0
                                lab_share = labor_pool * lab_pct if not is_loss else 0
                                print(f"    {m.name:<12s} {m.trade:<22s} {hrs:>8.1f} {mult:>5.2f}x {wh:>10.1f} ${lab_share:>9,.0f}")

                        print(f"\n    Profit Split:")
                        print(f"      Reserves (20%):  ${to_reserves:,.0f}")
                        print(f"      Overhead (10%):  ${to_overhead:,.0f}")
                        print(f"      Capital  (30%):  ${capital_pool:,.0f}")
                        print(f"      Labor    (40%):  ${labor_pool:,.0f}")

                deals_completed.append(deal)
            else:
                still_in_progress.append(deal)

        deals_in_progress = still_in_progress

        # ── Print events ──
        if quarter_events and not quiet:
            print(f"\n  EVENTS THIS QUARTER:")
            for e in quarter_events:
                severity_icon = {"minor": ".", "moderate": "!", "major": "!!!"}
                icon = severity_icon.get(e.severity, "")
                print(f"    [{e.severity.upper():>8s}] {icon} {e.name}: {e.description}")

        # ── Calculate co-op total value ──
        total_member_capital = sum(m.capital_account for m in members if m.active)
        # Value of deals in progress (conservative: purchase price + rehab spent so far)
        wip_value = sum(d.purchase_price * 0.85 + d.actual_rehab_cost * 0.5
                       for d in deals_in_progress)  # conservative WIP valuation
        coop_value = total_member_capital + total_reserves + total_overhead + wip_value

        # Build member snapshots
        member_snaps = {}
        for m in members:
            total_earnings = m.total_capital_earnings + m.total_labor_earnings
            member_snaps[m.name] = {
                "active": m.active,
                "capital_account": m.capital_account,
                "total_capital_earnings": m.total_capital_earnings,
                "total_labor_earnings": m.total_labor_earnings,
                "total_earnings": total_earnings,
                "total_labor_hours": m.total_labor_hours,
                "projects_worked": m.projects_worked,
                "roi_on_buyin": (total_earnings / m.capital_contribution * 100
                                if m.capital_contribution > 0 else 0),
            }

        quarter_reports.append(QuarterReport(
            quarter=q,
            year=year,
            q_in_year=q_in_year,
            deals_completed=[d for d in deals_completed if d.quarter <= q],
            deals_in_progress=list(deals_in_progress),
            events=quarter_events,
            member_earnings_this_q=q_member_earnings,
            coop_reserves=total_reserves,
            coop_overhead_fund=total_overhead,
            coop_total_value=coop_value,
            member_snapshots=member_snaps,
        ))

        # ── End-of-year summary ──
        if q_in_year == 4 and not quiet:
            print(f"\n{'─'*100}")
            print(f"  END OF YEAR {year} SUMMARY")
            print(f"{'─'*100}")
            year_deals = [d for d in deals_completed if d.quarter // 4 + 1 == year]
            year_profit = sum(d.gross_profit for d in year_deals)
            print(f"  Deals Completed This Year:  {len(year_deals)}")
            print(f"  Total Gross Profit:         ${year_profit:,.0f}")
            print(f"  Co-op Reserves:             ${total_reserves:,.0f}")
            print(f"  Co-op Overhead Fund:        ${total_overhead:,.0f}")
            print(f"  Market Adjustment:          {market_adjustment*100:+.1f}%")

            print(f"\n  Member Standings:")
            print(f"  {'Name':<12s} {'Status':<8s} {'Cap Acct':>12s} {'Cap Earn':>10s} {'Lab Earn':>10s} {'Total':>10s} {'Hours':>8s} {'Proj':>5s} {'ROI':>8s}")
            print(f"  {'─'*12} {'─'*8} {'─'*12} {'─'*10} {'─'*10} {'─'*10} {'─'*8} {'─'*5} {'─'*8}")
            for m in members:
                status = "ACTIVE" if m.active else "LEFT"
                total_e = m.total_capital_earnings + m.total_labor_earnings
                roi = total_e / m.capital_contribution * 100 if m.capital_contribution > 0 else 0
                print(
                    f"  {m.name:<12s} {status:<8s} "
                    f"${m.capital_account:>11,.0f} "
                    f"${m.total_capital_earnings:>9,.0f} "
                    f"${m.total_labor_earnings:>9,.0f} "
                    f"${total_e:>9,.0f} "
                    f"{m.total_labor_hours:>7.0f}h "
                    f"{m.projects_worked:>5d} "
                    f"{roi:>7.1f}%"
                )

            print(f"\n  CO-OP TOTAL VALUE:  ${coop_value:,.0f}")
            print(f"  (Member capital: ${total_member_capital:,.0f} + Reserves: ${total_reserves:,.0f} + Overhead: ${total_overhead:,.0f} + WIP: ${wip_value:,.0f})")

    # ══════════════════════════════════════════════════════════════════════
    # FINAL 5-YEAR SUMMARY
    # ══════════════════════════════════════════════════════════════════════

    print(f"\n\n{'═'*100}")
    print(f"  5-YEAR SIMULATION COMPLETE")
    print(f"{'═'*100}")

    total_deals = len(deals_completed)
    total_profit = sum(d.gross_profit for d in deals_completed)
    total_revenue = sum(d.actual_sale_price for d in deals_completed)
    total_invested = sum(d.purchase_price + d.actual_rehab_cost for d in deals_completed)
    profitable = sum(1 for d in deals_completed if d.gross_profit > 0)
    losses = sum(1 for d in deals_completed if d.gross_profit <= 0)

    print(f"\n  DEAL SUMMARY:")
    print(f"    Total Deals Completed:    {total_deals}")
    print(f"    Profitable:               {profitable}")
    print(f"    Losses:                   {losses}")
    print(f"    Total Revenue (sales):    ${total_revenue:,.0f}")
    print(f"    Total Invested:           ${total_invested:,.0f}")
    print(f"    Total Gross Profit:       ${total_profit:,.0f}")
    print(f"    Avg Profit/Deal:          ${total_profit/total_deals:,.0f}" if total_deals > 0 else "")
    print(f"    Avg ROI/Deal:             {total_profit/total_invested*100:.1f}%" if total_invested > 0 else "")

    print(f"\n  CO-OP FINANCIALS:")
    total_member_capital = sum(m.capital_account for m in members if m.active)
    final_value = total_member_capital + total_reserves + total_overhead
    print(f"    Total Reserves:           ${total_reserves:,.0f}")
    print(f"    Total Overhead Fund:      ${total_overhead:,.0f}")
    print(f"    Total Member Capital:     ${total_member_capital:,.0f}")
    print(f"    CO-OP TOTAL VALUE:        ${final_value:,.0f}")
    original_capital = sum(m.capital_contribution for m in members)
    print(f"    Original Capital Raised:  ${original_capital:,.0f}")
    print(f"    Total Value Growth:       ${final_value - original_capital:,.0f} ({(final_value/original_capital - 1)*100:.1f}%)")

    print(f"\n  EVENTS SUMMARY:")
    print(f"    Total Events:             {len(all_events)}")
    by_severity = {}
    for e in all_events:
        by_severity[e.severity] = by_severity.get(e.severity, 0) + 1
    for sev, count in sorted(by_severity.items()):
        print(f"      {sev.capitalize():<12s}  {count}")

    print(f"\n  FINAL MEMBER STANDINGS:")
    print(f"  {'Name':<12s} {'Status':<8s} {'Buy-In':>10s} {'Cap Acct':>12s} {'Cap Earn':>10s} {'Lab Earn':>10s} {'TOTAL':>10s} {'Hours':>8s} {'Proj':>5s} {'ROI':>8s} {'$/hr':>8s}")
    print(f"  {'═'*12} {'═'*8} {'═'*10} {'═'*12} {'═'*10} {'═'*10} {'═'*10} {'═'*8} {'═'*5} {'═'*8} {'═'*8}")

    for m in sorted(members, key=lambda x: x.total_capital_earnings + x.total_labor_earnings, reverse=True):
        status = "ACTIVE" if m.active else "LEFT Q" + str(m.left_quarter + 1)
        total_e = m.total_capital_earnings + m.total_labor_earnings
        roi = total_e / m.capital_contribution * 100 if m.capital_contribution > 0 else 0
        per_hour = total_e / m.total_labor_hours if m.total_labor_hours > 0 else 0
        print(
            f"  {m.name:<12s} {status:<8s} "
            f"${m.capital_contribution:>9,.0f} "
            f"${m.capital_account:>11,.0f} "
            f"${m.total_capital_earnings:>9,.0f} "
            f"${m.total_labor_earnings:>9,.0f} "
            f"${total_e:>9,.0f} "
            f"{m.total_labor_hours:>7.0f}h "
            f"{m.projects_worked:>5d} "
            f"{roi:>7.1f}% "
            f"${per_hour:>7,.0f}"
        )

    total_all_earnings = sum(m.total_capital_earnings + m.total_labor_earnings for m in members)
    total_all_hours = sum(m.total_labor_hours for m in members)
    print(f"  {'═'*12} {'═'*8} {'═'*10} {'═'*12} {'═'*10} {'═'*10} {'═'*10} {'═'*8} {'═'*5} {'═'*8} {'═'*8}")
    print(f"  {'TOTALS':<12s} {'':8s} ${sum(m.capital_contribution for m in members):>9,.0f} ${sum(m.capital_account for m in members if m.active):>11,.0f} ${sum(m.total_capital_earnings for m in members):>9,.0f} ${sum(m.total_labor_earnings for m in members):>9,.0f} ${total_all_earnings:>9,.0f} {total_all_hours:>7.0f}h {sum(m.projects_worked for m in members):>5d}")

    # ── Deal-by-deal ledger ──
    print(f"\n  DEAL LEDGER:")
    print(f"  {'#':<8s} {'Neighborhood':<20s} {'Purchase':>10s} {'Rehab':>10s} {'Sale':>10s} {'GP':>10s} {'ROI':>7s} {'Hold':>5s} {'Outcome':<12s}")
    print(f"  {'─'*8} {'─'*20} {'─'*10} {'─'*10} {'─'*10} {'─'*10} {'─'*7} {'─'*5} {'─'*12}")
    for d in deals_completed:
        invested = d.purchase_price + d.actual_rehab_cost
        roi = d.gross_profit / invested * 100 if invested > 0 else 0
        gp_str = f"${d.gross_profit:>9,.0f}" if d.gross_profit >= 0 else f"-${abs(d.gross_profit):>8,.0f}"
        print(
            f"  {d.name:<8s} {d.neighborhood:<20s} "
            f"${d.purchase_price:>9,.0f} "
            f"${d.actual_rehab_cost:>9,.0f} "
            f"${d.actual_sale_price:>9,.0f} "
            f"{gp_str} "
            f"{roi:>6.1f}% "
            f"{d.holding_months:>4d}m "
            f"{d.outcome.value:<12s}"
        )

    # ── Co-op value over time ──
    print(f"\n  CO-OP VALUE OVER TIME:")
    print(f"  {'Quarter':<10s} {'Value':>12s} {'Reserves':>12s} {'Overhead':>10s} {'Deals Done':>10s}")
    print(f"  {'─'*10} {'─'*12} {'─'*12} {'─'*10} {'─'*10}")
    for i, qr in enumerate(quarter_reports):
        if (i + 1) % 2 == 0 or i == 0 or i == len(quarter_reports) - 1:  # every 2 quarters
            deals_done = len([d for d in deals_completed if d.quarter <= qr.quarter])
            print(
                f"  Y{qr.year}Q{qr.q_in_year:<6d} "
                f"${qr.coop_total_value:>11,.0f} "
                f"${qr.coop_reserves:>11,.0f} "
                f"${qr.coop_overhead_fund:>9,.0f} "
                f"{deals_done:>10d}"
            )

    print(f"\n{'═'*100}")
    print(f"  Simulation seed: {seed}")
    print(f"{'═'*100}\n")

    return quarter_reports


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Portland Housing Co-op — 5-Year Simulation")
    parser.add_argument("--seed", type=int, default=2026, help="Random seed for reproducibility")
    parser.add_argument("--quiet", action="store_true", help="Summary only (skip quarter-by-quarter)")
    args = parser.parse_args()

    run_simulation(seed=args.seed, quiet=args.quiet)
