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
HEADERS = ["Name", "Version", "Add On For", "Category", "Added By", "Notes"]


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
                "",  # Add On For
                "",  # Category
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

    # Migrate from old layout: drop "Size (MB)" column if present
    if "Size (MB)" in mods_header:
        size_idx = mods_header.index("Size (MB)")
        mods_rows = [row[:size_idx] + row[size_idx + 1:] for row in mods_rows]
    if "Size (MB)" in removed_header:
        size_idx = removed_header.index("Size (MB)")
        removed_rows = [row[:size_idx] + row[size_idx + 1:] for row in removed_rows]

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
            "",  # Add On For
            "",  # Category
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
