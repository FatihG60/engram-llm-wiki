#!/usr/bin/env bash
# One-command macOS / Linux installer for Engram + Karpathy LLM Wiki (Second Brain)
set -euo pipefail

BASE_DIR="${1:-$HOME/obsidian-brain}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENGINE_SCRIPT="$REPO_ROOT/src/engram.py"
MCP_SCRIPT="$REPO_ROOT/src/engram_mcp.py"
VAULT_PATH="$BASE_DIR/Brain"
DB_PATH="$BASE_DIR/engram.db"

echo "==> [1/3] Preparing Second Brain directory at: $BASE_DIR"
mkdir -p "$BASE_DIR"

if [ ! -d "$VAULT_PATH" ]; then
    echo "==> Copying starter Obsidian Vault template to: $VAULT_PATH"
    cp -R "$REPO_ROOT/vault-template" "$VAULT_PATH"
else
    echo "==> Existing Obsidian Vault found at $VAULT_PATH (preserved)."
fi

export ENGRAM_DB_PATH="$DB_PATH"
export OBSIDIAN_VAULT_PATH="$VAULT_PATH"

echo "==> [2/3] Running initial Delta Sync & FTS5 indexing..."
python3 "$ENGINE_SCRIPT" sync --sources obsidian

echo "==> [3/3] Running Karpathy LLM Wiki Health Check (lint)..."
python3 "$ENGINE_SCRIPT" lint --vault "$VAULT_PATH"

cat <<EOF

✅ Installation Complete!
Add the following alias to your ~/.zshrc or ~/.bashrc:
  export ENGRAM_DB_PATH="$DB_PATH"
  export OBSIDIAN_VAULT_PATH="$VAULT_PATH"
  alias engram='python3 "$ENGINE_SCRIPT"'

And add this MCP server block to your agent configuration:
{
  "mcpServers": {
    "engram": {
      "command": "python3",
      "args": ["$MCP_SCRIPT"],
      "env": {
        "ENGRAM_DB_PATH": "$DB_PATH",
        "OBSIDIAN_VAULT_PATH": "$VAULT_PATH"
      }
    }
  }
}
EOF
