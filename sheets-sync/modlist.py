"""Sync installed Minecraft mods to a Google Sheet.

Single entry point: python modlist.py

Reads prism-export.json, diffs against Google Sheets state,
and pushes updates (new mods, removals, version changes) while
preserving all user edits in the sheet.
"""

import json
import re
import sys
from pathlib import Path

import gspread

PROJECT_DIR = Path(__file__).parent
CONFIG_PATH = PROJECT_DIR / "config.json"
EXPORT_PATH = PROJECT_DIR.parent / "prism-export.json"

# Sheet tab names
MODS_TAB = "Mods"
REMOVED_TAB = "Removed"
TRACKING_TAB = "_tracking"

# Columns in the Mods/Removed tabs
HEADERS = ["Name", "Version", "Category", "Added By", "Notes"]

# ---------------------------------------------------------------------------
# Mod categories — keyed by mod name from prism-export.json
# ---------------------------------------------------------------------------

CATEGORIES: dict[str, str] = {
    # --- Create ecosystem ---
    "Aileron": "Create",
    "Aeronautics Claims": "Create",
    "Create": "Create",
    "Create : Numismatic Bounties": "Create",
    "Create Aeronautics": "Create",
    "Create Bits 'n' Bobs": "Create",
    "Create Crafts & Additions": "Create",
    "Create Deco": "Create",
    "Create Diesel Generators": "Create",
    "Create Dynamic Lights": "Create",
    "Create Encased": "Create",
    "Create Goggles": "Create",
    "Create Jetpack": "Create",
    "Create More: Parallel Pipes": "Create",
    "Create Rail Grinding": "Create",
    "Create Railways Navigator": "Create",
    "Create Shuffle Filter": "Create",
    "Create Slice & Dice": "Create",
    "Create Stats and Numbers": "Create",
    "Create Stuff & Additions": "Create",
    "Create Tracks": "Create",
    "Create: Aeroworks": "Create",
    "Create: Bells & Whistles": "Create",
    "Create: Big Contraptions": "Create",
    "Create: Blocks & Bogies": "Create",
    "Create: Central Kitchen": "Create",
    "Create: Compatible Storage": "Create",
    "Create: Connected": "Create",
    "Create: Copper and Zinc": "Create",
    "Create: Copycats+": "Create",
    "Create: Dragons Plus": "Create",
    "Create: Enchantment Industry": "Create",
    "Create: Escalated": "Create",
    "Create: Filters Anywhere": "Create",
    "Create: Framed": "Create",
    "Create: Interiors": "Create",
    "Create: More Girder": "Create",
    "Create: Numismatics": "Create",
    "Create: Oxidized": "Create",
    "Create: Pattern Schematics": "Create",
    "Create: Power Grid": "Create",
    "Create: Rail Grinding": "Create",
    "Create: The Factory Must Grow": "Create",
    "Create: Threaded Trains": "Create",
    "Create: Trading Floor": "Create",
    "CreateBetterFps": "Create",
    "Drive By Wire": "Create",
    "Iris Flywheel Compat": "Create",
    "Molten Vents": "Create",
    "Sable": "Create",
    "Sable Schematic API": "Create",
    "Sable: Stuff&Additions Compatibility": "Create",
    "Synaxis": "Create",
    "Vista Aeronautics Fix": "Create",

    # --- Decoration & Building ---
    "Amendments": "Decoration",
    "Another Furniture": "Decoration",
    "AntiBlocksReChiseled": "Decoration",
    "Architects Palette": "Decoration",
    "Arts & Crafts": "Decoration",
    "Beautify": "Decoration",
    "Clayworks": "Decoration",
    "Decorative Blocks Reborn": "Decoration",
    "Design n' Decor": "Decoration",
    "Diagonal Fences": "Decoration",
    "Dramatic Doors (NeoQuiFab)": "Decoration",
    "Dye Depot": "Decoration",
    "FramedBlocks": "Decoration",
    "Handcrafted": "Decoration",
    "Iden's Decor": "Decoration",
    "Immersive Furniture": "Decoration",
    "Immersive Paintings": "Decoration",
    "Macaw's Bridges": "Decoration",
    "Macaw's Doors": "Decoration",
    "Macaw's Paths and Pavings": "Decoration",
    "Macaw's Trapdoors": "Decoration",
    "Macaw's Windows": "Decoration",
    "ManyIdeas Doors": "Decoration",
    "Rechiseled": "Decoration",
    "Rechiseled: AE2": "Decoration",
    "Rechiseled: Create": "Decoration",
    "Unusual Furniture": "Decoration",
    "Woodworks": "Decoration",

    # --- Worldgen & Structures ---
    "Angel Islands": "Worldgen",
    "atistructures": "Worldgen",
    "Biolith": "Worldgen",
    "ChoiceTheorem's Overhauled Village": "Worldgen",
    "Civillis": "Worldgen",
    "Epic Structures: Dungeons": "Worldgen",
    "Epic Structures: Igloo": "Worldgen",
    "Epic Structures: Witch Huts": "Worldgen",
    "Explorify": "Worldgen",
    "MoogsEndStructures": "Worldgen",
    "MoogsVoyagerStructures": "Worldgen",
    "No Man's Land": "Worldgen",
    "SparseStructures": "Worldgen",
    "Terralith": "Worldgen",
    "Terralith ReStoned": "Worldgen",
    "Towns and Towers": "Worldgen",
    "Vista": "Worldgen",
    "YUNG's Better Desert Temples": "Worldgen",
    "YUNG's Better Jungle Temples": "Worldgen",
    "YUNG's Better Nether Fortresses": "Worldgen",
    "YUNG's Better Ocean Monuments": "Worldgen",
    "YUNG's Better Strongholds": "Worldgen",

    # --- Performance & Optimization ---
    "Alternate Current": "Performance",
    "BadOptimizations": "Performance",
    "Clumps": "Performance",
    "Concurrent Chunk Management Engine": "Performance",
    "Fast Paintings": "Performance",
    "Fast Workbench": "Performance",
    "Ferrite Core": "Performance",
    "Gpu memory leak fix": "Performance",
    "ImmediatelyFast": "Performance",
    "Let Me Despawn": "Performance",
    "Lithium": "Performance",
    "ModernFix": "Performance",
    "More Culling": "Performance",
    "Noisium": "Performance",
    "Remove Reloading Screen": "Performance",
    "Smoothchunk mod": "Performance",

    # --- Graphics & Rendering ---
    "Entity Model Features": "Graphics",
    "Entity Texture Features": "Graphics",
    "Iris": "Graphics",
    "Reese's Sodium Options": "Graphics",
    "Sodium": "Graphics",
    "Sodium Dynamic Lights": "Graphics",

    # --- Food & Farming ---
    "Farmer's Delight": "Food & Farming",
    "Kaleidoscope Cookery": "Food & Farming",
    "KaleidoscopeCookery:Automation": "Food & Farming",
    "Ponder for KaleidoscopeCookery": "Food & Farming",
    "Spice of Life: Carrot Edition": "Food & Farming",

    # --- Let's Do series ---
    "[Let's Do Addon] Compat": "Let's Do",
    "[Let's Do] Beachparty": "Let's Do",
    "[Let's Do] BloomingNature": "Let's Do",
    "[Let's Do] Brewery": "Let's Do",
    "[Let's Do] Candlelight": "Let's Do",
    "[Let's Do] Farm & Charm": "Let's Do",
    "[Let's Do] Furniture": "Let's Do",
    "[Let's Do] HerbalBrews": "Let's Do",
    "[Let's Do] Meadow": "Let's Do",
    "[Let's Do] Vinery": "Let's Do",
    "[Let's Do] Wilder Nature": "Let's Do",
    "emi-letsdo-compat": "Let's Do",

    # --- Storage ---
    "Sophisticated Backpacks": "Storage",
    "Sophisticated Backpacks Create Integration": "Storage",
    "Sophisticated Storage": "Storage",
    "Sophisticated Storage Create Integration": "Storage",
    "Sophisticated Storage In Motion": "Storage",
    "SophisticatedSorter": "Storage",
    "Storage Labels": "Storage",

    # --- Technology ---
    "AE2WTLib": "Technology",
    "Applied Energistics 2": "Technology",

    # --- Gameplay ---
    "Accessories": "Gameplay",
    "All The Leaks": "Gameplay",
    "Aquaculture 2": "Gameplay",
    "Artifacts": "Gameplay",
    "Block Runner": "Gameplay",
    "Bountiful": "Gameplay",
    "Camping": "Gameplay",
    "Comforts": "Gameplay",
    "Ecologics": "Gameplay",
    "End Remastered": "Gameplay",
    "Envelope": "Gameplay",
    "Etched": "Gameplay",
    "Friends&Foes": "Gameplay",
    "Grappling Hook": "Gameplay",
    "Hang Glider": "Gameplay",
    "Hearthstone Mod": "Gameplay",
    "Immersive Melodies": "Gameplay",
    "Lootr": "Gameplay",
    "Magnum Torch": "Gameplay",
    "MmmMmmMmmMmm": "Gameplay",
    "Naturalist": "Gameplay",
    "Quark": "Gameplay",
    "Quark Oddities": "Gameplay",
    "Relics": "Gameplay",
    "Supplementaries": "Gameplay",
    "Supplementaries Squared": "Gameplay",

    # --- QoL & UI ---
    "Almanac": "QoL",
    "AppleSkin": "QoL",
    "Armor Statues": "QoL",
    "Better Advancements": "QoL",
    "Better Mods Button": "QoL",
    "Better Third Person": "QoL",
    "BetterF3": "QoL",
    "Carry On": "QoL",
    "Chat Heads": "QoL",
    "Configured": "QoL",
    "Controlling": "QoL",
    "CosmeticArmorReworked": "QoL",
    "Cut Through": "QoL",
    "Dark Mode Everywhere": "QoL",
    "EMI": "QoL",
    "Easy Anvils": "QoL",
    "Easy Magic": "QoL",
    "EnchantmentDescriptions": "QoL",
    "FancyMenu": "QoL",
    "Freecam": "QoL",
    "Jade": "QoL",
    "Leaves Be Gone": "QoL",
    "Map Atlases": "QoL",
    "Morph-o-Tool": "QoL",
    "Mouse Tweaks": "QoL",
    "Nature's Compass": "QoL",
    "NetherPortalFix": "QoL",
    "Polymorph": "QoL",
    "Straw Statues": "QoL",
    "Stylish Effects": "QoL",
    "Toast Control": "QoL",
    "TrashSlot": "QoL",
    "What Are They Up To": "QoL",
    "Xaero's Minimap": "QoL",
    "Xaero's World Map": "QoL",

    # --- Utility & Server ---
    "AlmostUnified": "Utility",
    "AttributeFix": "Utility",
    "Chunky": "Utility",
    "ChunkyBorder": "Utility",
    "Connectivity Mod": "Utility",
    "KubeJS": "Utility",
    "KubeJS Create": "Utility",
    "Log Begone": "Utility",
    "LootJS": "Utility",
    "Neruina": "Utility",
    "No Chat Reports": "Utility",
    "Observable": "Utility",
    "OpacBonusClaims": "Utility",
    "Open Parties and Claims": "Utility",
    "PacketFixer": "Utility",
    "Simple Voice Chat": "Utility",
    "Too Fast": "Utility",
    "Yeetus Experimentus": "Utility",
    "recipeessentials mod": "Utility",
    "spark": "Utility",

    # --- Library & API ---
    "Architectury": "Library",
    "Balm": "Library",
    "Blueprint": "Library",
    "Bookshelf": "Library",
    "Cloth Config v15 API": "Library",
    "Configurable": "Library",
    "CoroUtil": "Library",
    "Cristel Lib": "Library",
    "Cupboard mod": "Library",
    "Curios API": "Library",
    "DragonLib": "Library",
    "Fusion": "Library",
    "Fzzy Config": "Library",
    "GeckoLib 4": "Library",
    "GuideME": "Library",
    "JinxedLib": "Library",
    "Kambrik": "Library",
    "Konkrete": "Library",
    "Kotlin for Forge": "Library",
    "Lithostitched": "Library",
    "Load My F***ing Tags": "Library",
    "LowDragLib2": "Library",
    "ManyIdeas Core": "Library",
    "Melody": "Library",
    "MidnightLib": "Library",
    "Moog's Structure Lib": "Library",
    "Moonlight Lib": "Library",
    "OctoLib": "Library",
    "Placebo": "Library",
    "PrickleMC": "Library",
    "Puzzles Lib": "Library",
    "Recipes Library": "Library",
    "Resourceful Lib": "Library",
    "Rhino": "Library",
    "Searchables": "Library",
    "Sodium Options API": "Library",
    "Sophisticated Core": "Library",
    "Structure Essentials mod": "Library",
    "SuperMartijn642's Config Library": "Library",
    "SuperMartijn642's Core Lib": "Library",
    "YUNG's API": "Library",
    "Zeta": "Library",
    "oωo": "Library",
}


