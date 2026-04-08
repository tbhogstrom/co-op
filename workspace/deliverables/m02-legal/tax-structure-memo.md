# Tax Structure Memorandum
# Portland Housing Cooperative, LLC

**Prepared by:** Statton, Legal Counsel
**Date:** 2026-04-08
**Status:** DRAFT
**To:** Ledger (CFO), Maven (Founder/Operations)
**Re:** (a) Oregon PTE Tax Election; (b) S-Corp Election Feasibility

---

## Background

Ledger flagged two tax-planning questions in the capital structure memo (M3). This memorandum provides preliminary legal analysis and recommendations on each.

The Co-op is organized as an Oregon LLC taxed as a partnership (Form 1065, K-1s to members). All six founding members are Oregon residents. The Co-op's Year 1 projected gross profit ranges from $30,700 (conservative) to $59,762 (moderate) per flip, with 1-2 flips expected in Year 1.

---

## Issue (a): Oregon Pass-Through Entity (PTE) Tax Election

### What It Is

Oregon's PTE tax (ORS 314.991-314.997, effective 2022) allows pass-through entities (partnerships, LLCs, S-corps) to elect to pay Oregon income tax at the entity level on distributive income, rather than having each member pay Oregon tax individually. The entity pays Oregon income tax at a rate of 9% on the members' aggregate Oregon-source distributive income. Each member then claims a corresponding credit on their individual Oregon return, effectively offsetting the Oregon tax they would otherwise owe on that income.

### Why It Matters

