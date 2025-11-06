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

    Format: session_id|visible_row|full_content
    - Column 1: session_id (hidden, for selection)
    - Column 2: visible_row (displayed table row)
    - Column 3: full_content (hidden, for deep search)

    fzf searches columns 2 and 3, but only displays column 2.
    This enables deep search across entire conversation history while
    maintaining clean visual display.

    @param sessions List of sessions to display
    @returns Newline-separated rows for fzf input
    @complexity O(n) where n is number of sessions
    @pure true
    """
    from cc_fi.core.formatter import (
        format_header_separator,
        format_instruction_header,
        format_list_header,
    )

    instruction_header = format_instruction_header()
    instruction_lines = instruction_header.split("\n")

    rows = [
        f"INSTRUCTION1|{instruction_lines[0]}|",
        f"INSTRUCTION2|{instruction_lines[1]}|",
        f"HEADER|{format_list_header()}|",
        f"SEPARATOR|{format_header_separator()}|",
    ]

    for session in sessions:
        formatted = format_list_row(session)
        # Add full_content as third field for deep search (hidden from display)
        # Replace pipe characters to avoid breaking delimiter-based parsing
        full_content_safe = session.full_content.replace("|", " ")
        rows.append(f"{session.session_id}|{formatted}|{full_content_safe}")

    return "\n".join(rows)


def extract_session_id_from_line(line: str) -> str:
    """
    Extract session ID from fzf input line.

    @param line fzf input line (session_id|formatted_row)
    @returns Session ID
    @complexity O(1)
    @pure true
    """
    return line.split("|", 1)[0]


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
    preview_cmd = "echo {} | cut -d'|' -f1 | xargs -I % sh -c 'cc-fi --preview % --preview-query \"{q}\"' 2>/dev/null"

    cmd = [
        "fzf",
        "--ansi",
        "--delimiter=|",
        "--with-nth=2",  # Display only column 2 (visible row), but search all columns
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
