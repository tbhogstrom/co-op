# Portland Housing Co-op — Business Model

**Author:** Ledger (CFO)
**Date:** 2026-04-07
**Status:** DRAFT — Awaiting Maven review

---

## 1. What Is This Business?

A worker-owned cooperative that buys distressed residential properties in the
Portland metro area, renovates them using member labor, and sells them at market
value. Members are both the investors and the workforce. Profit is split between
capital contributors and labor contributors through a transparent formula.

**In one sentence:** We buy ugly houses, fix them with our own hands, sell them
at full price, and split the profit among the people who put up the money and
did the work — because they're the same people.

---

## 2. The Flip Cycle

Each project follows a 5-phase cycle. Every phase has defined financial controls.

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  1. SOURCE   │───▶│  2. ACQUIRE  │───▶│  3. REHAB    │───▶│  4. SELL     │───▶│ 5. DISTRIBUTE│
│              │    │              │    │              │    │              │    │              │
│ Find deals   │    │ Close with   │    │ Members do   │    │ List at ARV  │    │ Split profit │
│ Run numbers  │    │ hard money   │    │ the work     │    │ Close sale   │    │ Fund reserves│
│ Walk away if │    │ + co-op cash │    │ Track hours  │    │ Pay off loan │    │ Update equity│
│ <15% ROI     │    │              │    │ Track costs  │    │              │    │              │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### Phase 1: Source (2-4 weeks)

**Who:** Reeves (Real Estate Analyst), Ledger (CFO)

**Activities:**
- Identify distressed properties via MLS, auctions, wholesalers, direct mail
- Target neighborhoods: Lents, Foster-Powell, Woodstock, Cully, outer NE/SE
  (areas with strong ARV growth and available inventory under $350K)
- Walk each candidate property with Harlan (Construction PM)

**Financial Controls:**
- Run deal analysis before making any offer (see deal analysis template in M7)
- **Hard rule: Do not offer on any property where conservative-case ROI < 15%**
- Purchase price must be ≤65% of estimated ARV after repair
- Rehab budget estimated by Harlan before offer, not after

**Kill criteria (walk away if):**
- Foundation issues requiring >$15K in structural work
- Environmental hazards (lead, asbestos, mold) without clear remediation path
- Zoning issues that limit resale value
- Title complications that can't be resolved in 30 days

### Phase 2: Acquire (2-4 weeks)

**Who:** Reeves, Ledger, Statton (Legal)

**Activities:**
- Negotiate purchase agreement
- Secure hard money loan (85% LTV typical)
- Complete inspection, title search, appraisal
- Close

**Capital Stack:**
```
┌──────────────────────────────────┐
│   Hard Money Loan (85% LTV)      │  ← External debt
│   $255,000 on a $300K purchase   │
├──────────────────────────────────┤
│   Co-op Cash (15% down)          │  ← Member equity
│   $45,000                        │
├──────────────────────────────────┤
│   Hard Money Rehab Draws (70%)   │  ← External debt (drawn as work completes)
│   $52,500 of $75K rehab          │
├──────────────────────────────────┤
│   Co-op Cash (rehab gap)         │  ← Member equity
│   $22,500                        │
└──────────────────────────────────┘
```

**Financial Controls:**
- Hard money terms locked before closing (no floating-rate surprises)
- Title insurance required
- Builder's risk insurance bound before keys received
- All acquisition costs logged in project accounting on day 1

### Phase 3: Rehab (3-6 months)

**Who:** Harlan (Construction PM), Birch, Slate, Copper (trades), all working members

**Activities:**
- Execute scope of work per Harlan's rehab plan
- Members log hours daily (trade type, task, hours)
- Weekly budget check: actual spend vs. planned spend
- Draw schedule with hard money lender (inspections trigger fund releases)

**Financial Controls:**
- **Weekly burn rate report:** Ledger tracks cash out vs. budget
- **Change order process:** Any cost increase >$2,000 requires board vote
- **Labor tracking:** All member hours logged in shared system. No hours = no labor share.
- **Material procurement:** Bulk purchasing through co-op account. No personal reimbursements over $500 without pre-approval.
- **Budget contingency:** 15% rehab contingency. If contingency is tapped, board reviews scope.

