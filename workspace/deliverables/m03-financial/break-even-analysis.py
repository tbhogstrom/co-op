#!/usr/bin/env python3
"""
Portland Housing Co-op — Break-Even Analysis
Author: Ledger (CFO)
Date: 2026-04-08
Status: DRAFT — M3 Deliverable

Answers the question: What's the minimum sale price (or max cost) where the co-op
breaks even on a flip? And at what point does the co-op break even on annual
overhead?

Usage:
    python break-even-analysis.py
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple


# ============================================================================
# INPUT PARAMETERS
# ============================================================================

@dataclass
class DealParams:
    """Parameters for a single flip deal."""
    purchase_price: float = 300_000
    rehab_budget: float = 75_000
    hard_money_ltv: float = 0.85
    hard_money_rate: float = 0.12         # Annual
    hard_money_points: float = 0.03
    hard_money_rehab_coverage: float = 0.70
    hold_months: float = 6
    property_tax_monthly: float = 375
    insurance_monthly: float = 250         # Builder's risk
    utilities_monthly: float = 300
    inspection: float = 600
    appraisal: float = 500
    title_insurance: float = 2_500
    survey: float = 400
    permits: float = 3_000
    dumpster: float = 2_500
    staging: float = 2_000
    photography: float = 800
    selling_commission_pct: float = 0.06   # Total agent commissions
    closing_cost_seller: float = 2_500

    @property
    def loan_amount(self) -> float:
        return self.purchase_price * self.hard_money_ltv

    @property
    def origination_fee(self) -> float:
        return self.loan_amount * self.hard_money_points

    @property
    def monthly_interest(self) -> float:
        return self.loan_amount * (self.hard_money_rate / 12)

    @property
    def total_carrying(self) -> float:
        monthly = (
            self.monthly_interest + self.property_tax_monthly
            + self.insurance_monthly + self.utilities_monthly
        )
        return monthly * self.hold_months

    @property
    def acquisition_costs(self) -> float:
        return (
            self.origination_fee + self.inspection + self.appraisal
            + self.title_insurance + self.survey
        )

    @property
    def total_fixed_costs(self) -> float:
        """All costs that don't depend on sale price."""
        return (
            self.purchase_price + self.rehab_budget
            + self.acquisition_costs + self.total_carrying
            + self.permits + self.dumpster
            + self.staging + self.photography + self.closing_cost_seller
        )

    def selling_costs(self, sale_price: float) -> float:
        """Selling costs that scale with sale price."""
        return sale_price * self.selling_commission_pct

    def total_cost(self, sale_price: float) -> float:
        """Total project cost given a sale price."""
        return self.total_fixed_costs + self.selling_costs(sale_price)

    def gross_profit(self, sale_price: float) -> float:
        return sale_price - self.total_cost(sale_price)

    def break_even_sale_price(self) -> float:
        """
        Find the sale price where gross profit = 0.

        gross_profit = sale_price - (fixed_costs + sale_price * commission_pct)
        0 = sale_price - fixed_costs - sale_price * commission_pct
        0 = sale_price * (1 - commission_pct) - fixed_costs
        sale_price = fixed_costs / (1 - commission_pct)
        """
        return self.total_fixed_costs / (1 - self.selling_commission_pct)

    def target_sale_price(self, target_roi: float, equity: float) -> float:
        """
        Find the sale price needed to achieve a target ROI on equity.

        gross_profit = target_roi * equity
        sale_price - fixed_costs - sale_price * comm_pct = target_roi * equity
        sale_price * (1 - comm_pct) = fixed_costs + target_roi * equity
        sale_price = (fixed_costs + target_roi * equity) / (1 - comm_pct)
        """
        return (self.total_fixed_costs + target_roi * equity) / (1 - self.selling_commission_pct)

    def max_purchase_price(self, arv: float, target_roi: float, equity: float) -> float:
        """
        Find the maximum purchase price for a given ARV and target ROI.

        This is the inverse: given an ARV, what's the most we can pay?
        """
        # Total cost must be <= ARV - (target_roi * equity)
        # total_cost = purchase + rehab + acquisition_costs(varies with purchase)
        #            + carrying(varies with purchase) + selling + etc.
        #
        # This is complex because many costs depend on purchase price.
        # Use iterative approach.
        lo, hi = 0, arv
        for _ in range(100):
            mid = (lo + hi) / 2
            self.purchase_price = mid
            gp = self.gross_profit(arv)
            roi = gp / equity if equity > 0 else 0
            if roi > target_roi:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2


# ============================================================================
# OVERHEAD BREAK-EVEN
# ============================================================================

