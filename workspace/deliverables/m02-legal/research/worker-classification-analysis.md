# Worker Classification Analysis — Co-op Members

**Prepared by:** Statton, Legal Counsel
**Date:** 2026-04-07
**Status:** PRELIMINARY
**For:** Maven (Founder), Harlan (General Contractor), Ledger (CFO)

---

## 1. Issue

How should the Portland Housing Co-op classify its member-tradespeople for purposes of Oregon employment law, workers' compensation, and federal tax law? This classification has cascading effects on:

- Workers' compensation obligations (ORS Chapter 656)
- Unemployment insurance obligations (ORS Chapter 657)
- Payroll tax obligations (federal and state)
- CCB licensing structure
- Operating Agreement and Member Agreement drafting
- Liability exposure

---

## 2. The Three Classification Options

### A. Employee

Members are W-2 employees of the co-op. The co-op withholds income tax, pays employer FICA, provides workers' compensation, and manages payroll.

**Pros:**
- Clear legal framework — well-understood by regulators
- Workers' compensation coverage protects members on job sites
- Members may prefer W-2 status for mortgage qualification, unemployment eligibility

**Cons:**
- Fundamentally inconsistent with cooperative ownership model — employees don't "own" the business in the same sense
- Co-op bears full payroll tax burden (employer FICA: 7.65%, FUTA, SUTA)
- Co-op must comply with Oregon wage and hour laws (ORS Chapter 652, 653) — minimum wage, overtime, meal/rest periods
- Members cannot share in losses (employees cannot have negative compensation)
- **Risk (HIGH):** Oregon Employment Department and IRS may view co-op members performing construction labor as employees regardless of what the Operating Agreement says, if the economic reality test is not satisfied

### B. Independent Contractor

Members are 1099 independent contractors who contract with the co-op to perform specific work on specific projects.

**Pros:**
- Each member controls their own work schedule, methods, and tools
- Aligns with the CCB licensing model (each member holds own license)
- Co-op avoids payroll tax and workers' comp obligations
- Members deduct business expenses on Schedule C

**Cons:**
- Must genuinely satisfy Oregon's independent contractor test (ORS 670.600) — cannot simply label someone an IC
- Each member must carry their own workers' comp (if they have employees) or waive coverage
- Co-op has less control over work quality and scheduling
- **Risk (MEDIUM):** If the co-op exercises significant control over when, where, and how members work (which it will, on a construction project with deadlines), the IC classification may be challenged

### C. Bona Fide Cooperative Member

Members are neither employees nor independent contractors — they are owner-operators of a cooperative enterprise who contribute labor as part of their membership obligation.

**Pros:**
- Most accurately reflects the intended relationship
- Members share in governance, profits, AND losses — true ownership
- Potentially avoids both employment law and independent contractor misclassification issues
- Recognized (to varying degrees) under federal tax law for cooperatives

**Cons:**
- Oregon law does not have a clear, bright-line "cooperative member" exemption from employment law
- Workers' compensation obligations are ambiguous for cooperative members in Oregon
- IRS treatment depends on entity type (ORS 62 cooperative vs. LLC)
- **Risk (HIGH):** Novelty of this classification in the construction context means regulatory challenge is possible

---

## 3. Oregon Legal Analysis

### ORS 670.600 — Independent Contractor Test

Oregon uses a multi-factor test to determine independent contractor status. The person must satisfy ALL of the following:

| Factor | IC Requirement | Co-op Member Analysis |
|--------|---------------|----------------------|
| (a) Free from direction and control | Worker controls manner and means of work | **MIXED** — Co-op project manager (Harlan) will direct work sequence, but members control trade-specific methods |
| (b) Customarily engaged in independent business | Worker has own business, clients, marketing | **LIKELY MET** — CCB-licensed tradespeople typically have independent businesses |
| (c) Responsible for own licenses | Worker obtains own business licenses | **MET** — Each member holds own CCB license |
| (d) Risk of profit or loss | Worker bears economic risk | **LIKELY MET** — Members share in co-op profits and losses |
| (e) Makes services available to general public | Worker is not exclusive to one client | **NEEDS ATTENTION** — Operating Agreement should not prohibit members from taking outside work |

### ORS Chapter 656 — Workers' Compensation

Under ORS 656.027, workers' compensation is mandatory for all "subject workers." A subject worker is defined broadly. However:

