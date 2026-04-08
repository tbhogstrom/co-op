# Entity Structure Comparison — Preliminary Research

**Prepared by:** Statton, Legal Counsel
**Date:** 2026-04-07
**Status:** PRELIMINARY — Pending M1 Vision & Strategy outputs
**For:** Maven (Founder), Ledger (CFO)

---

## 1. Purpose

This memorandum provides preliminary legal research comparing three entity structures available under Oregon law for the Portland Housing Co-op. A final recommendation (to be issued as `entity-recommendation.md`) requires M1 outputs, specifically: (a) the co-op's mission statement and governance philosophy, (b) Ledger's capitalization target and profit-split model, and (c) Maven's decision on member count and growth trajectory.

This research is organized to allow Maven and Ledger to make informed decisions during M1 that account for downstream legal implications.

---

## 2. Entity Options Under Oregon Law

### Option A: Oregon Cooperative Corporation (ORS Chapter 62)

**Governing Statute:** ORS 62.005–62.455

#### Formation

- Filed with the Oregon Secretary of State, Corporation Division
- Requires Articles of Incorporation per ORS 62.055
- Minimum of three (3) incorporators required (ORS 62.045)
- Must include a statement of cooperative purpose in the Articles
- Filing fee: approximately $100 (Secretary of State schedule)

#### Governance

- **One member, one vote** — This is the defining feature. ORS 62.265 mandates that each member has one vote regardless of capital contribution. Voting may not be weighted by equity stake.
- Board of Directors required; minimum three (3) directors (ORS 62.185)
- Bylaws govern internal operations (ORS 62.075)
- Annual meetings required (ORS 62.155)
- Members may be expelled only for cause and with due process per bylaws (ORS 62.145)

#### Capital Structure

- Members may be required to make capital contributions (membership fees, equity purchases) per ORS 62.115
- Cooperative may issue membership certificates (ORS 62.105)
- **Patronage dividends**: Net savings (profits) are allocated based on patronage (labor contributed, transactions with the co-op), not capital invested (ORS 62.315). This is a critical distinction.
- Cooperative may retain a portion of net savings as reserves (ORS 62.325)

#### Taxation

- Oregon cooperative corporations are generally taxed as C corporations by default
- **However**: Subchapter T of the Internal Revenue Code (26 USC §§ 1381–1388) allows cooperatives to deduct patronage dividends from taxable income, effectively achieving pass-through treatment for distributed earnings
- Cooperatives must file IRS Form 1120-C
- Oregon follows federal treatment; no separate Oregon cooperative tax election required
- **Risk (MEDIUM):** If the co-op retains significant earnings (e.g., for property acquisition reserves), those retained earnings are taxed at the entity level. This may conflict with Ledger's capitalization strategy.

#### Advantages for This Project

1. Legal structure explicitly designed for member-owned, member-operated businesses
2. Democratic governance (one member, one vote) aligns with cooperative ethos
3. Patronage-based profit distribution aligns with a labor-equity model where tradespeople contribute sweat equity
4. Well-understood by Oregon regulators and lending institutions familiar with co-ops
5. Potential access to cooperative-specific financing (e.g., NCB, CoBank, CDFI lenders)

#### Disadvantages for This Project

1. **Rigid governance**: One-member-one-vote cannot be modified. If Maven or founding members want weighted voting during startup, this structure does not permit it.
2. **Patronage allocation complexity**: Defining "patronage" for a construction co-op (labor hours? project value? skill tier?) requires careful bylaw drafting. Ledger's profit-split formula must conform to Subchapter T rules.
3. **Limited investor capital**: Outside investors cannot receive returns proportional to investment — only patronage-based returns. This limits fundraising options.
4. **Dissolution complexity**: ORS 62.415–62.435 requires distribution of assets first to creditors, then to members based on patronage, then to other cooperatives or charitable purposes. Members cannot simply divide assets by ownership percentage.
5. **Minimum three incorporators**: Need at least three committed founding members before filing.

---

### Option B: Oregon Limited Liability Company (ORS Chapter 63)

**Governing Statute:** ORS 63.001–63.990

