"""fzf integration for interactive session selection."""

import shutil
import subprocess
import sys
from pathlib import Path

from cc_fi.constants import FZF_HEIGHT_PERCENT, FZF_PREVIEW_HEIGHT_PERCENT
from cc_fi.core.formatter import format_fzf_preview, format_list_row
from cc_fi.models.session import SessionData


def check_fzf_installed() -> bool:
    """
    Check if fzf is installed and available.

    @returns True if fzf is available, False otherwise
    @complexity O(1)
    @pure false - checks system PATH
    """
    return shutil.which("fzf") is not None


def build_fzf_input(sessions: list[SessionData]) -> str:
    """
    Build fzf input for interactive session selection.

    Format: session_id|formatted_row_with_searchable_content

    We use a two-column format:
    - Column 1: session_id (hidden, for extraction)
    - Column 2: formatted_row + hidden searchable content

    The searchable content is appended invisibly to allow deep search
    while maintaining clean display.

    @param sessions List of sessions to display
    @returns Newline-separated rows for fzf input
    @complexity O(n) where n is number of sessions
    @pure true
    """
    import re
    from cc_fi.core.formatter import (
        format_header_separator,
        format_instruction_header,
        format_list_header,
    )

    instruction_header = format_instruction_header()
    instruction_lines = instruction_header.split("\n")

    rows = [
        f"INSTRUCTION1|{instruction_lines[0]}",
        f"INSTRUCTION2|{instruction_lines[1]}",
        f"HEADER|{format_list_header()}",
        f"SEPARATOR|{format_header_separator()}",
    ]

    for session in sessions:
        formatted = format_list_row(session)

        # Strip ANSI codes from formatted text for searchable version
        formatted_plain = re.sub(r'\x1b\[[0-9;]*m', '', formatted)

        # Build searchable content (plain text + full content)
        # Add unique markers to avoid false matches
        searchable_content = f" SEARCH_START {formatted_plain} {session.full_content} SEARCH_END"

        # Make searchable content invisible using ANSI concealment
        invisible_searchable = f"\x1b[8m{searchable_content}\x1b[0m"

        # Combine visible formatted text with invisible searchable text
        display_content = f"{formatted}{invisible_searchable}"

        # Build row: session_id|display_content
        row = f"{session.session_id}|{display_content}"
        rows.append(row)

    return "\n".join(rows)


def extract_session_id_from_line(line: str) -> str:
    """
    Extract session ID from fzf input line.

    @param line fzf input line with format: session_id|display_content
    @returns Session ID (first field before pipe)
    @complexity O(1)
    @pure true
    """
    # Session ID is the first field before the pipe
    parts = line.split("|", 1)
    return parts[0] if parts else ""


def run_fzf_selection(sessions: list[SessionData]) -> SessionData | None:
    """
    Launch fzf for interactive session selection.

    @param sessions List of sessions to choose from
    @returns Selected SessionData or None if cancelled
    @throws RuntimeError When fzf is not installed
    @complexity O(n) where n is number of sessions
    @pure false - launches subprocess
    """
    if not check_fzf_installed():
        raise RuntimeError(
            "fzf is not installed. Install with: brew install fzf (macOS) "
            "or apt install fzf (Linux)"
        )

    fzf_input = build_fzf_input(sessions)
    session_map = {s.session_id: s for s in sessions}

    # Build preview command that extracts session ID and passes search query
    # {q} is the current fzf query, {} is the selected line
    # Session ID is the first field in pipe-delimited format
    preview_cmd = "echo {} | cut -d'|' -f1 | xargs -I % sh -c 'cc-fi --preview % --preview-query \"{q}\"' 2>/dev/null"

    cmd = [
        "fzf",
        "--ansi",
        "--exact",  # Require exact substring match, not fuzzy matching
        "--delimiter=|",
        "--with-nth=2",  # Display only column 2 (formatted row + invisible searchable)
        "--header-lines=4",  # Skip instruction (2 lines) + column header + separator
        "--layout=reverse",
        f"--height={FZF_HEIGHT_PERCENT}%",
        f"--preview-window=down:{FZF_PREVIEW_HEIGHT_PERCENT}%",
        "--preview",
        preview_cmd,
    ]

    try:
        result = subprocess.run(
            cmd,
            input=fzf_input,
            text=True,
            capture_output=True,
            check=False,
        )

        if result.returncode != 0:
            return None

        selected_line = result.stdout.strip()
        session_id = extract_session_id_from_line(selected_line)
        return session_map.get(session_id)

    except Exception as e:
        print(f"Error running fzf: {e}", file=sys.stderr)
        return None