def get_category(mod_name: str) -> str:
    """Look up category for a mod name, returning empty string if unknown."""
    return CATEGORIES.get(mod_name, "")


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Export loading
# ---------------------------------------------------------------------------

def load_export(path: Path) -> dict[str, dict]:
    """Read prism-export.json and return {filename: {name, version, url}}."""
    with open(path) as f:
        entries = json.load(f)
    export = {}
    for entry in entries:
        export[entry["filename"]] = {
            "name": entry.get("name", ""),
            "version": entry.get("version", ""),
            "url": entry.get("url", ""),
        }
    return export


# ---------------------------------------------------------------------------
# Google Sheets helpers
# ---------------------------------------------------------------------------

def get_or_create_worksheet(spreadsheet, title: str, headers: list[str] | None = None):
    """Get an existing worksheet or create it with optional headers."""
    try:
        return spreadsheet.worksheet(title)
    except gspread.exceptions.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=title, rows=1, cols=len(headers or HEADERS))
        if headers:
            ws.update([headers], "A1")
        return ws


def read_sheet_rows(ws, formulas: bool = False) -> list[list[str]]:
    """Read all values from a worksheet, skipping the header row.

    If formulas=True, return raw formula text (e.g. =HYPERLINK(...))
    instead of the displayed values.
    """
    kwargs = {}
    if formulas:
        kwargs["value_render_option"] = "FORMULA"
    all_values = ws.get_all_values(**kwargs)
    if len(all_values) <= 1:
        return []
    return all_values[1:]  # skip header