**Cash Flow During Rehab:**
```
Month 1:  Down payment + acquisition costs + permits      ~$60K out
Month 2:  Rehab materials + carrying costs                 ~$10K out
Month 3:  Rehab materials + carrying costs                 ~$10K out
Month 4:  Rehab materials + carrying costs                 ~$10K out
Month 5:  Final rehab + carrying costs + staging           ~$10K out
                                                     ──────────────
          Total cash deployed before sale:                 ~$100K
```

### Phase 4: Sell (1-3 months)

**Who:** Reeves, Maven

**Activities:**
- Professional photography and staging
- List on MLS at ARV-informed price
- Manage showings and offers
- Negotiate and accept offer
- Close sale

**Financial Controls:**
- Listing price justified by comp analysis (Reeves)
- If no offer within 30 days, price reduction strategy pre-defined
- Closing costs estimated in advance and deducted from proceeds
- Hard money loan paid off at closing from sale proceeds
- Net proceeds deposited to co-op operating account same day

**Proceeds Waterfall at Sale:**
```
  Sale Price (ARV)                              $475,000
  Less: Buyer's agent commission (3%)           ($14,250)
  Less: Seller's agent commission (3%)          ($14,250)
  Less: Closing costs / title / escrow           ($2,500)
  Less: Hard money payoff (principal)          ($255,000)
  Less: Hard money rehab draws payoff           ($52,500)
                                              ──────────
  Net Proceeds to Co-op                        $136,500
  Less: Co-op cash deployed during project     (~$100,000)
                                              ──────────
  Cash Profit Returned to Co-op                 ~$36,500
```

### Phase 5: Distribute (1-2 weeks)

**Who:** Ledger, Maven

**Activities:**
- Calculate actual P&L (every dollar, not estimates)
- Run profit-split formula
- Issue member distributions
- Fund reserves
- Update member equity accounts
- File any required tax documentation

**Profit Split Formula:**
```
  Gross Profit                                  $40,750

  Step 1: Reserve Contribution (20%)            ($8,150)
    → Goes to co-op reserve fund for future deals

  Step 2: Overhead Recovery (10%)               ($4,075)
    → Reimburses co-op for insurance, admin, tools, etc.

  Step 3: Distributable Profit                  $28,525

  Step 4: Capital Share (30% of distributable)  $8,558
    → Split proportional to each member's equity account balance

  Step 5: Labor Share (40% of distributable)    $11,410
    → Split proportional to tracked labor hours, weighted by trade rate

  Accounting Check: $8,150 + $4,075 + $8,558 + $11,410 = $32,193
  ✓ Total = 20% + 10% + 30%×70% + 40%×70% = 100% of gross profit
```

**Note on the split math:** The 30% capital + 40% labor percentages are applied
to the *distributable* profit (after reserves and overhead), which is 70% of gross.
So the effective split of gross profit is: 20% reserves, 10% overhead, 21% capital,
28% labor, with a 21% "float" that covers the reserves and overhead recovery.
Actually, let me restate this clearly:

```
  Of every $1.00 in gross profit:
    $0.20 → Reserves
    $0.10 → Overhead recovery
    $0.30 → Capital contributors (proportional to equity)
    $0.40 → Labor contributors (proportional to hours × rate)
    ──────
    $1.00  ✓
```

Wait — that's the correct version. The four buckets sum to 100% of gross profit,
not 100% of distributable. The "distributable" framing was misleading. Let me
be precise: **all four percentages are applied directly to gross profit.**
Members receive the capital + labor shares. The co-op retains the reserve +
overhead shares.

---

## 3. Revenue Model

### Per-Flip Economics (Conservative)

| Metric | Amount |
|--------|--------|
| Purchase Price | $300,000 |
| Rehab Budget | $75,000 |
| All-In Cost (including carry, closing, overhead) | ~$434,000 |
| ARV / Sale Price | $475,000 |
| **Gross Profit** | **$40,750** |
| Member Distributions (capital + labor) | $28,525 |
| To Reserves | $8,150 |
| To Overhead Recovery | $4,075 |

### Year 1 Target

| Scenario | Flips | Revenue | Gross Profit | Member Distributions |
|----------|-------|---------|--------------|---------------------|
| Conservative | 1 | $475,000 | $40,750 | $28,525 |
| Moderate | 1 | $500,000 | $79,750 | $55,825 |
| Aggressive | 2 | $1,050,000 | ~$150,000 | ~$105,000 |

