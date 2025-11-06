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

    Format: Single line with hidden session_id, visible formatted_row, and zero-width searchable

    We combine everything in one line without delimiters:
    - Hidden session_id using ANSI concealment
    - Visible formatted row
    - Zero-width searchable content using cursor positioning

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
        instruction_lines[0],
        instruction_lines[1],
        format_list_header(),
        format_header_separator(),
    ]

    for session in sessions:
        formatted = format_list_row(session)

        # Strip ANSI codes from formatted to get plain text
        formatted_plain = re.sub(r'\x1b\[[0-9;]*m', '', formatted)

        # Get searchable content from conversation
        content_snippet = session.full_content[:300].replace("\n", " ").replace("\r", " ")
        searchable = f"{formatted_plain} {content_snippet}"

        # Hide session ID using ANSI concealment
        hidden_id = f"\x1b[8m{session.session_id}|\x1b[0m"

        # Make searchable content zero-width using cursor save/restore
        # This keeps it searchable but not visible
        zero_width_searchable = f"\x1b[s{searchable}\x1b[u"

        # Combine all parts in one line
        row = f"{hidden_id}{formatted}{zero_width_searchable}"
        rows.append(row)

    return "\n".join(rows)


def extract_session_id_from_line(line: str) -> str:
    """
    Extract session ID from fzf input line.

    @param line fzf input line with hidden session_id at start
    @returns Session ID extracted from hidden part
    @complexity O(1)
    @pure true
    """
    import re
    # Remove ANSI codes to get plain text
    plain = re.sub(r'\x1b\[[0-9;]*m', '', line)
    # Session ID is before the first pipe
    parts = plain.split("|", 1)
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
    # Session ID is hidden at the start, extract it after removing ANSI codes
    preview_cmd = "echo {} | sed 's/\\x1b\\[[0-9;]*m//g' | cut -d'|' -f1 | xargs -I % sh -c 'cc-fi --preview % --preview-query \"{q}\"' 2>/dev/null"

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
