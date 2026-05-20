#!/usr/bin/env bash
# Sync the packwiz pack to match prism-export.json.
# Usage: ./update-packwiz.sh
#
# Wipes all existing mod definitions and re-adds every mod from
# prism-export.json via packwiz, so the pack always matches the export.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
EXPORT_FILE="$SCRIPT_DIR/prism-export.json"
PACK_DIR="$SCRIPT_DIR/pack"
MODS_DIR="$PACK_DIR/mods"

if [[ ! -f "$EXPORT_FILE" ]]; then
  echo "Error: $EXPORT_FILE not found" >&2
  exit 1
fi

# Extract CurseForge project IDs and names
mapfile -t entries < <(
  jq -r '.[] | select(.url? // "" | test("curseforge\\.com/projects/")) |
    "\(.url | capture("projects/(?<id>[0-9]+)").id)\t\(.name)"' "$EXPORT_FILE"
)

if [[ ${#entries[@]} -eq 0 ]]; then
  echo "Error: no CurseForge mods found in $EXPORT_FILE" >&2
  exit 1
fi

# Wipe existing mod definitions
echo "Clearing existing mod definitions..."
rm -f "$MODS_DIR"/*.pw.toml
echo

cd "$PACK_DIR"

total=${#entries[@]}
echo "Adding $total mods from CurseForge..."
echo

failed=()
added=0

for entry in "${entries[@]}"; do
  project_id="${entry%%	*}"
  name="${entry#*	}"
  i=$((added + ${#failed[@]} + 1))

  echo "[$i/$total] $name (project $project_id)"

  if packwiz -y curseforge add --addon-id "$project_id" 2>&1; then
    ((added++))
  else
    echo "  !! FAILED: $name (project $project_id)"
    failed+=("$name (project $project_id)")
  fi
  echo
done

# Rebuild index to ensure consistency
packwiz refresh

echo "========================================="
echo "Done: $added added, ${#failed[@]} failed, $total total"

if [[ ${#failed[@]} -gt 0 ]]; then
  echo
  echo "Failed mods:"
  for f in "${failed[@]}"; do
    echo "  - $f"
  done
fi