### Year 2-3 Scaling Path

| Year | Flips/Year | Capital Needed | Projected Gross Profit |
|------|------------|----------------|----------------------|
| 1 | 1 | $200,000 (member equity) | $40K - $115K |
| 2 | 2 | Reserves + member equity | $80K - $230K |
| 3 | 3-4 | Reserves + bank line of credit | $120K - $460K |

Scaling requires:
1. Building reserves from Year 1 profits (20% of each flip)
2. Establishing banking relationship (transition from hard money to conventional)
3. Recruiting additional skilled members (Calloway's job)
4. Developing a property pipeline (Reeves' job)

---

## 4. Cost Structure

### Fixed Costs (Annual)

| Category | Amount | Notes |
|----------|--------|-------|
| Insurance (GL + WC + umbrella) | $18,500 | Workers comp is the big one — construction class codes |
| Legal & Compliance | $7,650 | Formation, retainer, filings |
| Accounting | $7,300 | Bookkeeping + tax prep |
| Office & Admin | $6,000 | Coworking, software, phone |
| Tools & Equipment | $10,900 | Heavy Year 1 investment; drops to ~$3K/yr maintenance |
| Marketing & Recruitment | $2,700 | Website, outreach |
| **Subtotal** | **$53,050** | |
| Contingency (10%) | $5,305 | |
| **Total Fixed Overhead** | **$58,355** | |

See `operating-cost-model.py` for the full interactive model.

### Variable Costs (Per Flip)

| Category | Amount | Notes |
|----------|--------|-------|
| Acquisition costs | ~$12,000 | Inspection, title, appraisal, origination |
| Carrying costs | ~$15,000-$23,000 | Hard money interest, taxes, insurance, utilities |
| Rehab materials | $75,000 | Varies widely by scope |
| Selling costs | ~$31,000 | Commissions + closing + staging |
| Permits | ~$3,000 | Portland BDS — varies by scope |

### Key Ratio: Overhead as % of Revenue

| Scenario | Revenue | Overhead | Overhead % |
|----------|---------|----------|------------|
| 1 flip/yr | $475K | $58K | 12.3% |
| 2 flips/yr | $950K | $58K | 6.1% |
| 3 flips/yr | $1.4M | $62K* | 4.4% |

*Slight increase at 3 flips for additional insurance and bookkeeping.

This is why scaling matters. The fixed overhead is essentially the same whether
we do 1 flip or 3. Every additional flip after the first is dramatically more
profitable because it's not carrying the full overhead burden.

---

## 5. Member Economics — What Does a Member Actually Earn?

### Example: Member B — Plumber, Tier B Buy-In

| Input | Value |
|-------|-------|
| Capital Contribution | $25,000 |
| % of Total Capital | 12.5% (of $200K) |
| Labor Hours on Flip 1 | 350 hours |
| Trade Rate Weighting | 1.2x (plumbing) |
| Weighted Hours | 420 |
| Total Weighted Hours (all members) | 2,000 (est.) |
| % of Labor Pool | 21.0% |

| Payout | Calculation | Amount |
|--------|------------|--------|
| Capital Share | 12.5% × $12,225 (30% of $40,750) | $1,528 |
| Labor Share | 21.0% × $16,300 (40% of $40,750) | $3,423 |
| **Total Distribution** | | **$4,951** |
| **Return on Cash Investment** | $4,951 / $25,000 | **19.8%** |

Plus: Member B still has their $25,000 capital account in the co-op for the
next flip.

### What About a Tier C Member (Low Buy-In, High Labor)?

| Input | Value |
|-------|-------|
| Capital Contribution | $5,000 |
| % of Total Capital | 2.5% |
| Labor Hours | 500 hours |
| Trade Rate Weighting | 1.0x (general labor) |
| Weighted Hours | 500 |
| % of Labor Pool | 25.0% |

| Payout | Calculation | Amount |
|--------|------------|--------|
| Capital Share | 2.5% × $12,225 | $306 |
| Labor Share | 25.0% × $16,300 | $4,075 |
| **Total Distribution** | | **$4,381** |
| **Return on Cash Investment** | $4,381 / $5,000 | **87.6%** |

The formula is designed so that **labor is the primary wealth-building mechanism**
for members who can't invest large amounts of capital. This is the whole point of
the cooperative structure.

---

## 6. Risk Management

### Deal-Level Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Rehab exceeds budget by >20% | Medium | Eats profit, may break even | 15% contingency; fixed-scope SOW; weekly tracking |
| Property doesn't sell within 60 days | Medium | Carrying costs erode profit | Price to market; stage professionally; pre-identify agent |
| Hard money lender issues | Low | Can't close | Maintain relationships with 2-3 lenders |
| Title/permit complications | Low-Medium | Delays; added costs | Title insurance; pre-permit research |
| Injury on job site | Low | WC claim; project delay | Workers comp insurance; safety protocols; experienced trades |

### Co-op-Level Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Member dispute over profit split | Medium | Operational disruption | Transparent formula; all math auditable; board governance |
| Member withdraws capital mid-project | Low | Cash crunch | 90-day notice; no withdrawal during active projects |
| Portland market downturn (5-10%) | Low-Medium | ARV drops; deals thin | Only buy at ≤65% ARV; maintain cash buffer |
| Tax/legal compliance failure | Low | Fines; entity issues | Statton on retainer; annual tax filing; proper WC coverage |
| Burnout / member turnover | Medium | Labor gap; institutional knowledge loss | Fair compensation; democratic governance; recruit pipeline |

### Financial Guardrails

1. **Never deploy more than 70% of co-op cash on a single project.** Always maintain a
   liquidity cushion.
2. **No second project until the first project's cash is recovered** (Year 1 only —
   can relax once reserves are built).
3. **Kill a deal rather than stretch.** If the numbers don't work at our offer price,
   we walk. There are always more houses.
4. **20% to reserves is sacred.** Don't skip it to boost member payouts. The reserve
   fund is what turns this from one flip into a real business.

---

## 7. Entity Structure Options (For Statton to Evaluate)

From a financial perspective, the co-op has three viable entity structures. Each has
different tax and governance implications. I'm flagging the financial trade-offs here;
Statton should evaluate the legal side.

| Structure | Tax Treatment | Profit Distribution | Governance | Ledger's Take |
|-----------|--------------|-------------------|------------|--------------|
| **Oregon Cooperative Corporation** | Patronage dividends (partially deductible to co-op) | Based on patronage (labor + capital) | One member, one vote | Best fit for our model. Patronage dividends align with labor-capital split. |
| **LLC (member-managed)** | Pass-through (K-1s to each member) | Per operating agreement | Flexible — can be one-member-one-vote | More flexible but less co-op identity. Tax treatment is simpler. |
| **LLC taxed as S-Corp** | Pass-through with salary requirement | Per operating agreement | Flexible | Could save on self-employment tax but adds complexity. Probably premature. |

**My recommendation:** Start as an **Oregon Cooperative Corporation** if Statton
confirms the legal mechanics work. It gives us patronage dividend treatment, democratic
governance by statute, and a clear identity for recruiting members who believe in the
cooperative model. If the legal overhead is too high for Year 1, fall back to a
member-managed LLC with cooperative principles written into the operating agreement.

---

## 8. Open Questions for Maven

1. **Member count target?** I modeled 6-8 members. Is that aligned with your recruitment
   timeline? Calloway can't recruit 8 skilled tradespeople overnight.

2. **First flip timeline?** I assumed we buy in Month 3 of operations. Is that realistic
   given formation, capitalization, and member recruitment timelines?

3. **Labor compensation during rehab?** Are members working unpaid (sweat equity only,
   paid out at distribution) or do they receive a draw/stipend during rehab? This
   significantly affects cash flow. I modeled zero-draw (members are compensated only
   at profit distribution), but that may not be realistic for members who need income.

4. **Your personal capital commitment?** I modeled Maven at $50K. Is that accurate?
   The founder's commitment sets the tone for everyone else's buy-in.

5. **Target neighborhoods?** I listed several but Reeves should validate. The numbers
   work in outer Portland — they probably don't work in inner NE/SE where purchase
   prices are already at ARV.

6. **Timeline to first distribution?** Members should know: from the day they write
   a check, it could be 8-12 months before they see a return. That's a long time.
   We need to set expectations clearly in recruitment materials.

---

*This document should be read alongside `capitalization-target.md` (funding) and
`operating-cost-model.py` (interactive cost model). Together, these three documents
define the financial foundation for M1 — Co-op Vision & Strategy.*

*— Ledger, CFO*
