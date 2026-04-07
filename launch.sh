#!/usr/bin/env bash
set -euo pipefail

# Portland Housing Co-op — Scion Simulation Launcher
# This script initializes the Scion grove and starts Maven (the Founder agent).
# Maven will then start the remaining agents according to the simulation plan.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Portland Housing Co-op — Scion Simulation ==="
echo ""

# Check prerequisites
command -v scion >/dev/null 2>&1 || { echo "ERROR: scion CLI not found. Install with: go install github.com/GoogleCloudPlatform/scion/cmd/scion@latest"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "ERROR: docker not found. Ensure Docker is running in WSL2."; exit 1; }
command -v git >/dev/null 2>&1 || { echo "ERROR: git not found."; exit 1; }

# Check git version (need >= 2.47.0 for worktree relative paths)
GIT_VERSION=$(git --version | grep -oP '\d+\.\d+\.\d+')
echo "Git version: $GIT_VERSION"

# Check Docker is running
docker info >/dev/null 2>&1 || { echo "ERROR: Docker is not running. Start Docker Desktop or the Docker daemon in WSL2."; exit 1; }
echo "Docker: running"

# Initialize Scion grove if not already initialized
if [ ! -f ".scion/grove.yaml" ]; then
    echo "Initializing Scion grove..."
    scion init --non-interactive
fi

echo ""
echo "Starting Maven (Founder agent)..."
echo "Maven will bootstrap the co-op by starting the remaining agents."
echo ""

# Start Maven — the orchestrator
scion start maven \
    --type maven \
    --non-interactive \
    --attach \
    "You are Maven, founder of the Portland Housing Co-op. Begin the simulation:
1. Read workspace/project-board.md
2. Set M1 (Co-op Vision & Strategy) as ACTIVE
3. Start the core leadership agents (Statton, Reeves, Ledger, Calloway)
4. Begin working on M1 with Ledger
Follow your operational instructions in agents.md."