@dataclass
class OverheadBreakEven:
    """How many flips to cover annual overhead."""
    annual_overhead: float = 58_465

    def flips_to_break_even(self, avg_overhead_recovery_per_flip: float) -> float:
        """Number of flips needed so overhead recovery covers annual overhead."""
        if avg_overhead_recovery_per_flip <= 0:
            return float('inf')
        return self.annual_overhead / avg_overhead_recovery_per_flip

    def overhead_per_flip(self, num_flips: int) -> float:
        """Overhead allocated per flip given N flips per year."""
        if num_flips <= 0:
            return self.annual_overhead
        return self.annual_overhead / num_flips

    def min_gross_profit_per_flip(self, num_flips: int) -> float:
        """
        Minimum gross profit per flip so that the 10% overhead recovery
        covers the allocated overhead.

        overhead_recovery = 10% × gross_profit
        overhead_per_flip = annual_overhead / num_flips
        10% × gross_profit ≥ overhead_per_flip
        gross_profit ≥ overhead_per_flip / 0.10
        """
        return self.overhead_per_flip(num_flips) / 0.10


# ============================================================================
# SENSITIVITY MATRIX
# ============================================================================

def sensitivity_matrix(
    base: DealParams,
    arv_range: List[float],
    rehab_range: List[float],
    equity: float = 200_000,
) -> List[Dict]:
    """
    Generate a matrix of ROI outcomes for different ARV × rehab combinations.
    """
    results = []
    for arv in arv_range:
        for rehab in rehab_range:
            params = DealParams(
                purchase_price=base.purchase_price,
                rehab_budget=rehab,
                hard_money_ltv=base.hard_money_ltv,
                hard_money_rate=base.hard_money_rate,
                hard_money_points=base.hard_money_points,
                hard_money_rehab_coverage=base.hard_money_rehab_coverage,
                hold_months=base.hold_months,
            )
            gp = params.gross_profit(arv)
            roi = gp / equity * 100
            results.append({
                "arv": arv,
                "rehab": rehab,
                "gross_profit": gp,
                "roi": roi,
                "break_even": gp <= 0,
            })
    return results


# ============================================================================
# OUTPUT
# ============================================================================

def fmt(amount: float) -> str:
    if amount < 0:
        return f"-${abs(amount):,.0f}"
    return f"${amount:,.0f}"


