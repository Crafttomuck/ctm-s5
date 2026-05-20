#!/usr/bin/env bash
set -euo pipefail

# Build a server zip from a local Prism Launcher instance.
# Copies jars directly — no CurseForge API key needed.
#
# Usage:
#   ./build-server.sh [path-to-minecraft-dir]
#
# Defaults to the CTMS5 Prism instance if no path given.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PACK_DIR="$SCRIPT_DIR/pack"
CONFIG="$SCRIPT_DIR/config.local.json"

if [ -n "${1:-}" ]; then
    INSTANCE_DIR="$1"
elif [ -f "$CONFIG" ]; then
    INSTANCE_DIR=$(jq -r '.local_prism_path' "$CONFIG")
else
    echo "Error: no instance path given and config.local.json not found" >&2
    echo "Usage: ./build-server.sh [path-to-minecraft-dir]" >&2
    echo "Or create config.local.json with: {\"local_prism_path\": \"/path/to/minecraft\"}" >&2
    exit 1
fi

MODS_DIR="$INSTANCE_DIR/mods"

if [ ! -d "$MODS_DIR" ]; then
    echo "Error: mods directory not found: $MODS_DIR" >&2
    exit 1
fi

ver=$(grep -E '^version\s*=' "$PACK_DIR/pack.toml" | sed -E 's/^version\s*=\s*"([^"]+)".*/\1/')
output="$SCRIPT_DIR/ctm-s5-server-${ver}.zip"

tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT
mkdir -p "$tmpdir/mods"

# Read each .pw.toml — skip client-only mods, copy the rest from local instance
copied=0
skipped=0
missing=0
for toml in "$PACK_DIR"/mods/*.pw.toml; do
    side=$(grep -E '^side\s*=' "$toml" | sed -E 's/^side\s*=\s*"([^"]+)".*/\1/')
    if [ "$side" = "client" ]; then
        skipped=$((skipped + 1))
        continue
    fi

    filename=$(grep -E '^filename\s*=' "$toml" | sed -E 's/^filename\s*=\s*"([^"]+)".*/\1/')
    if [ -z "$filename" ]; then
        continue
    fi

    if [ -f "$MODS_DIR/$filename" ]; then
        cp "$MODS_DIR/$filename" "$tmpdir/mods/"
        copied=$((copied + 1))
    else
        echo "Warning: missing jar: $filename" >&2
        missing=$((missing + 1))
    fi
done

# Copy overrides (configs, kubejs, etc.)
if [ -d "$PACK_DIR/config" ]; then
    cp -a "$PACK_DIR/config" "$tmpdir/"
fi
if [ -d "$PACK_DIR/defaultconfigs" ]; then
    cp -a "$PACK_DIR/defaultconfigs" "$tmpdir/"
fi
if [ -d "$PACK_DIR/kubejs" ]; then
    cp -a "$PACK_DIR/kubejs" "$tmpdir/"
fi

# Copy servers.dat if present
if [ -f "$PACK_DIR/servers.dat" ]; then
    cp "$PACK_DIR/servers.dat" "$tmpdir/"
fi

echo "Creating $output..."
(cd "$tmpdir" && zip -qr "$output" .)

echo "Done: $copied copied, $skipped client-only skipped, $missing missing"
echo "Output: $output"