def write_sheet(ws, headers: list[str], rows: list[list[str]]):
    """Clear and rewrite a worksheet with headers + rows."""
    ws.clear()
    ws.update([headers] + rows, "A1", value_input_option="USER_ENTERED")


# ---------------------------------------------------------------------------
# HYPERLINK formula helpers
# ---------------------------------------------------------------------------

def make_name_cell(name: str, url: str) -> str:
    """Build a HYPERLINK formula if URL exists, plain name otherwise."""
    if not url:
        return name
    escaped_name = name.replace('"', '""')
    escaped_url = url.replace('"', '""')
    return f'=HYPERLINK("{escaped_url}", "{escaped_name}")'


def extract_name_and_url(cell_value: str) -> tuple[str, str]:
    """Extract name and URL from a cell that may contain a HYPERLINK formula."""
    match = re.match(r'=HYPERLINK\("([^"]*)"(?:,\s*"([^"]*)")?\)', cell_value)
    if match:
        url = match.group(1)
        name = match.group(2) or url
        return name, url
    return cell_value, ""


# ---------------------------------------------------------------------------
# Column migration helpers
# ---------------------------------------------------------------------------

def _drop_column(header: list[str], rows: list[list[str]], col_name: str) -> list[list[str]]:
    """Remove a column from rows if it exists in the header."""
    if col_name not in header:
        return rows
    idx = header.index(col_name)
    return [row[:idx] + row[idx + 1:] for row in rows]


