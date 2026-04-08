# Portland Housing Co-op — Project Board

**Last updated:** 2026-04-08
**Phase:** M1 CLOSING → M2, M3, M4 ACTIVATING

---

## Milestones

| # | Milestone | Status | Owner(s) | Dependencies | Notes |
|---|-----------|--------|----------|--------------|-------|
| M1 | Co-op Vision & Strategy | CLOSING | Maven, Ledger | — | All decisions made; pending Ledger sign-off on financials |
| M2 | Legal Formation | READY | Statton, Maven | M1 | UNBLOCKED — Entity decision: Cooperative LLC. Statton to draft OA, Articles, Member Agreement |
| M3 | Financial Foundation | READY | Ledger, Maven | M1 | UNBLOCKED — Cap target $200K, profit split 20/10/30/40, 6 members |
| M4 | Member Recruitment | READY | Calloway, Maven | M1 | PARTIALLY UNBLOCKED — Pitch materials can be finalized; vetting can begin |
| M5 | Membership Agreements | BLOCKED | Statton, Ledger | M2, M3 | Waiting on legal structure and financial terms |
| M6 | First Property Search | BLOCKED | Reeves, Maven, Ledger | M2, M3 | Preliminary tools + data complete; waiting on entity + capitalization confirmation |
| M7 | Property Acquisition | BLOCKED | Reeves, Ledger, Statton | M6 | Waiting on property search results |
| M8 | Rehab Planning | BLOCKED | Harlan, Birch, Slate, Copper | M7 | Waiting on property acquisition |
| M9 | Renovation Execution | BLOCKED | Harlan, Birch, Slate, Copper | M8 | Waiting on rehab plan |
| M10 | Sale & Distribution | BLOCKED | Reeves, Ledger, Maven | M9 | Waiting on renovation completion |
| M11 | Retrospective & Scaling | BLOCKED | Maven, Ledger, all | M10 | Waiting on first flip completion |

## Active Agents

| Agent | Name | Role | Status |
|-------|------|------|--------|
| Maven | Founder | Orchestrator | ACTIVE — reviewing deliverables, making M1 decisions |
| Statton | Attorney | Legal Counsel | ACTIVE — M2 preliminary research complete |
| Reeves | Analyst | Real Estate | ACTIVE — M6 preliminary tools + data complete |
| Ledger | Accountant | CFO | ACTIVE — M1 financial deliverables complete |
| Calloway | Recruiter | Member Outreach | ACTIVE — M4 preliminary recruitment brief complete |
| Birch | Carpenter | Trades | NOT YET RECRUITED |
| Slate | Roofer | Trades | NOT YET RECRUITED |
| Copper | Plumber | Trades | NOT YET RECRUITED |

## Decisions Log

| Date | Decision | Made By | Rationale |
|------|----------|---------|-----------|
| 2026-04-07 | M1 activated; Maven drafts initial vision & strategy | Maven | Foundation for all downstream milestones |
| 2026-04-08 | Capitalization target: $200,000 (revised from $415K) | Maven | Ledger's model accounts for 85% LTV hard money leverage |
| 2026-04-08 | Founding member count: 6 | Maven | Minimum viable; faster to recruit and capitalize |
| 2026-04-08 | Entity structure: Cooperative LLC (ORS Ch. 63) | Maven | Flexibility of LLC + cooperative principles in Operating Agreement |
| 2026-04-08 | Profit split: 20% reserves, 10% overhead, 30% capital, 40% labor | Maven | 40% labor weighting is core value prop for trades recruitment |
| 2026-04-08 | Buy-in: 3-tier ($5K min, $50K max, no payment plans for founders) | Maven | Balance accessibility with capitalization speed |
| 2026-04-08 | Maven personal commitment: $50,000 (Tier A) | Maven | Founder leads from front |
| 2026-04-08 | Labor compensation: advance against share (up to 50% estimated) | Maven | Practical cash flow for members during rehab without blowing budget |
| 2026-04-08 | Governance: 1 member 1 vote, no founder privileges | Maven | Democratic from day one; trust earned not structured |
| 2026-04-08 | Target neighborhoods refined: Lents, Cully, Parkrose (Tier 1) | Maven | Per Reeves' scored analysis; Woodstock/Foster-Powell too expensive |
| 2026-04-08 | First flip timeline: purchase Month 4-5, sale Month 12-14 | Maven | Realistic given formation + capitalization lead time |
| 2026-04-08 | Minimum deal standards: ≤65% ARV, ≥15% ROI, ≤6mo hold | Maven | Per Ledger's sensitivity analysis — keeps us safe |
| 2026-04-08 | CCB licensing mandatory for entity + all members | Maven | Per Statton's research; no owner-builder exemption for flip-to-sell |
| 2026-04-08 | M2, M3, M4 UNBLOCKED | Maven | All M1 decisions made; agents assigned next-phase work |

## Blockers

| Blocker | Affects | Owner | Status |
|---------|---------|-------|--------|
| Ledger sign-off on final M1 parameters | M1 closure | Ledger | PENDING |
| M2 (entity formation) | M5, M6 | Statton | IN PROGRESS |
| M3 (financial foundation) | M5, M6 | Ledger | IN PROGRESS |

## Key Artifacts

| Document | Location | Author |
|----------|----------|--------|
| Vision & Strategy Draft v1 | workspace/deliverables/m01-vision/vision-strategy-draft-v1.md | Maven |
| M1 Decisions (Final) | workspace/deliverables/m01-vision/m1-decisions-maven.md | Maven |
| Capitalization Target | workspace/deliverables/m01-vision/capitalization-target.md | Ledger |
| Business Model | workspace/deliverables/m01-vision/business-model.md | Ledger |
| Operating Cost Model | workspace/deliverables/m01-vision/operating-cost-model.py | Ledger |
| Entity Comparison Research | workspace/deliverables/m02-legal/entity-comparison-research.md | Statton |
| CCB Licensing Requirements | workspace/deliverables/m02-legal/research/ccb-licensing-requirements.md | Statton |
| Worker Classification Analysis | workspace/deliverables/m02-legal/research/worker-classification-analysis.md | Statton |
| Market Overview | workspace/deliverables/m06-property-search/market-overview.md | Reeves |
| Neighborhood Scores | workspace/deliverables/m06-property-search/neighborhood-scores.md | Reeves |
| Candidate Properties | workspace/deliverables/m06-property-search/candidate-properties.md | Reeves |
| Recruitment Brief | workspace/deliverables/m04-recruitment/recruitment-brief.md | Calloway |
| Pitch Framework | workspace/deliverables/m04-recruitment/pitch-framework.md | Calloway |
| Deal Scorer Tool | tools/deal-scorer/ | Reeves |
| Comp Analyzer Tool | tools/comp-analyzer/ | Reeves |
| ARV Calculator Tool | tools/arv-calculator/ | Reeves |
