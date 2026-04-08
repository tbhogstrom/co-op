# Portland House-Flipping Co-op — Scion Multi-Agent Simulation

## Overview

A Scion-based multi-agent simulation that models the founding and operation of a cooperative that buys derelict houses in Portland, OR, repairs them with licensed and bonded co-op member tradespeople, and splits profits among owners and contributors based on real time invested. The simulation uses 9+ agents (all Claude harness) running concurrently in Docker containers via WSL2, producing real, usable deliverables — legal documents, financial models, analysis tools, project plans, and long-term business strategy.

**Primary purpose:** Scion stress test — exercising multi-agent coordination, concurrent work, file-based handoffs, messaging, sub-agent spawning, and leadership transitions across a complex, real-world-grounded scenario.

## Agent Roster

### Core Leadership (persistent, launched at startup)

| Agent | Name | Role | Responsibilities |
|-------|------|------|-----------------|
| Founder | **Maven** | Orchestrator → Co-op Chair | Drives vision, sets milestones, coordinates all agents. Transitions from director to facilitator once co-op is established. Maintains the shared project board. |
| Attorney | **Statton** | Legal Counsel | Oregon co-op law, articles of incorporation, operating agreement, bylaws, membership agreements, contractor licensing compliance, liability/insurance guidance. Cites ORS Chapter 62 (cooperatives) and ORS Chapter 63 (LLCs). |
| Analyst | **Reeves** | Real Estate Analyst | Property sourcing, comp analysis, ARV calculations, neighborhood scoring, deal pipeline, market trend reports. Builds analysis scripts using real public data + synthetic fills. |
| GC/Estimator | **Harlan** | General Contractor | Scopes of work, rehab budgets, scheduling, permit requirements, trade coordination, inspection checklists, quality standards. Licensed Oregon GC. |
| Accountant | **Ledger** | CFO | Capitalization plans, project P&L, profit-split formulas, tax implications, cash flow projections, 5-year business plan, break-even analysis. |
| Recruiter | **Calloway** | Member Recruiter | Member vetting criteria, skills matrix, application templates, outreach materials, pitch deck, onboarding process. |

### Tradespeople (persistent, launched mid-simulation after recruitment)

| Agent | Name | Trade | Focus |
|-------|------|-------|-------|
| Carpenter | **Birch** | Carpentry | Framing, finish carpentry, cabinetry, structural repair estimates. 12 years experience, union trained. Estimates by the board foot. |
| Roofer | **Slate** | Roofing | Roof assessment, tear-off/re-roof scoping, weather considerations. PNW specialist. Estimates by the square. |
| Plumber | **Copper** | Plumbing | Plumbing assessment, re-pipe scoping, fixture specs, code compliance. Oregon licensed master plumber. Knows Portland's old galvanized/cast iron problems. |

### Ephemeral (spawned on demand)

Any agent can spawn sub-agents for focused subtasks. Examples: permit researcher, title searcher, neighborhood scout, materials pricer, inspector. Created as needed, dismissed after task completion.

## Agent Persona Design

Each agent template contains:

1. **Identity** — Name, role, professional background
2. **Expertise** — Specific domain knowledge (Oregon law, Portland market, trade specialization)
3. **Working style** — How they approach problems, what they prioritize
4. **Output standards** — Format expectations for their deliverables (real docs, not summaries)
5. **Collaboration rules** — How they interact with other agents, when to message vs. write files
6. **Spawn authority** — When and what kind of sub-agents they can create

### Key Design Principle

Agents disagree productively. Harlan pushes back on Reeves if a deal looks too thin on rehab budget. Statton flags legal risks that Maven wants to gloss over. Ledger rejects deals that don't pencil. This tension produces better artifacts.

## Coordination Model: Event-Driven Milestones

### Leadership Transition

- **Phases M1–M5:** Maven orchestrates directly — assigns work, reviews output, resolves conflicts
- **Phases M6+:** Maven transitions to facilitator. Decision-making moves to consensus via agent messaging. Tradespeople join and participate as equals.

### Milestone Structure

| # | Milestone | Key Agents | Deliverables | Dependencies |
|---|-----------|-----------|--------------|--------------|
| M1 | Co-op Vision & Strategy | Maven, Ledger | Mission statement, business model canvas, initial capitalization target | — |
| M2 | Legal Formation | Statton, Maven | Articles of incorporation, operating agreement, bylaws (Oregon-specific), LLC/co-op entity selection | M1 |
| M3 | Financial Foundation | Ledger, Maven | Capital structure, member buy-in model, profit-split formula, break-even analysis, banking setup | M1 |
| M4 | Member Recruitment | Calloway, Maven | Application template, skills matrix, vetting criteria, pitch deck, recruitment outreach plan | M1 |
| M5 | Membership Agreements | Statton, Ledger | Member contracts, liability waivers, insurance requirements, licensing verification process | M2, M3 |
| M6 | First Property Search | Reeves, Maven, Ledger | Market analysis scripts, neighborhood scoring model, deal pipeline with 3-5 candidate properties | M2, M3 |
| M7 | Property Acquisition | Reeves, Ledger, Statton | Selected property, comp analysis, ARV estimate, purchase financial model, title/lien review | M6 |
| M8 | Rehab Planning | Harlan, Birch, Slate, Copper | Full scope of work, trade-specific estimates, materials list, schedule/Gantt, permit checklist | M7 |
| M9 | Renovation Execution | Harlan, Birch, Slate, Copper | Daily logs, change orders, inspection reports, budget tracking, quality checklists | M8 |
| M10 | Sale & Distribution | Reeves, Ledger, Maven | Listing strategy, closing projections, actual P&L, profit distribution calc, member payouts | M9 |
| M11 | Retrospective & Scaling | Maven, Ledger, all | Lessons learned, process improvements, 5-year growth plan, multi-property pipeline strategy, reinvestment model, succession/exit planning | M10 |

