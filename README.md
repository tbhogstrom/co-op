# Portland Housing Co-op — Scion Multi-Agent Simulation

A multi-agent simulation using [Scion](https://github.com/GoogleCloudPlatform/scion) that models the founding and operation of a housing cooperative in Portland, Oregon. Nine AI agents collaborate to produce real deliverables: legal documents, financial models, analysis tools, project plans, and long-term business strategy.

## Agents

| Name | Role | Model |
|------|------|-------|
| **Maven** | Founder / Orchestrator | Claude Opus |
| **Statton** | Attorney | Claude Opus |
| **Reeves** | Real Estate Analyst | Claude Opus |
| **Harlan** | General Contractor | Claude Opus |
| **Ledger** | Accountant / CFO | Claude Opus |
| **Calloway** | Recruiter | Claude Sonnet |
| **Birch** | Carpenter | Claude Sonnet |
| **Slate** | Roofer | Claude Sonnet |
| **Copper** | Plumber | Claude Sonnet |

## Prerequisites

- [Scion](https://github.com/GoogleCloudPlatform/scion) (`go install github.com/GoogleCloudPlatform/scion/cmd/scion@latest`)
- Docker (via WSL2)
- Git >= 2.47.0
- Claude Code Max subscription (OAuth token)
- Scion container images built and available

## Quick Start

```bash
# 1. Clone this repo
git clone <repo-url> co-op && cd co-op

# 2. Ensure Docker is running in WSL2

# 3. Launch the simulation
./launch.sh
```

Maven will start first, then spawn the remaining agents. Monitor with:

```bash
scion list                  # See active agents
scion look <agent-name>     # Check agent's current output
scion attach <agent-name>   # Attach to agent session
scion logs <agent-name>     # View agent logs
```

## Milestones

1. **Co-op Vision & Strategy** — Mission, business model, capitalization target
2. **Legal Formation** — Articles of incorporation, operating agreement, bylaws
3. **Financial Foundation** — Capital structure, profit-split formula, break-even
4. **Member Recruitment** — Applications, pitch deck, candidate vetting
5. **Membership Agreements** — Member contracts, insurance, licensing verification
6. **First Property Search** — Market analysis tools, neighborhood scoring, deal pipeline
7. **Property Acquisition** — Comp analysis, ARV, purchase financial model
8. **Rehab Planning** — Scope of work, trade estimates, schedule, permits
9. **Renovation Execution** — Daily logs, budget tracking, inspections
10. **Sale & Distribution** — Listing, P&L, profit distribution
11. **Retrospective & Scaling** — 5-year plan, pipeline strategy, reinvestment

## Deliverables

All agent output goes to `workspace/deliverables/<milestone>/`. Analysis tools go to `tools/`. See the [design spec](docs/superpowers/specs/2026-04-07-co-op-scion-simulation-design.md) for full details.
