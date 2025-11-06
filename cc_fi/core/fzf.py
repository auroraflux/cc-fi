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

    Format: formatted_row_with_ansi ␟ session_id ␟ formatted_row_no_ansi ␟ full_content

    We append searchable content after the visible part, separated by a special char (␟).
    The searchable content is made invisible using zero-width spaces and special formatting.

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

    # Use Unicode separator that won't appear in normal text
    SEP = " ␟ "  # Unit separator with spaces for visibility

    rows = [
        instruction_lines[0],
        instruction_lines[1],
        format_list_header(),
        format_header_separator(),
    ]

    for session in sessions:
        formatted = format_list_row(session)

        # Strip ANSI codes from formatted text to create plain searchable version
        formatted_plain = re.sub(r'\x1b\[[0-9;]*m', '', formatted)

        # Build searchable content
        searchable_content = f"{session.session_id}{SEP}{formatted_plain}{SEP}{session.full_content}"

        # Make searchable content invisible using zero-width spaces and dim color
        # This allows searching while keeping display clean
        invisible_searchable = f"\x1b[8m{searchable_content}\x1b[0m"

        # Combine visible and invisible parts
        row = f"{formatted}  {invisible_searchable}"
        rows.append(row)

    return "\n".join(rows)


def extract_session_id_from_line(line: str) -> str:
    """
    Extract session ID from fzf input line.

    @param line fzf input line with format: visible_part + invisible_searchable
    @returns Session ID extracted from invisible part
    @complexity O(1)
    @pure true
    """
    import re

    # Remove ANSI codes to find the content
    plain = re.sub(r'\x1b\[[0-9;]*m', '', line)

    # Look for the separator to find searchable content
    SEP = " ␟ "

    # Find the last occurrence of the visible content followed by separator
    # Format is: visible_content SEP session_id SEP plain_text SEP full_content
    parts = plain.rsplit(SEP, 3)  # Split from right, max 3 splits

    if len(parts) >= 4:
        # parts = [visible_content, session_id, plain_text, full_content]
        # We want the session_id which is parts[1] when split from right,
        # but since we used rsplit, it's parts[-3]
        return parts[-3]

    return ""


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
    # Session ID is extracted from the invisible part using the separator
    preview_cmd = r"echo {} | python3 -c \"import sys, re; line = sys.stdin.read(); plain = re.sub(r'\\x1b\\[[0-9;]*m', '', line); parts = plain.split(' ␟ '); print(parts[-3] if len(parts) >= 3 else '')\" | xargs -I % sh -c 'cc-fi --preview % --preview-query \"{q}\"' 2>/dev/null"

    cmd = [
        "fzf",
        "--ansi",
        "--exact",  # Require exact substring match, not fuzzy matching
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
