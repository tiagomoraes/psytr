#!/usr/bin/env bash
set -euo pipefail

# sintr installer.
#
#   ./installers/install.sh <agent> [ledger-path]   install for one agent
#   ./installers/install.sh                          show detected agents (installs nothing)
#
# Supported <agent> values: hermes, claude-code, generic.
# Default ledger path: ~/sintr (override with the second argument or SINTR_LEDGER).

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SINTR_HOME="${SINTR_HOME:-$HOME/.sintr}"
SKILL_SRC="$REPO_DIR/skills/sintr"
TEMPLATE_SRC="$REPO_DIR/templates/sintr"

AGENT="${1:-}"
LEDGER_PATH="${2:-${SINTR_LEDGER:-$HOME/sintr}}"

if [ -z "$AGENT" ]; then
  echo "sintr — detected agents (this installs nothing):"
  if [ -d "${HERMES_HOME:-$HOME/.hermes}" ]; then
    echo "  hermes      -> ./installers/install.sh hermes      [ledger-path]"
  fi
  if [ -d "$HOME/.claude" ]; then
    echo "  claude-code -> ./installers/install.sh claude-code [ledger-path]"
  fi
  echo "  generic     -> ./installers/install.sh generic     [ledger-path]"
  exit 0
fi

copy_templates() {
  # Seed starter ledger files, skipping any that already exist. Never fails on
  # reinstall, and never overwrites the owner's data.
  ( cd "$TEMPLATE_SRC" && find . -type f -print ) | while IFS= read -r rel; do
    dest="$LEDGER_PATH/${rel#./}"
    if [ ! -e "$dest" ]; then
      mkdir -p "$(dirname "$dest")"
      cp "$TEMPLATE_SRC/$rel" "$dest"
    fi
  done
}

secure_ledger() {
  chmod 700 "$LEDGER_PATH" 2>/dev/null || true
  ( cd "$LEDGER_PATH" && find . -type d -exec chmod 700 {} + && find . -type f -exec chmod 600 {} + ) 2>/dev/null || true
}

install_skill() {
  local dest="$1"
  mkdir -p "$dest"
  cp -R "$SKILL_SRC/." "$dest/"
}

install_scripts() {
  # The weekly digest collector, installed for schedulers (cron, systemd, etc.).
  mkdir -p "$SINTR_HOME/bin"
  cp "$REPO_DIR/scripts/week_collect.py" "$SINTR_HOME/bin/week_collect.py"
  chmod 700 "$SINTR_HOME/bin/week_collect.py" 2>/dev/null || true
}

case "$AGENT" in
  hermes)
    install_skill "${HERMES_HOME:-$HOME/.hermes}/skills/sintr"
    copy_templates
    install_scripts
    ;;
  claude-code)
    install_skill "$HOME/.claude/skills/sintr"
    copy_templates
    install_scripts
    ;;
  generic)
    install_skill "$SINTR_HOME/skill"
    copy_templates
    install_scripts
    ;;
  *)
    echo "Unknown agent: $AGENT (supported: hermes, claude-code, generic)" >&2
    exit 2
    ;;
esac

secure_ledger
mkdir -p "$SINTR_HOME"
printf 'ledger_path=%s\n' "$LEDGER_PATH" > "$SINTR_HOME/config"
cp "$SKILL_SRC/SKILL.md" "$SINTR_HOME/sintr.md"
chmod 600 "$SINTR_HOME/config" "$SINTR_HOME/sintr.md" 2>/dev/null || true
echo "sintr installed for $AGENT."
echo "  ledger:    $LEDGER_PATH"
echo "  home:      $SINTR_HOME (config + canonical instruction copy)"
echo "  collector: $SINTR_HOME/bin/week_collect.py"
echo "Next: fill $(printf '%s' "$LEDGER_PATH")/config.md, then ask your agent for the sintr skill."