### Coordination Mechanics

- **Project board** — Maven maintains `workspace/project-board.md` tracking milestone status, blockers, and ownership
- **Agent messaging** — Agents use `scion` CLI to send direct messages and party-wide broadcasts
- **File-based handoffs** — Deliverables go in `workspace/deliverables/<milestone>/`, agents read each other's output
- **Dependency gates** — An agent checks the project board before starting work; if dependencies aren't met, it works on prep or spawns a sub-agent for research

## Workspace & File Structure

```
co-op/
├── .scion/
│   ├── settings.yaml
│   └── templates/
│       ├── maven/
│       │   ├── scion-agent.yaml
│       │   ├── system-prompt.md
│       │   ├── agents.md
│       │   └── home/
│       ├── statton/
│       ├── reeves/
│       ├── harlan/
│       ├── ledger/
│       ├── calloway/
│       ├── birch/
│       ├── slate/
│       └── copper/
│
├── workspace/
│   ├── project-board.md
│   ├── comms/
│   └── deliverables/
│       ├── m01-vision/
│       ├── m02-legal/
│       ├── m03-financial/
│       ├── m04-recruitment/
│       ├── m05-membership/
│       ├── m06-property-search/
│       ├── m07-acquisition/
│       ├── m08-rehab-planning/
│       ├── m09-renovation/
│       ├── m10-sale/
│       └── m11-scaling/
│
├── tools/
│   ├── comp-analyzer/
│   ├── arv-calculator/
│   ├── deal-scorer/
│   ├── profit-splitter/
│   └── rehab-estimator/
│
└── data/
    ├── portland-neighborhoods/
    ├── property-listings/
    └── member-registry/
```

## Deliverable Standards

### Legal Documents
- Full-text drafts citing Oregon Revised Statutes (ORS Chapter 62 for cooperatives, ORS Chapter 63 for LLCs)
- Proper legal formatting with numbered sections, definitions, signature blocks
- Oregon-specific requirements (registered agent, annual report obligations, CCB licensing)

### Financial Models
- Python scripts or spreadsheet-compatible formats (CSV with formulas documented)
- Actual calculations, not descriptions of calculations
- Inputs clearly separated from outputs — designed to be re-run with different numbers
- Profit-split calculator handles: member equity shares, hours worked by trade, overhead allocation, reserve fund contributions

### Analysis Tools
- Working Python scripts in `tools/` directory
- Real data integrations where feasible: Multnomah/Washington/Clackamas county assessor data, PortlandMaps.com, Oregon CCB license lookup
- Synthetic data generators for paywalled sources (Zillow, MLS) that produce realistic Portland numbers
- Each tool has a README, CLI interface, and example output

### Project Management
- Gantt charts as Mermaid diagrams or CSV timelines
- Scopes of work with line-item detail (CSI format where applicable)
- Inspection checklists specific to Portland code requirements

### Recruitment Materials
- Pitch deck as Markdown (convertible to slides)
- Member application with skills inventory, licensing verification, references
- Co-op culture document and decision-making framework

### Long-term Planning
- 5-year pro forma with scenario modeling (conservative/moderate/aggressive)
- Multi-property pipeline strategy with reinvestment waterfall
- Succession and exit planning for members

## Simulation Lifecycle

### Startup Sequence
1. Maven launches first — reads the project board template, initializes milestone tracking, sets M1 as active
2. Maven spawns core leadership — Statton, Reeves, Ledger, Calloway via `scion start`
3. Agents discover each other — each agent uses `scion list` to find peers, introduces themselves via messaging
4. Concurrent work begins — Maven assigns M1, but agents can start prep work on their own milestones

### Steady State
- Agents check the project board for milestone status and dependencies
- When a milestone's dependencies are met, agents with ownership start producing deliverables
- Agents message each other for input, reviews, and handoffs
- Any agent can spawn ephemeral sub-agents for focused research tasks
- Maven updates the project board as milestones complete

### Founder Transition (after M5)
- Maven shifts from directing to facilitating
- Decision-making moves to consensus — agents discuss and vote via messaging
- Maven still maintains the project board but doesn't unilaterally assign work

### Tradesperson Entry
- Birch, Slate, Copper aren't launched at startup — they're "recruited"
- Calloway produces member profiles, Maven approves, then those agents are started via `scion start`
- They arrive with their personas already set, read existing deliverables to get up to speed
- They become active contributors starting at M8 (rehab planning)

### Completion
- After M11, Maven produces a final summary and all agents write their retrospective notes
- All deliverables are committed to the repo

## Technical Requirements

- **Scion** built from source (Go 1.22+)
- **Container runtime:** Docker via WSL2
- **Git >= 2.47.0** for worktree support
- **LLM provider:** Anthropic (Claude) — all agents use the `claude` harness
- **Auth:** Claude Code Max OAuth via volume mount. The host's `~/.claude` directory is mounted into each agent container at `/home/scion/.claude` (read-write), giving Claude Code inside the container access to the OAuth credentials and token refresh.
- **Python 3.10+** for analysis tools and financial models