#### Formation

- Filed with the Oregon Secretary of State, Corporation Division
- Requires Articles of Organization per ORS 63.047
- Only one (1) organizer required (ORS 63.044)
- Filing fee: approximately $100 (Secretary of State schedule)
- Must designate a registered agent in Oregon (ORS 63.114)

#### Governance

- **Maximum flexibility** — Operating Agreement governs all internal affairs (ORS 63.130)
- Voting rights, profit allocation, management structure are all customizable
- Can be member-managed or manager-managed (ORS 63.130(8))
- No statutory requirement for annual meetings (though advisable in Operating Agreement)
- Members may be expelled per Operating Agreement terms (ORS 63.205)

#### Capital Structure

- Capital contributions defined by Operating Agreement — may include cash, property, services, or promissory notes (ORS 63.175)
- **Profit and loss allocation is fully customizable** — can be by capital account, by labor contribution, by equal share, or by any formula the members agree to
- Membership interests are assignable per Operating Agreement terms (ORS 63.249)
- No statutory requirement for patronage-based distribution

#### Taxation

- Default: pass-through taxation. Multi-member LLCs are taxed as partnerships (IRS Form 1065); single-member as disregarded entity
- **May elect** S-corp taxation (IRS Form 2553) or C-corp taxation (IRS Form 8832)
- Oregon pass-through entity tax (PTE-E) available under ORS 314.990 — allows entity-level deduction of state taxes, beneficial for members who itemize
- **Advantage**: No entity-level tax on retained earnings under default partnership treatment. All income flows through to members regardless of distribution.

#### Advantages for This Project

1. **Maximum structural flexibility**: Profit split can match any formula Ledger designs — hourly labor weighting, skill-tier multipliers, project-specific allocation, etc.
2. **Simple formation**: One organizer, no minimum member count to file
3. **Pass-through taxation by default**: No entity-level tax, even on retained earnings
4. **Flexible voting**: Can implement one-member-one-vote by agreement, or weighted voting, or supermajority requirements for major decisions — all customizable
5. **Familiar to lenders and contractors**: Banks, title companies, and the CCB all deal with LLCs daily
6. **Simpler dissolution**: Operating Agreement controls distribution on dissolution; no statutory mandate to distribute to other cooperatives

#### Disadvantages for This Project

1. **Not a "cooperative" by law**: Cannot use the word "cooperative" in the entity name (ORS 62.805(1)) unless formed under ORS Chapter 62. May use "co-op" informally but cannot register as a cooperative.
2. **No cooperative identity**: Does not qualify for cooperative-specific lending programs, technical assistance from cooperative development organizations, or membership in cooperative associations (e.g., NCBA CLUSA)
3. **Governance depends entirely on Operating Agreement quality**: If the Operating Agreement is poorly drafted, members have fewer statutory protections than under ORS Chapter 62
4. **Member departure complexity**: Buyout of departing member's interest must be carefully addressed in Operating Agreement — no statutory default that protects remaining members
5. **Self-employment tax**: Members who perform services for the LLC may owe self-employment tax on their distributive share (IRC § 1402(a)), which may be higher than employee-side payroll taxes

---

### Option C: Oregon Nonprofit Corporation (ORS Chapter 65)

**Governing Statute:** ORS 65.001–65.990

#### Formation

- Filed with the Oregon Secretary of State
- Requires Articles of Incorporation per ORS 65.047
- Minimum one (1) incorporator
- Must state a nonprofit purpose; may be mutual-benefit or public-benefit (ORS 65.044)

#### Governance

- Board of Directors required (ORS 65.304)
- Members (if any) have voting rights per Articles or Bylaws
- Can be structured as a membership corporation or a board-only corporation

#### Capital Structure

- **No equity ownership** — members do not own shares or equity interests
- **No profit distribution** — net revenues must be used to further the nonprofit's purpose (ORS 65.554)
- May charge membership dues
- May pay reasonable compensation for services

#### Taxation

