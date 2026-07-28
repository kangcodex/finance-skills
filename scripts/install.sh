#!/usr/bin/env bash
# One-shot install for the private weather-trading runtime + skills.
#
# This public repo only ships the SKILL.md files. The deterministic math
# + I/O (sizing, signal blend, halt matrix, wallet setup, orders,
# adapters) lives in a separate PRIVATE repo and is fetched by this
# script. We do not embed the runtime URL in this file because the
# private location may change without notice and the public repo
# should not leak the location.
#
# Configuration:
#   RUNTIME_REPO    GitHub org/repo of the private runtime (default: kangcodex/weather-runtime)
#   RUNTIME_REF     git ref to fetch (default: main)
#   INSTALL_DIR     install path (default: ./weather-agent)
#
# Usage:
#   ./install.sh
#   INSTALL_DIR=/opt/agent ./install.sh
#   RUNTIME_REF=v1.2.3 ./install.sh
#
# Re-run safely: refuses to overwrite a non-empty directory.

set -euo pipefail

INSTALL_DIR="${INSTALL_DIR:-./weather-agent}"
RUNTIME_REPO="${RUNTIME_REPO:-kangcodex/weather-runtime}"
RUNTIME_REF="${RUNTIME_REF:-main}"
RUNTIME_TARBALL="https://github.com/${RUNTIME_REPO}/archive/refs/heads/${RUNTIME_REF}.tar.gz"

if [ -e "$INSTALL_DIR" ] && [ -n "$(ls -A "$INSTALL_DIR" 2>/dev/null || true)" ]; then
  echo "ERROR: $INSTALL_DIR exists and is not empty. Pass INSTALL_DIR=... or remove it first." >&2
  exit 1
fi

command -v uv >/dev/null 2>&1 || {
  echo "ERROR: 'uv' not installed. Install: https://docs.astral.sh/uv/getting-started/installation/" >&2
  exit 1
}

echo "==> Creating $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

echo "==> Fetching private runtime from $RUNTIME_REPO@$RUNTIME_REF"
curl -fsSL "$RUNTIME_TARBALL" \
  | tar -xz --strip=1 -C "$INSTALL_DIR"

echo "==> Installing weather_runtime (uv sync + editable install)"
cd "$INSTALL_DIR"
uv sync
uv pip install -e .

if [ ! -f .env ]; then
  echo "==> Creating .env from .env.example"
  cp .env.example .env
  echo "    Edit .env before you start the agent."
fi

cat <<'NEXT'

==> Done. Next steps:

  1. Edit your environment:
       $EDITOR .env

  2. Run the test suite to confirm everything works:
       uv run pytest          # ~201 tests, <1s

  3. Install the 5 weather-trading skills into your agent (OpenCode, Claude
     Code, Codex, Cursor, etc.):
       npx skills add https://github.com/kangcodex/finance-skills/tree/main/skills/polymarket-wallet-setup
       npx skills add https://github.com/kangcodex/finance-skills/tree/main/skills/weather-data-fetch
       npx skills add https://github.com/kangcodex/finance-skills/tree/main/skills/signal-gen
       npx skills add https://github.com/kangcodex/finance-skills/tree/main/skills/risk-manage
       npx skills add https://github.com/kangcodex/finance-skills/tree/main/skills/trade-execute

     Or grab all 5 at once:
       npx skills add kangcodex/finance-skills --skill polymarket-wallet-setup
       npx skills add kangcodex/finance-skills --skill weather-data-fetch
       npx skills add kangcodex/finance-skills --skill signal-gen
       npx skills add kangcodex/finance-skills --skill risk-manage
       npx skills add kangcodex/finance-skills --skill trade-execute

  4. In your agent, prompt: "set me up on Amoy".
     The agent reads the polymarket-wallet-setup skill and walks you through
     the wallet + CLOB auth + test order in under 2 minutes.

  5. After the wallet is up, the per-tick loop runs every hour (or on
     event-driven triggers): weather-data-fetch -> signal-gen -> risk-manage
     -> trade-execute. The agent drives this loop from the skill workflows.

NEXT