# ---------------------------------------------------------------------------
# Core sync logic
# ---------------------------------------------------------------------------

def sync(spreadsheet, export_data: dict[str, dict]):
    """Main sync: diff export against sheets, push updates."""
    export_filenames = set(export_data.keys())

    # Check if _tracking tab exists (first run = bootstrap)
    try:
        tracking_ws = spreadsheet.worksheet(TRACKING_TAB)
    except gspread.exceptions.WorksheetNotFound:
        # First run: create all tabs from export data
        tracking_ws = get_or_create_worksheet(spreadsheet, TRACKING_TAB, ["Filename", "Name"])
        mods_rows = []
        tracking_entries = []
        for filename in sorted(export_filenames):
            info = export_data[filename]
            name_cell = make_name_cell(info["name"], info["url"])
            mods_rows.append([
                name_cell,
                info["version"],
                get_category(info["name"]),
                "Modpack Sync",
                "",  # Notes
            ])
            tracking_entries.append([filename, info["name"]])

        def sort_key(row):
            name, _ = extract_name_and_url(row[0])
            return name.lower()

        mods_rows.sort(key=sort_key)

        mods_ws = get_or_create_worksheet(spreadsheet, MODS_TAB, HEADERS)
        write_sheet(mods_ws, HEADERS, mods_rows)

        removed_ws = get_or_create_worksheet(spreadsheet, REMOVED_TAB, HEADERS)
        write_sheet(removed_ws, HEADERS, [])

        write_sheet(tracking_ws, ["Filename", "Name"], tracking_entries)

        print(f"First run complete: {len(mods_rows)} mods, {len(tracking_entries)} tracked files")
        return

    # Read current state from all tabs
    tracking_rows = read_sheet_rows(tracking_ws)
    # {filename: name}
    tracking = {row[0]: row[1] for row in tracking_rows if len(row) >= 2}

    # Read Mods and Removed tabs with formula rendering to preserve HYPERLINKs
    mods_ws = spreadsheet.worksheet(MODS_TAB)
    mods_all = mods_ws.get_all_values(value_render_option="FORMULA")
    mods_header = mods_all[0] if mods_all else []
    mods_rows = mods_all[1:] if len(mods_all) > 1 else []

    removed_ws = get_or_create_worksheet(spreadsheet, REMOVED_TAB, HEADERS)
    removed_all = removed_ws.get_all_values(value_render_option="FORMULA")
    removed_header = removed_all[0] if removed_all else []
    removed_rows = removed_all[1:] if len(removed_all) > 1 else []

    # Migrate from old layouts: drop removed columns if present
    for col_name in ("Size (MB)", "Add On For"):
        mods_rows = _drop_column(mods_header, mods_rows, col_name)
        removed_rows = _drop_column(removed_header, removed_rows, col_name)

    # Build name → row index mapping for the Mods tab
    name_to_indices: dict[str, list[int]] = {}
    for i, row in enumerate(mods_rows):
        name, _ = extract_name_and_url(row[0]) if row else ("", "")
        name_to_indices.setdefault(name, []).append(i)

    tracked_filenames = set(tracking.keys())

    # Compute diffs
    new_filenames = export_filenames - tracked_filenames
    removed_filenames = tracked_filenames - export_filenames
    existing_filenames = tracked_filenames & export_filenames

    # --- Handle existing mods: update versions ---
    name_idx_cursor: dict[str, int] = {}
    filename_to_row_idx: dict[str, int] = {}
    for filename in sorted(existing_filenames):
        name = tracking[filename]
        indices = name_to_indices.get(name, [])
        cursor = name_idx_cursor.get(name, 0)
        if cursor < len(indices):
            filename_to_row_idx[filename] = indices[cursor]
            name_idx_cursor[name] = cursor + 1

    version_col = HEADERS.index("Version")
    for filename, idx in filename_to_row_idx.items():
        while len(mods_rows[idx]) <= version_col:
            mods_rows[idx].append("")
        mods_rows[idx][version_col] = export_data[filename]["version"]

    # --- Handle removed mods ---
    removed_count = 0
    added_by_col = HEADERS.index("Added By")
    rows_to_remove = set()
    name_remove_count: dict[str, int] = {}

    for filename in sorted(removed_filenames):
        name = tracking[filename]
        indices = name_to_indices.get(name, [])
        # Pick the next un-removed index for this name
        offset = name_remove_count.get(name, 0)
        name_remove_count[name] = offset + 1

        candidate_indices = [i for i in indices if i not in rows_to_remove]
        if not candidate_indices:
            continue

        idx = candidate_indices[0]
        row = mods_rows[idx]

        # Only move if Added By == "Modpack Sync"
        added_by = row[added_by_col] if len(row) > added_by_col else ""
        if added_by != "Modpack Sync":
            continue

        removed_rows.append(row)
        rows_to_remove.add(idx)
        removed_count += 1

    # Remove rows from mods (in reverse order to preserve indices)
    for idx in sorted(rows_to_remove, reverse=True):
        mods_rows.pop(idx)

    # Remove from tracking
    for filename in removed_filenames:
        tracking.pop(filename, None)

    # --- Handle new mods ---
    new_count = 0
    for filename in sorted(new_filenames):
        info = export_data[filename]
        name_cell = make_name_cell(info["name"], info["url"])
        row = [
            name_cell,
            info["version"],
            get_category(info["name"]),
            "Modpack Sync",
            "",  # Notes
        ]
        mods_rows.append(row)
        tracking[filename] = info["name"]
        new_count += 1

    # Sort mods by name
    def sort_key(row):
        name, _ = extract_name_and_url(row[0]) if row else ("", "")
        return name.lower()

    mods_rows.sort(key=sort_key)

    # --- Push everything back ---
    write_sheet(mods_ws, HEADERS, mods_rows)
    write_sheet(removed_ws, HEADERS, removed_rows)

    tracking_entries = [[fn, name] for fn, name in sorted(tracking.items())]
    tracking_headers = ["Filename", "Name"]
    write_sheet(tracking_ws, tracking_headers, tracking_entries)

    unchanged = len(existing_filenames) - removed_count
    print(f"Sync complete: {new_count} new, {removed_count} removed, {unchanged} unchanged")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def fresh_start(spreadsheet):
    """Delete _tracking tab so sync bootstraps from scratch.

    Mods and Removed are overwritten by the bootstrap path, so they
    don't need deleting (and keeping them avoids the Google Sheets
    "can't delete last sheet" constraint).
    """
    try:
        ws = spreadsheet.worksheet(TRACKING_TAB)
        spreadsheet.del_worksheet(ws)
        print(f"Deleted tab: {TRACKING_TAB}")
    except gspread.exceptions.WorksheetNotFound:
        pass


def main():
    config = load_config()
    fresh = "--fresh" in sys.argv

    if not EXPORT_PATH.is_file():
        print(f"Error: export file not found: {EXPORT_PATH}", file=sys.stderr)
        sys.exit(1)

    export_data = load_export(EXPORT_PATH)

    sa_path = PROJECT_DIR / config["service_account"]
    gc = gspread.service_account(filename=sa_path)
    spreadsheet = gc.open_by_key(config["spreadsheet_id"])

    if fresh:
        fresh_start(spreadsheet)

    sync(spreadsheet, export_data)


if __name__ == "__main__":
    main()