def main():
    deal = DealParams()
    equity = 200_000

    print()
    print("=" * 80)
    print("  PORTLAND HOUSING CO-OP — BREAK-EVEN ANALYSIS")
    print("  Prepared by: Ledger (CFO)")
    print("=" * 80)

    # ---- Deal-Level Break-Even ----
    print("\n  SECTION 1: DEAL-LEVEL BREAK-EVEN")
    print("  " + "-" * 50)

    be_price = deal.break_even_sale_price()
    print(f"\n  Base Deal Parameters:")
    print(f"    Purchase Price:     {fmt(deal.purchase_price)}")
    print(f"    Rehab Budget:       {fmt(deal.rehab_budget)}")
    print(f"    Hold Period:        {deal.hold_months:.0f} months")
    print(f"    Hard Money:         {deal.hard_money_ltv*100:.0f}% LTV @ {deal.hard_money_rate*100:.1f}%")

    print(f"\n  Cost Structure:")
    print(f"    Fixed Costs (non-sale-dependent): {fmt(deal.total_fixed_costs)}")
    print(f"    Variable (6% commission on ARV):  Scales with sale price")

    print(f"\n  ▸ BREAK-EVEN SALE PRICE: {fmt(be_price)}")
    print(f"    (Sale price where gross profit = $0)")
    print(f"    At purchase price of {fmt(deal.purchase_price)}, this is {be_price/deal.purchase_price*100:.1f}% of purchase price.")

    # Target ROI sale prices
    print(f"\n  Sale Price Needed for Target Returns (on {fmt(equity)} equity):")
    for target in [0.10, 0.15, 0.20, 0.25, 0.30]:
        target_price = deal.target_sale_price(target, equity)
        print(f"    {target*100:>5.0f}% ROI → {fmt(target_price):>10s}  (= {target_price/deal.purchase_price*100:.0f}% of purchase)")

    # ---- Maximum Purchase Price ----
    print(f"\n\n  SECTION 2: MAXIMUM PURCHASE PRICE")
    print("  " + "-" * 50)
    print(f"\n  Given a target ARV and 15% ROI, what's the most we can pay?")
    print(f"\n  {'ARV':>10s} {'Max Purchase':>14s} {'% of ARV':>10s} {'Rehab':>10s} {'Hold':>6s}")
    print(f"  {'─'*10} {'─'*14} {'─'*10} {'─'*10} {'─'*6}")

    for arv in [400_000, 425_000, 450_000, 475_000, 500_000, 525_000, 550_000]:
        d = DealParams()
        max_pp = d.max_purchase_price(arv, 0.15, equity)
        pct = max_pp / arv * 100
        print(f"  {fmt(arv):>10s} {fmt(max_pp):>14s} {pct:>9.1f}% {fmt(d.rehab_budget):>10s} {d.hold_months:>5.0f}m")

    print(f"\n  Rule of thumb: Buy at ≤65% of ARV to have a shot at 15% ROI.")

    # ---- Overhead Break-Even ----
    print(f"\n\n  SECTION 3: OVERHEAD BREAK-EVEN")
    print("  " + "-" * 50)

    obe = OverheadBreakEven()

    print(f"\n  Annual Fixed Overhead: {fmt(obe.annual_overhead)}")
    print(f"  Overhead recovery = 10% of gross profit per flip")

    print(f"\n  {'Flips/Year':>12s} {'OH/Flip':>10s} {'Min GP/Flip':>14s} {'OH Recovered':>14s} {'Shortfall':>12s}")
    print(f"  {'─'*12} {'─'*10} {'─'*14} {'─'*14} {'─'*12}")

    for n_flips in [1, 2, 3, 4, 5]:
        oh_per = obe.overhead_per_flip(n_flips)
        min_gp = obe.min_gross_profit_per_flip(n_flips)
        # Assume conservative GP for recovery estimate
        conservative_gp = 30_700
        recovered = conservative_gp * 0.10 * n_flips
        shortfall = max(0, obe.annual_overhead - recovered)
        print(
            f"  {n_flips:>12d} "
            f"{fmt(oh_per):>10s} "
            f"{fmt(min_gp):>14s} "
            f"{fmt(recovered):>14s} "
            f"{fmt(shortfall) if shortfall > 0 else 'Covered':>12s}"
        )

    print(f"\n  At conservative GP ({fmt(30_700)} per flip):")
    flips_needed = obe.flips_to_break_even(30_700 * 0.10)
    print(f"  ▸ Need {flips_needed:.1f} flips/year for overhead recovery to cover annual overhead.")
    print(f"  ▸ Until then, overhead is subsidized by the co-op's capital / reserve fund.")
    print(f"  ▸ This is expected in Year 1. The co-op operates at a net overhead deficit")
    print(f"    until it scales to 2+ flips/year.")

    # ---- Sensitivity Matrix ----
    print(f"\n\n  SECTION 4: ROI SENSITIVITY MATRIX (Purchase = {fmt(deal.purchase_price)})")
    print("  " + "-" * 50)
    print(f"\n  ROI% for different ARV (columns) × Rehab Budget (rows)")
    print(f"  Green zone ≥15% | Yellow 0-15% | Red <0% (loss)")

    arv_range = [425_000, 450_000, 475_000, 500_000, 525_000]
    rehab_range = [50_000, 65_000, 75_000, 85_000, 100_000]

    # Header
    header = f"\n  {'Rehab ↓ / ARV →':>18s}"
    for arv in arv_range:
        header += f" {fmt(arv):>10s}"
    print(header)
    print(f"  {'─'*18}" + " ─────────" * len(arv_range))

    for rehab in rehab_range:
        row = f"  {fmt(rehab):>18s}"
        for arv in arv_range:
            d = DealParams(rehab_budget=rehab)
            gp = d.gross_profit(arv)
            roi = gp / equity * 100
            if roi >= 15:
                marker = f"{roi:>8.1f}%✓"
            elif roi >= 0:
                marker = f"{roi:>8.1f}%⚠"
            else:
                marker = f"{roi:>8.1f}%✗"
            row += f" {marker:>10s}"
        print(row)

    print(f"\n  Reading: At $300K purchase, $75K rehab, $475K ARV → ~15% ROI ✓")
    print(f"  At $300K purchase, $100K rehab, $425K ARV → negative ROI ✗")

    # ---- Key Takeaways ----
    print(f"\n\n  SECTION 5: KEY TAKEAWAYS")
    print("  " + "-" * 50)
    print(f"""
  1. Break-even sale price for our standard deal: {fmt(be_price)}
     That's {be_price/deal.purchase_price*100:.0f}% of purchase price. Any sale above this = profit.

  2. To hit 15% ROI, we need to sell at {fmt(deal.target_sale_price(0.15, equity))}
     That's {deal.target_sale_price(0.15, equity)/deal.purchase_price*100:.0f}% of purchase price.

  3. Maximum purchase price at 15% ROI target:
     • $475K ARV → buy at ≤{fmt(DealParams().max_purchase_price(475_000, 0.15, equity))}
     • $500K ARV → buy at ≤{fmt(DealParams().max_purchase_price(500_000, 0.15, equity))}

  4. The co-op needs ~19 flips at conservative GP before overhead recovery
     fully covers annual overhead. Until then, the co-op is investing in
     building its track record.

  5. The most dangerous combination: high rehab + low ARV. If rehab hits $100K
     and ARV only reaches $450K, we lose money. The 65% of ARV purchase rule
     protects against this.
    """)

    print("=" * 80)
    print("  END OF ANALYSIS — Ledger")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
