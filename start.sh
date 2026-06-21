#!/usr/bin/env sh
set -e

cd "$(dirname "$0")"

VERSION="1.0.5"
VERSION_FILE=".ctm-s5-version"

NEOFORGE_VERSION="21.1.233"
NEOFORGE_VERSION_FILE=".neoforge-version"

download() {
    url="$1"
    out="$2"
    if command -v wget >/dev/null 2>&1; then
        echo "DEBUG: (wget) Downloading $url"
        wget -O "$out" "$url"
    elif command -v curl >/dev/null 2>&1; then
        echo "DEBUG: (curl) Downloading $url"
        curl -fL -o "$out" "$url"
    else
        echo "Neither wget nor curl were found. Install one and try again." >&2
        exit 1
    fi
}

if [ ! -f "$NEOFORGE_VERSION_FILE" ] || [ "$(cat "$NEOFORGE_VERSION_FILE")" != "$NEOFORGE_VERSION" ]; then
    echo "Installing NeoForge $NEOFORGE_VERSION..."
    INSTALLER="neoforge-$NEOFORGE_VERSION-installer.jar"
    INSTALLER_URL="https://maven.neoforged.net/releases/net/neoforged/neoforge/$NEOFORGE_VERSION/neoforge-$NEOFORGE_VERSION-installer.jar"

    download "$INSTALLER_URL" "$INSTALLER"

    # The installer overwrites user_jvm_args.txt; preserve customizations.
    [ -f user_jvm_args.txt ] && cp user_jvm_args.txt .user_jvm_args.txt.bak

    java -jar "$INSTALLER" -installServer
    rm -f "$INSTALLER"

    [ -f .user_jvm_args.txt.bak ] && mv .user_jvm_args.txt.bak user_jvm_args.txt

    echo "$NEOFORGE_VERSION" > "$NEOFORGE_VERSION_FILE"
fi

if [ ! -f "$VERSION_FILE" ] || [ "$(cat "$VERSION_FILE")" != "$VERSION" ]; then
    echo "Installing CTM S5: Cogs and Canvas $VERSION..."
    ARCHIVE="ctm-s5-server-$VERSION.zip"
    ARCHIVE_URL="https://github.com/Crafttomuck/ctm-s5/releases/download/v$VERSION/ctm-s5-server-$VERSION.zip"

    download "$ARCHIVE_URL" "$ARCHIVE"

    rm -rf mods_old
    [ -d mods ] && mv mods mods_old

    jar xf "$ARCHIVE"
    rm -f "$ARCHIVE"

    if [ -d overrides ]; then
        cp -R overrides/. ./
    fi

    echo "$VERSION" > "$VERSION_FILE"
fi

# Forge requires a configured set of both JVM and program arguments.
# Add custom JVM arguments to the user_jvm_args.txt
# Add custom program arguments {such as nogui} to this file in the next line before the "$@" or
#  pass them to this script directly
java @user_jvm_args.txt @libraries/net/neoforged/neoforge/$NEOFORGE_VERSION/unix_args.txt "$@"