- May apply for 501(c)(3) (charitable/educational), 501(c)(4) (social welfare), or 501(c)(12) (cooperative associations) tax-exempt status
- Oregon property tax exemptions may apply under ORS 307.130 (if charitable purpose)
- **However**: A house-flipping co-op generating profit for members almost certainly does NOT qualify for 501(c)(3) status. The IRS private inurement prohibition (IRC § 501(c)(3)) would apply.

#### Advantages for This Project

1. Potential tax exemptions (if qualifying purpose can be established)
2. Access to grant funding and charitable donations
3. Community credibility and public trust

#### Disadvantages for This Project

1. **FATAL FLAW: No profit distribution.** The entire business model of this co-op is to flip houses and distribute profit to members. A nonprofit cannot do this. Period.
2. Members cannot build equity through a nonprofit structure
3. Even a 501(c)(12) cooperative association exemption is unlikely for a house-flipping operation — designed for utilities, telephone co-ops, etc.
4. Extremely complex compliance (annual filings, governance requirements, use-of-funds restrictions)

#### Assessment

**I do not recommend a nonprofit structure for this project.** The fundamental purpose — generating profit through real estate renovation and distributing that profit to member-tradespeople — is incompatible with nonprofit law. I include this option for completeness and to foreclose the question early.

---

## 3. Hybrid Approach: "Cooperative LLC"

There is a fourth option that merits discussion: structuring an LLC under ORS Chapter 63 but drafting the Operating Agreement to incorporate cooperative principles.

#### Concept

- Form as an Oregon LLC
- Operating Agreement includes:
  - One member, one vote (by agreement, not statute)
  - Patronage-based profit allocation (by agreement, not statute)
  - Member admission and expulsion procedures modeled on ORS Chapter 62
  - Reserve requirements and dissolution provisions similar to cooperative statutes
- Optionally elect Subchapter T tax treatment if qualifying (IRS revenue rulings suggest LLCs operating on a cooperative basis may elect Subchapter T, though this area of law is not fully settled)

#### Advantages

1. Flexibility of an LLC with cooperative governance principles
2. Pass-through taxation with optional Subchapter T election
3. Can be structured to qualify for cooperative lending (some CDFIs accept cooperative LLCs)
4. Members get statutory LLC protections AND contractual cooperative protections

#### Disadvantages / Risks

