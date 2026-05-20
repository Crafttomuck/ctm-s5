# CTM Season 5: Cogs and Canvas

A Minecraft modpack for CraftToMuck Season 5. Managed with [packwiz](https://packwiz.infra.link/).

## Repo layout

- `pack/` — the packwiz pack (`pack.toml`, `index.toml`, `mods/`, etc.)
- `pack/changelog.md` — per-release notes
- `start.sh` — server bootstrap/launcher; pins the modpack and NeoForge versions, downloads on first run or version bump, then `exec`s NeoForge
- `sheets-sync/` — Google Sheets sync tooling (`modlist.py`, `config.json`, etc.)
- `.github/workflows/release.yml` — CI that builds client and server zips on every push to `main` and attaches them to a GitHub release tagged `v<version>`

## Release workflow

### Update mods

Make changes from inside `pack/` using the `packwiz` CLI:

```sh
cd pack
packwiz cf add <slug-or-url>     # add a CurseForge mod
packwiz update --all             # refresh all mods to latest
packwiz remove <slug>            # remove a mod
```

`packwiz` rewrites `pack/mods/*.pw.toml` and refreshes the hash in `pack/index.toml` and `pack/pack.toml`.

### Bump version, commit, tag

Bump `version = "..."` in `pack/pack.toml`, then add an entry to `pack/changelog.md` describing what changed. Commit and tag:

```sh
git add pack/
git commit -m "Release v0.0.5"
git tag v0.0.5
git push origin main --tags
```

The push to `main` triggers `.github/workflows/release.yml`, which:

- Reads the version from `pack/pack.toml`
- Runs `packwiz curseforge export` once per side (`-s client`, `-s server`)
- For the server zip, downloads every mod jar via `moddl` into `mods/` and flattens packwiz's `overrides/` into the root
- Creates (or updates) the GitHub release `v<version>` with both zips attached

Final server zip layout:

```
mods/<jar files>
config/, defaultconfigs/, kubejs/, ...   # flattened from overrides/
```

### Update the server

Wait for the **Build & Release** workflow run to finish and confirm the new `v<version>` release has both zips attached on GitHub before touching the server — otherwise `start.sh` will 404 trying to download the archive.

The server's `start.sh` tracks the installed version in a marker file. To roll the server forward, edit the `VERSION` variable at the top of `start.sh` to match the new release and restart:

```sh
# in start.sh
VERSION="0.0.5"
```

On the next launch, `start.sh` will:

- Download the server zip from the GitHub release
- Move the existing `mods/` to `mods_old/` (overwriting any previous backup)
- Extract the new zip into the server root
- Re-apply the contents of `overrides/` (a server-local directory of sticky customizations like `server.properties`) on top
- Write the version to the marker file so the install step is skipped on subsequent restarts

`start.sh` does the same dance for NeoForge via `NEOFORGE_VERSION`. Bump that variable to roll the loader; on the next restart it downloads the matching installer, runs `-installServer`, restores `user_jvm_args.txt` (the installer overwrites it), and updates the marker file.

## Bootstrapping a fresh server

On a clean Pelican/Pterodactyl egg (or any directory with Java 21 available), the only file you need to drop in is `start.sh` from this repo. On the first launch:

- `.neoforge-version` doesn't exist, so `start.sh` downloads the NeoForge installer and runs `-installServer`, which populates `libraries/` and writes `user_jvm_args.txt`.
- The version marker doesn't exist, so it then downloads the server zip and extracts mods + configs into the root.
- Finally it `exec`s NeoForge with the generated `unix_args.txt`.

If you need to force a reinstall of either layer, delete the corresponding marker file and restart.

The yolks `java_21` image used by Pterodactyl/Pelican has everything `start.sh` needs (`curl`/`wget`, `jar` from the JDK). No `unzip` is needed — extraction goes through `jar xf`.

## Modlist sync

`sheets-sync/modlist.py` keeps a Google Sheet in sync with `prism-export.json`. Run it with:

```sh
sheets-sync/venv/bin/python sheets-sync/modlist.py
```

It reads `prism-export.json` (resolved relative to the script, same as `update-packwiz.sh`) and `config.json` for the spreadsheet ID and service account credentials. On each run it diffs the export against the sheet, adds new mods with names/versions/URLs, moves removed mods to a "Removed" tab, updates versions, and preserves any user edits (categories, notes, etc.).

Use `--fresh` to wipe the sheet and rebuild from scratch:

```sh
sheets-sync/venv/bin/python sheets-sync/modlist.py --fresh
```
