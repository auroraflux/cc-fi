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

    Format: session_id|formatted_display_with_hidden_searchable

    We use a two-column pipe-delimited format:
    - Column 1: session_id (hidden)
    - Column 2: formatted_row + concealed searchable content (displayed + searchable)

    The searchable content is made invisible using ANSI concealment but remains
    searchable by fzf. We use --with-nth=2 to display only column 2.

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

        # Get searchable content - combine formatted plain text + conversation content
        formatted_plain = re.sub(r'\x1b\[[0-9;]*m', '', formatted)
        content_snippet = session.full_content[:500].replace("\n", " ").replace("\r", " ").replace("|", " ")
        searchable = f" {formatted_plain} {content_snippet}"

        # Conceal the searchable content so it's invisible but still searchable
        hidden_searchable = f"\x1b[8m{searchable}\x1b[0m"

        # Column 2 contains visible formatted + concealed searchable
        display_with_search = f"{formatted}{hidden_searchable}"

        # Two-column format: session_id|display_with_search
        row = f"{session.session_id}|{display_with_search}"
        rows.append(row)

    return "\n".join(rows)


def extract_session_id_from_line(line: str) -> str:
    """
    Extract session ID from fzf input line.

    @param line fzf input line in format: session_id|formatted|searchable
    @returns Session ID extracted from first column
    @complexity O(1)
    @pure true
    """
    # Session ID is before the first pipe
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
    # Session ID is in the first column of pipe-delimited format
    preview_cmd = "echo {} | cut -d'|' -f1 | xargs -I % sh -c 'cc-fi --preview % --preview-query \"{q}\"' 2>/dev/null"

    cmd = [
        "fzf",
        "--ansi",
        "--exact",  # Require exact substring match, not fuzzy matching
        "--delimiter=|",  # Pipe-delimited columns
        "--with-nth=2",  # Only display column 2 (formatted row)
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