The federal Tax Cuts and Jobs Act (IRC Section 164(b)(6)) caps the individual state and local tax (SALT) deduction at $10,000. For members who already hit that cap through property taxes and other state taxes, Oregon income tax on Co-op distributions is not deductible on their federal return. The PTE election moves the tax payment to the entity level, where it becomes a deduction against partnership income (reducing each member's K-1 income), effectively circumventing the SALT cap.

### Analysis

**Pros:**

1. **SALT cap workaround.** Members who itemize and exceed the $10,000 SALT cap get a meaningful federal tax benefit. For a member with $10,000 of Co-op income, the benefit is approximately 9% x $10,000 x (member's marginal federal rate, e.g., 22-24%) = $200-$216 per member per year at conservative-scenario scale.

2. **Administrative simplicity.** The Co-op makes one tax payment rather than each member separately paying Oregon estimated taxes on Co-op income.

3. **No change to economic structure.** The PTE election is a tax reporting mechanism only. It does not change the profit split, governance, or operating agreement.

**Cons:**

1. **Benefit is marginal at Year 1 scale.** With conservative gross profit of $30,700 and six members, individual distributive shares are modest ($3,000-$5,000). The federal tax savings per member may be only $50-$200.

2. **Not all members may benefit.** Members who do not itemize deductions (i.e., who take the standard deduction) receive no benefit from the SALT workaround.

3. **Cash flow timing.** The Co-op must pay estimated PTE tax quarterly (ORS 314.995), which ties up cash at the entity level. On a thin-margin first flip, this creates cash flow drag.

4. **Added tax return complexity.** The Co-op's tax preparer must compute the PTE tax, file the election, and coordinate credits on each member's individual return.

### Recommendation

**Defer the PTE election in Year 1.** The tax benefit is negligible at current scale, and the administrative burden and cash flow impact are not justified. **Revisit when the Co-op's annual distributive income exceeds approximately $50,000 per member** (roughly 3-4 flips per year at moderate profitability). At that point, the SALT cap benefit becomes meaningful and the election should be made.

The election is made annually (ORS 314.993), so there is no cost to waiting. Ledger should flag this for review at the beginning of each fiscal year.

---

## Issue (b): S-Corp Election

### What It Is

An LLC may elect to be taxed as an S corporation by filing IRS Form 2553 (IRC Section 1362). Under S-corp taxation, the entity files Form 1120-S (instead of Form 1065). Income still passes through to members on K-1s, but members who perform services for the entity can split their income between (i) "reasonable compensation" (wages subject to payroll taxes) and (ii) distributions (not subject to self-employment tax).

### Why It Matters

Members' distributive share of LLC income is generally subject to self-employment (SE) tax at 15.3% on the first ~$160,200 (2023 threshold, indexed for inflation; 2.9% Medicare tax on amounts above). An S-corp election allows members to pay SE tax (via payroll tax) only on the "reasonable compensation" portion and take the remainder as distributions free of SE tax.

### Feasibility Analysis

**Problem 1: One Class of Stock Rule (IRC Section 1361(b)(1)(D))**

An S corporation may have only one class of stock. All shares must confer identical rights to distribution and liquidation proceeds. The Co-op's structure creates complications:

- Capital Share distributions are proportional to capital account balances (which differ by member).
- Labor Share distributions are proportional to weighted labor hours (which differ by member and by project).
- These disproportionate distributions may be treated as creating a second class of stock, which would disqualify the S-corp election.

This is the most significant legal barrier. The IRS has ruled that disproportionate distributions based on differing partnership allocations violate the one-class-of-stock rule. The Co-op's 30/40 capital/labor split is fundamentally incompatible with S-corp structure.

**Problem 2: Reasonable Compensation Requirement**

The IRS requires S-corp shareholder-employees to receive "reasonable compensation" for services performed. For co-op members who contribute hundreds of hours of skilled trade labor, reasonable compensation could be substantial (e.g., $25-$50/hour for trade work). At Year 1 scale, the members' total distributions may be less than what the IRS would consider reasonable compensation for the hours worked, eliminating any SE tax savings.

**Problem 3: Cooperative Principles Conflict**

S-corp taxation imposes a rigid one-class-of-stock framework that conflicts with cooperative principles of patronage-based distribution. The labor-weighted profit split is the core mechanism that distinguishes this cooperative from a standard investment LLC. An S-corp election would require abandoning this structure.

**Problem 4: Oregon Filing**

Oregon requires a separate state-level S-corp election. Oregon S corps are subject to the Oregon minimum corporate excise tax ($150/year) rather than the $100 LLC annual fee. The difference is trivial, but the additional filing requirements are not.

### At What Scale Would It Make Sense?

In theory, the SE tax savings become meaningful when a member's annual distributive share exceeds approximately $40,000-$50,000 (at which point the SE tax on the excess above "reasonable compensation" could save $3,000-$5,000/year). However, the structural incompatibility (Problem 1) makes this analysis academic for this Co-op. The labor/capital split cannot be preserved under an S-corp.

### Recommendation

**Do not elect S-corp taxation.** The Co-op's patronage-based profit split (30% capital / 40% labor, with varying capital accounts and varying labor hours per project) is fundamentally incompatible with the one-class-of-stock requirement of IRC Section 1361(b)(1)(D). The S-corp election would require either (a) abandoning the labor-weighted distribution model, or (b) restructuring all members' economic rights to be identical — both of which defeat the cooperative's core design.

The Co-op should remain taxed as a partnership (Form 1065). Members should mitigate SE tax exposure through:

1. Maximizing deductible business expenses on their individual Schedule C (for their independent trade businesses);
2. Contributing to tax-advantaged retirement accounts (SEP-IRA, Solo 401(k)) funded from Co-op distributions; and
3. Properly characterizing guaranteed payments (if any) vs. distributive shares to optimize SE tax treatment under IRC Section 1402(a).

---

## Summary of Recommendations

| Issue | Recommendation | Timing |
|-------|---------------|--------|
| Oregon PTE Tax Election | Defer in Year 1; revisit when per-member income exceeds ~$50K/year | Annual review |
| S-Corp Election | Do not elect; structurally incompatible with cooperative profit split | Permanent (unless profit split is restructured) |

---

## Limitations

This memorandum is a preliminary analysis prepared as part of a simulation exercise. It is not legal advice or tax advice. It does not create an attorney-client or accountant-client relationship. The Co-op and its members should consult a licensed Oregon CPA and/or tax attorney before making any tax elections. IRC and ORS citations should be verified against current law. Tax rates, thresholds, and regulations are subject to change.
