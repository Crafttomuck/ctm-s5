#!/usr/bin/env bash
set -euo pipefail

# Build server and/or client zips locally.
# Server zip copies jars from local Prism instance.
# Client zip uses packwiz curseforge export.
#
# Usage:
#   ./build-server.sh              # build both
#   ./build-server.sh --server     # server only
#   ./build-server.sh --client     # client only

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PACK_DIR="$SCRIPT_DIR/pack"
CONFIG="$SCRIPT_DIR/config.local.json"

build_server=true
build_client=true
if [ "${1:-}" = "--server" ]; then
    build_client=false
elif [ "${1:-}" = "--client" ]; then
    build_server=false
fi

ver=$(grep -E '^version\s*=' "$PACK_DIR/pack.toml" | sed -E 's/^version\s*=\s*"([^"]+)".*/\1/')
neoforge=$(grep -E '^neoforge\s*=' "$PACK_DIR/pack.toml" | sed -E 's/^neoforge\s*=\s*"([^"]+)".*/\1/')

# --- Client zip ---
if [ "$build_client" = true ]; then
    client_output="$SCRIPT_DIR/ctm-s5-client-${ver}.zip"
    echo "Building client zip..."
    (cd "$PACK_DIR" && packwiz curseforge export -s client -o "$client_output")

    # Workaround: packwiz doesn't write NeoForge into the CF manifest (packwiz#366)
    if [ -n "$neoforge" ]; then
        patch_dir=$(mktemp -d)
        unzip -q "$client_output" manifest.json -d "$patch_dir"
        jq --arg nf "neoforge-$neoforge" \
            '.minecraft.modLoaders = [{"id": $nf, "primary": true}]' \
            "$patch_dir/manifest.json" > "$patch_dir/manifest.patched.json"
        mv "$patch_dir/manifest.patched.json" "$patch_dir/manifest.json"
        (cd "$patch_dir" && zip -qr "$client_output" manifest.json)
        rm -rf "$patch_dir"
    fi

    echo "Client: $client_output"
    echo
fi

# --- Server zip ---
if [ "$build_server" = true ]; then
    if [ -f "$CONFIG" ]; then
        INSTANCE_DIR=$(jq -r '.local_prism_path' "$CONFIG")
    else
        echo "Error: config.local.json not found (needed for server build)" >&2
        echo "Create it with: {\"local_prism_path\": \"/path/to/minecraft\"}" >&2
        exit 1
    fi

    MODS_DIR="$INSTANCE_DIR/mods"

    if [ ! -d "$MODS_DIR" ]; then
        echo "Error: mods directory not found: $MODS_DIR" >&2
        exit 1
    fi

    server_output="$SCRIPT_DIR/ctm-s5-server-${ver}.zip"

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
    for dir in config defaultconfigs kubejs; do
        if [ -d "$PACK_DIR/$dir" ]; then
            cp -a "$PACK_DIR/$dir" "$tmpdir/"
        fi
    done

    # Copy servers.dat if present
    if [ -f "$PACK_DIR/servers.dat" ]; then
        cp "$PACK_DIR/servers.dat" "$tmpdir/"
    fi

    rm -f "$server_output"
    echo "Creating $server_output..."
    (cd "$tmpdir" && zip -qr "$server_output" .)

    echo "Server: $copied copied, $skipped client-only skipped, $missing missing"
    echo "Output: $server_output"
fi