1. **Risk (MEDIUM):** Subchapter T eligibility for LLCs is based on IRS rulings and case law, not explicit statutory authorization. A conservative position would not rely on this election.
2. **Risk (LOW):** Cannot use "cooperative" in entity name per ORS 62.805(1). Must use alternative branding.
3. Requires a more complex Operating Agreement (higher drafting cost, but I'm here for that)
4. Members may not fully understand that they're in an LLC, not a statutory cooperative — requires education

---

## 4. Preliminary Decision Matrix

| Factor | ORS 62 Cooperative | ORS 63 LLC | ORS 65 Nonprofit | Cooperative LLC |
|--------|-------------------|------------|-------------------|-----------------|
| Profit distribution | Patronage only | Any formula | **Prohibited** | Any formula (can mirror patronage) |
| Governance flexibility | Low (statutory) | High | Medium | High |
| Pass-through taxation | Only via Sub T | Default | N/A (exempt) | Default + optional Sub T |
| Formation complexity | Medium | Low | High | Low (formation) / Medium (Operating Agreement) |
| Cooperative identity | Full | None | None | Partial |
| Cooperative lending access | Yes | No | Possibly | Possibly |
| Minimum founders to file | 3 | 1 | 1 | 1 |
| CCB compatibility | Compatible | Compatible | Unusual | Compatible |
| Lender familiarity | Medium | High | Low | High |
| Member equity building | Limited | Full flexibility | None | Full flexibility |
| Dissolution control | Statutory limits | Full flexibility | Statutory limits | Full flexibility |
| **Overall fit for house-flipping co-op** | **Good** | **Good** | **Poor** | **Very Good** |

---

## 5. Open Questions for M1

The following questions must be answered by Maven and Ledger before I can issue a final recommendation:

### For Maven (Vision & Governance)

1. **Governance philosophy**: Does the co-op require strict one-member-one-vote, or should founding members have additional voting weight during the startup phase (M1–M5)?
2. **Cooperative identity**: How important is it to be a legally recognized cooperative? Does the co-op plan to seek cooperative-specific funding or join cooperative associations?
3. **Growth trajectory**: Is the target 5–8 members for the first flip, scaling to 15–20? Or a smaller, tighter operation?
4. **Decision-making**: Majority vote? Supermajority for major decisions (property acquisition, new members, dissolution)?
5. **Founding member protections**: Should founding members have special rights (e.g., veto power, preferred returns) that sunset after the first flip?

### For Ledger (Financial & Tax)

6. **Profit-split model**: Is the profit split based purely on labor hours, or does it include a capital-contribution component? Does it include a skill-tier multiplier?
7. **Capitalization target**: What is the total capital needed for the first flip? How is it raised — member contributions, loans, or both?
8. **Reserve policy**: What percentage of net profit will be retained by the entity vs. distributed? This affects entity-level taxation under ORS Chapter 62.
9. **Tax strategy**: Does Ledger prefer default partnership pass-through, or is there a reason to consider S-corp or Subchapter T election?
10. **Member buyout**: When a member departs, how is their interest valued? Book value? Appraised value? Formula-based?

### For Both

11. **Timeline**: When does the co-op need to be a legal entity? Property acquisition (M7) requires it. Recruitment (M4) is better with it. What's the earliest realistic filing date?

---

## 6. Preliminary Risk Register

| # | Risk | Severity | Likelihood | Entity Affected | Mitigation |
|---|------|----------|------------|-----------------|------------|
| R1 | Members classified as employees, not co-op members, by Oregon Employment Department | HIGH | MEDIUM | All | Structure Operating Agreement to establish bona fide member relationship; ensure members have governance rights, capital accounts, and share in profits/losses. See ORS 670.600 (independent contractor factors). |
| R2 | CCB licensing gaps — co-op performs work without valid license | HIGH | MEDIUM | All | Operating Agreement must require active CCB license as condition of membership; co-op entity must also hold CCB license if it contracts directly with property owners. See ORS 701.005–701.992. |
| R3 | Subchapter T election denied by IRS for LLC structure | MEDIUM | LOW | Cooperative LLC | If Sub T treatment is desired, consider forming under ORS 62 instead. Alternatively, draft Operating Agreement to satisfy cooperative principles under Rev. Rul. 72-602. |
| R4 | Member departure triggers entity dissolution or buyout crisis | MEDIUM | MEDIUM | All | Operating Agreement must include mandatory buyout provisions, valuation formula, and payment terms. Consider life insurance/disability provisions. |
| R5 | Retained earnings taxed at entity level under ORS 62 | MEDIUM | HIGH | ORS 62 Coop | Plan reserve policy with Ledger to minimize entity-level taxation; maximize qualified patronage dividend distributions. |
| R6 | General liability claim from renovation work exceeds insurance | HIGH | LOW | All | Require minimum GL coverage ($1M/$2M), umbrella policy, and workers comp. Each member must carry own professional liability. |
| R7 | Real property held in co-op name creates transfer tax and title issues | LOW | LOW | ORS 62 Coop | Standard practice in Oregon; no transfer tax. Title insurance available for cooperative-held property. |

---

## 7. Next Steps

Upon completion of M1 deliverables:

1. **Statton** will issue `entity-recommendation.md` with a final recommendation and rationale
2. **Statton** will draft `articles-of-incorporation.md` for the selected entity type
3. **Statton** will draft `operating-agreement.md` incorporating Ledger's profit-split formula
4. **Statton** will draft `bylaws.md` (if ORS 62 cooperative) or governance provisions within the Operating Agreement (if LLC)

**Estimated drafting time once M1 is complete:** 2–3 working sessions for all M2 deliverables.

---

## Limitations

This memorandum is a preliminary research document prepared as part of a simulation exercise. It is not legal advice. It does not create an attorney-client relationship. Any real entity formation should be reviewed by a licensed Oregon attorney. Oregon Revised Statutes cited herein are referenced for educational purposes and should be verified against current law at the time of filing.