- **ORS 656.027(7)** — Corporate officers may elect exemption from coverage
- **ORS 656.029** — Members of an LLC may be exempt if they are not "subject workers" (i.e., not performing services for the LLC as employees)
- For a cooperative corporation under ORS 62, the analysis is less clear — member-workers of a cooperative may still be "subject workers" under ORS 656.005(30)

**My assessment:** This is the single highest-risk area. If a co-op member is injured on a job site and does not have workers' compensation coverage, the co-op faces potential liability under ORS 656.052 (noncomplying employer penalties) including:

1. Payment of all claim costs
2. Penalty of $250 per day of noncompliance (ORS 656.735)
3. Potential criminal misdemeanor (ORS 656.990)

### ORS Chapter 657 — Unemployment Insurance

Oregon Employment Department applies the ABC test for unemployment insurance:

- (A) Worker is free from control and direction
- (B) Service is performed outside the usual course of business OR outside all places of business
- (C) Worker is customarily engaged in an independently established trade or business

A co-op member performing construction work on co-op projects likely **fails prong (B)** — the work IS the co-op's usual course of business and is performed at the co-op's places of business (job sites).

**Risk (MEDIUM):** Oregon Employment Department may assert that members are subject to unemployment insurance, creating unexpected tax obligations for the co-op.

---

## 4. Recommended Structure

Based on this preliminary analysis, I recommend a **hybrid classification** approach:

### Structure: Independent Contractor-Members with Cooperative Governance

1. **Entity formation:** Form the co-op (entity type TBD pending M1) to hold property, manage projects, and distribute profits

2. **Member relationship:** Each member enters into a Member Agreement that establishes:
   - Membership in the co-op with full governance rights (voting, board eligibility)
   - Capital contribution obligation
   - Profit/loss sharing per Operating Agreement formula
   - **No employment relationship** — explicitly stated

3. **Work relationship:** For each project, the co-op (as general contractor, holding its own CCB license) enters into **subcontract agreements** with individual members (each holding their own CCB licenses) for specific scopes of work

4. **Insurance stack:**
   - Co-op carries: General liability ($1M/$2M), umbrella ($1M), property insurance on held properties
   - Each member carries: Own GL policy, own CCB bond, own workers' comp (if they have employees) or occupational accident insurance
   - **All members required to carry occupational accident insurance** as a gap-filler for workers' comp

5. **Workers' compensation strategy:**
   - If LLC structure: Members may be exempt under ORS 656.029 if properly structured
   - If ORS 62 cooperative: Obtain a workers' comp policy covering all member-workers during project work — this is the conservative and recommended approach
   - **In either case, I recommend obtaining workers' comp coverage** rather than relying on exemptions. The cost is modest compared to the liability exposure.

---

## 5. Federal Tax Classification Implications

| Entity Type | Member Tax Treatment | Self-Employment Tax | Payroll Tax |
|-------------|---------------------|-------------------|-------------|
| ORS 62 Cooperative | Patronage dividends (1099-PATR) | Yes, on patronage income | No (if not employees) |
| LLC (partnership) | Distributive share (K-1) | Yes, on distributive share | No (if not employees) |
| LLC (S-corp elect) | Reasonable salary (W-2) + distributions (K-1) | Only on salary portion | Yes, on salary portion |

**Note for Ledger:** The S-corp election for an LLC could reduce self-employment tax for members by allowing a portion of income to be classified as distributions rather than self-employment income. However, each member must receive a "reasonable salary" for services performed. This adds payroll complexity and requires the co-op to run payroll. Discuss with Ledger whether the tax savings justify the administrative burden.

---

## 6. Action Items

| # | Action | Owner | Depends On |
|---|--------|-------|------------|
| 1 | Finalize entity type selection | Statton | M1 outputs |
| 2 | Draft Operating Agreement with member classification provisions | Statton | Action #1 |
| 3 | Draft Member Agreement with IC provisions | Statton | Action #1 |
| 4 | Draft subcontract agreement template for project work | Statton | Action #1 |
| 5 | Obtain workers' comp quote for member coverage | Ledger | Action #1 |
| 6 | Determine optimal tax election (partnership vs. S-corp) | Ledger | Action #1 |
| 7 | Incorporate licensing requirements into recruitment criteria | Calloway | This memo (complete) |
| 8 | Review project management structure to preserve IC classification | Harlan | Action #2 |

---

## Limitations

This memorandum is a preliminary research document prepared as part of a simulation exercise. It is not legal advice. It does not create an attorney-client relationship. Worker classification is a fact-intensive inquiry that depends on the specific circumstances of the working relationship. Any real classification decisions should be made with the assistance of licensed Oregon employment law counsel.
