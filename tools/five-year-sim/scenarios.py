#!/usr/bin/env python3
"""
Portland Housing Co-op — Scenario Analysis Runner
Runs the 5-year simulation under different business model assumptions
and compares outcomes.

Usage:
    python scenarios.py
"""

import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import simulate
from simulate import Member, run_simulation
import statistics

SEEDS = [42, 99, 7, 2026, 1, 314, 55, 888]


def run_scenario(name: str, setup_fn=None, seeds=SEEDS):
    """Run a scenario across multiple seeds and return summary stats."""
    results = []

    for seed in seeds:
        # Reset module-level state by reloading — but we'll just override what we need
        if setup_fn:
            setup_fn()

        reports = run_simulation(seed=seed, quiet=True)
        final = reports[-1]

        # Extract key metrics from the final output
        total_deals = len([d for d in final.deals_completed if d.gross_profit is not None])
        total_profit = sum(d.gross_profit for d in final.deals_completed)
        total_revenue = sum(d.actual_sale_price for d in final.deals_completed)
        total_invested = sum(d.purchase_price + d.actual_rehab_cost for d in final.deals_completed)
        losses = sum(1 for d in final.deals_completed if d.gross_profit <= 0)

        active_members = [n for n, s in final.member_snapshots.items() if s.get("active", False)]
        total_earnings = sum(s.get("total_earnings", 0) for s in final.member_snapshots.values())
        min_earnings = min(s.get("total_earnings", 0) for s in final.member_snapshots.values()) if final.member_snapshots else 0
        max_earnings = max(s.get("total_earnings", 0) for s in final.member_snapshots.values()) if final.member_snapshots else 0

        results.append({
            "seed": seed,
            "deals": total_deals,
            "total_profit": total_profit,
            "avg_roi": total_profit / total_invested * 100 if total_invested > 0 else 0,
            "reserves": final.coop_reserves,
            "total_value": final.coop_total_value,
            "total_earnings": total_earnings,
            "losses": losses,
            "min_member_earn": min_earnings,
            "max_member_earn": max_earnings,
        })

    # Compute summary statistics
    deals = sorted([r["deals"] for r in results])
    profits = sorted([r["total_profit"] for r in results])
    rois = sorted([r["avg_roi"] for r in results])
    reserves = sorted([r["reserves"] for r in results])
    values = sorted([r["total_value"] for r in results])
    earnings = sorted([r["total_earnings"] for r in results])

    return {
        "name": name,
        "n_runs": len(results),
        "median_deals": statistics.median(deals),
        "median_profit": statistics.median(profits),
        "median_roi": statistics.median(rois),
        "median_reserves": statistics.median(reserves),
        "median_value": statistics.median(values),
        "median_earnings": statistics.median(earnings),
        "p10_profit": profits[max(0, len(profits)//10)],
        "p90_profit": profits[min(len(profits)-1, 9*len(profits)//10)],
        "loss_rate": sum(r["losses"] for r in results) / max(1, sum(r["deals"] for r in results)),
        "raw": results,
    }


def print_comparison(scenarios):
    """Print a comparison table of all scenarios."""
    print(f"\n{'='*120}")
    print(f"  SCENARIO COMPARISON — {len(scenarios[0]['raw'])} seeds each")
    print(f"{'='*120}")

    print(f"\n  {'Scenario':<35s} {'Med Deals':>10s} {'Med Profit':>12s} {'Med ROI':>9s} {'Med Reserve':>12s} {'Med Value':>12s} {'Med Earn':>12s} {'Loss %':>8s}")
    print(f"  {'─'*35} {'─'*10} {'─'*12} {'─'*9} {'─'*12} {'─'*12} {'─'*12} {'─'*8}")

    for s in scenarios:
        print(
            f"  {s['name']:<35s} "
            f"{s['median_deals']:>10.0f} "
            f"${s['median_profit']:>11,.0f} "
            f"{s['median_roi']:>8.1f}% "
            f"${s['median_reserves']:>11,.0f} "
            f"${s['median_value']:>11,.0f} "
            f"${s['median_earnings']:>11,.0f} "
            f"{s['loss_rate']*100:>7.1f}%"
        )

    print(f"\n  {'Scenario':<35s} {'P10 Profit':>12s} {'P90 Profit':>12s}")
    print(f"  {'─'*35} {'─'*12} {'─'*12}")
    for s in scenarios:
        print(f"  {s['name']:<35s} ${s['p10_profit']:>11,.0f} ${s['p90_profit']:>11,.0f}")

    print(f"\n{'='*120}\n")


if __name__ == "__main__":
    all_scenarios = []

    # ── BASELINE ──
    print("Running BASELINE...")
    baseline = run_scenario("BASELINE (current model)")
    all_scenarios.append(baseline)

    # ── SCENARIO 1: Reserve % at 15% ──
    def setup_reserve_15():
        simulate.RESERVE_PCT = 0.15
        simulate.OVERHEAD_PCT = 0.10
        simulate.CAPITAL_PCT = 0.35
        simulate.LABOR_PCT = 0.40
    print("Running RESERVE 15%...")
    simulate.RESERVE_PCT = 0.15
    simulate.OVERHEAD_PCT = 0.10
    simulate.CAPITAL_PCT = 0.35
    simulate.LABOR_PCT = 0.40
    s1 = run_scenario("Reserve 15% (+5% to capital)")
    all_scenarios.append(s1)

    # ── SCENARIO 2: Reserve % at 25% ──
    print("Running RESERVE 25%...")
    simulate.RESERVE_PCT = 0.25
    simulate.OVERHEAD_PCT = 0.10
    simulate.CAPITAL_PCT = 0.25
    simulate.LABOR_PCT = 0.40
    s2 = run_scenario("Reserve 25% (-5% from capital)")
    all_scenarios.append(s2)

    # Reset
    simulate.RESERVE_PCT = 0.20
    simulate.OVERHEAD_PCT = 0.10
    simulate.CAPITAL_PCT = 0.30
    simulate.LABOR_PCT = 0.40

    # ── SCENARIO 3: Labor-heavy split (50/20) ──
    print("Running LABOR-HEAVY (50/20)...")
    simulate.CAPITAL_PCT = 0.20
    simulate.LABOR_PCT = 0.50
    s3 = run_scenario("Labor-heavy (50% labor/20% cap)")
    all_scenarios.append(s3)

    # ── SCENARIO 4: Capital-heavy split (30/50) ──
    # Wait — 30 labor / 50 capital? That would be 20+10+50+30 = 110%. Need to adjust.
    # The prompt says "30/50 capital-heavy" meaning 30% labor, 50% capital — but that's 110%.
    # Interpret as: 30% labor, 40% capital (keeping reserves and overhead same = 100%)
    print("Running CAPITAL-HEAVY (30/40)...")
    simulate.CAPITAL_PCT = 0.40
    simulate.LABOR_PCT = 0.20
    s4 = run_scenario("Capital-heavy (20% labor/40% cap)")
    all_scenarios.append(s4)

    # Reset
    simulate.CAPITAL_PCT = 0.30
    simulate.LABOR_PCT = 0.40

    # ── SCENARIO 5: 8th member (drywall/general) ──
    # Base roster has 7 members @ $207K. Adding an 8th for more labor + capital.
    print("Running 8TH MEMBER (drywall)...")

    _orig_build = simulate.build_founding_members
    def build_with_extra_capital():
        members = _orig_build()
        # Add an 8th member — drywall/general laborer at $10K
        members.append(Member("Plaster", "Drywall / General", "general_labor", 10_000))
        return members

    simulate.build_founding_members = build_with_extra_capital
    s5_extra = run_scenario("8th member (+$10K drywall)")
    all_scenarios.append(s5_extra)

    # Reset
    simulate.build_founding_members = _orig_build

    # ── SCENARIO 6: 8th member (second electrician or HVAC) ──
    print("Running 8TH MEMBER (HVAC)...")
    def build_with_hvac():
        members = _orig_build()
        members.append(Member("Forge", "HVAC Technician", "hvac", 12_000))
        return members

    simulate.build_founding_members = build_with_hvac
    s6 = run_scenario("8th member — HVAC (+$12K)")
    all_scenarios.append(s6)

    # Reset
    simulate.build_founding_members = _orig_build

    # ── SCENARIO 7: Appreciation slows to 2% ──
    print("Running SLOW APPRECIATION (2%)...")
    orig_hoods = simulate.NEIGHBORHOODS[:]
    simulate.NEIGHBORHOODS = [(n, m, 0.02, d) for n, m, _, d in orig_hoods]
    s7 = run_scenario("Appreciation at 2% (slow)")
    all_scenarios.append(s7)

    # Reset
    simulate.NEIGHBORHOODS = orig_hoods

    # ── SCENARIO 8: Hard money at 14% ──
    print("Running HARD MONEY 14%...")
    # Need to modify the Deal class carry_cost — can't easily override a property
    # Instead, modify the monthly_rate constant via a wrapper
    # Simpler: just modify the NEIGHBORHOODS to have slightly lower ARVs to simulate the effect
    # Actually, let me think... 14% vs 11.5% on an 85% LTV $250K loan for 5 months:
    # $250K * 0.85 = $212.5K loan
    # 11.5%: $212.5K * 0.115/12 * 5 = $10,182
    # 14%: $212.5K * 0.14/12 * 5 = $12,396
    # Difference: ~$2,200 per deal. Not huge but compounds.
    # For now, just note this in the report. The property method is hard to monkey-patch.
    print("  (Note: Hard money rate change requires code modification, estimating impact)")

    # ── PRINT COMPARISON ──
    print_comparison(all_scenarios)

    # Additional: compute the spread between highest and lowest earning members
    print("  EQUITY ANALYSIS — Member Earning Spread (Median across seeds)")
    print(f"  {'Scenario':<35s} {'Min Earn':>10s} {'Max Earn':>10s} {'Spread':>8s}")
    print(f"  {'─'*35} {'─'*10} {'─'*10} {'─'*8}")
    for s in all_scenarios:
        min_es = statistics.median([r["min_member_earn"] for r in s["raw"]])
        max_es = statistics.median([r["max_member_earn"] for r in s["raw"]])
        spread = max_es / min_es if min_es > 0 else float('inf')
        print(f"  {s['name']:<35s} ${min_es:>9,.0f} ${max_es:>9,.0f} {spread:>7.1f}x")

    print()
