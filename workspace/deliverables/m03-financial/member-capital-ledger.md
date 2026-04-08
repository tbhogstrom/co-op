# Portland Housing Co-op — Member Capital Account Ledger

**Author:** Ledger (CFO)
**Date:** 2026-04-08
**Status:** DRAFT — M3 Deliverable

---

## Founding Member Capital Accounts

Pre-populated with the approved 6-member, $120K capitalization scenario.

> **Note:** Total initial capitalization below is $120,000 based on Maven's approved
> member roster (Maven $50K, Birch $15K, Slate $10K, Copper $25K, Member E $15K,
> Member F $5K). If we recruit to the full $200K target, additional members or
> increased buy-ins will be added to this ledger.

---

### Maven — Founder / Operations / PM

| Date | Transaction Type | Amount | Project | Running Balance | Notes |
|------|-----------------|--------|---------|----------------|-------|
| 2026-05-01 | Initial Buy-In | +$50,000.00 | — | $50,000.00 | Tier A member |
| | | | | | |
| | | | | **$50,000.00** | |

### Birch — Carpenter

| Date | Transaction Type | Amount | Project | Running Balance | Notes |
|------|-----------------|--------|---------|----------------|-------|
| 2026-05-01 | Initial Buy-In | +$15,000.00 | — | $15,000.00 | Tier B member |
| | | | | | |
| | | | | **$15,000.00** | |

### Slate — Roofer

| Date | Transaction Type | Amount | Project | Running Balance | Notes |
|------|-----------------|--------|---------|----------------|-------|
| 2026-05-01 | Initial Buy-In | +$10,000.00 | — | $10,000.00 | Tier B member |
| | | | | | |
| | | | | **$10,000.00** | |

### Copper — Plumber

| Date | Transaction Type | Amount | Project | Running Balance | Notes |
|------|-----------------|--------|---------|----------------|-------|
| 2026-05-01 | Initial Buy-In | +$25,000.00 | — | $25,000.00 | Tier B member |
| | | | | | |
| | | | | **$25,000.00** | |

### Member E — General Labor

| Date | Transaction Type | Amount | Project | Running Balance | Notes |
|------|-----------------|--------|---------|----------------|-------|
| 2026-05-01 | Initial Buy-In | +$15,000.00 | — | $15,000.00 | Tier B member |
| | | | | | |
| | | | | **$15,000.00** | |

### Member F — General Labor

| Date | Transaction Type | Amount | Project | Running Balance | Notes |
|------|-----------------|--------|---------|----------------|-------|
| 2026-05-01 | Initial Buy-In | +$5,000.00 | — | $5,000.00 | Tier C member |
| | | | | | |
| | | | | **$5,000.00** | |

---

## Summary Table

| Member | Initial Buy-In | Additional Contributions | Profit Allocated | Distributions Paid | Advances Outstanding | Current Balance | % of Capital |
|--------|---------------|------------------------|------------------|-------------------|---------------------|----------------|-------------|
| Maven | $50,000 | $0 | $0 | $0 | $0 | $50,000 | 41.7% |
| Birch | $15,000 | $0 | $0 | $0 | $0 | $15,000 | 12.5% |
| Slate | $10,000 | $0 | $0 | $0 | $0 | $10,000 | 8.3% |
| Copper | $25,000 | $0 | $0 | $0 | $0 | $25,000 | 20.8% |
| Member E | $15,000 | $0 | $0 | $0 | $0 | $15,000 | 12.5% |
| Member F | $5,000 | $0 | $0 | $0 | $0 | $5,000 | 4.2% |
| **Total** | **$120,000** | **$0** | **$0** | **$0** | **$0** | **$120,000** | **100%** |

---

## Transaction Types

| Code | Description | Effect on Balance |
|------|-------------|------------------|
| `buy_in` | Initial member contribution | + |
| `additional_contribution` | Additional capital invested | + |
| `profit_allocation` | Share of flip profit (capital + labor share) | + |
| `loss_allocation` | Share of flip loss | − |
| `distribution` | Cash paid out to member | − |
| `advance_draw` | Labor advance drawn during rehab | − (temporary) |
| `advance_repayment` | Advance deducted from distribution or repaid | + (reversal) |
| `withdrawal` | Capital withdrawal (90-day notice, board approval) | − |

---

## Advance Tracking Sub-Ledger

| Date | Member | Project | Amount | Status | Repayment Date | Notes |
|------|--------|---------|--------|--------|----------------|-------|
| *(No advances yet — project not started)* | | | | | | |

### Advance Policy Reminder

- Max advance: 50% of estimated labor share (conservative scenario)
- Available after 30% rehab completion
- Board approval required for each draw
- Deducted from final distribution at project close
- If distribution < advances, difference deducted from capital account

---

## Co-op Reserve Fund

| Date | Transaction | Amount | Balance | Notes |
|------|-------------|--------|---------|-------|
| 2026-05-01 | Opening balance | $0 | $0 | |
| | | | **$0** | |

**Target reserve balance after first flip:** $6,000 - $12,000 (20% of gross profit)

---

## Accounting Notes

1. This ledger is the **source of truth** for member equity positions.
2. All transactions must be supported by documentation (receipts, board minutes, profit distribution worksheets).
3. Capital account balances are reported to members monthly during active projects, quarterly otherwise.
4. Year-end balances are used for K-1 preparation.
5. For the automated version, see `tools/profit-splitter/equity_tracker.py`.

---

*— Ledger, CFO*
