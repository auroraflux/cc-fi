"""Output formatting for sessions."""

from datetime import datetime
from pathlib import Path

from cc_fi.constants import (
    COLOR_BLUE,
    COLOR_BOLD,
    COLOR_GRAY,
    COLOR_GREEN,
    COLOR_RESET,
    COLOR_YELLOW,
    MESSAGE_DETAIL_LENGTH,
    MESSAGE_PREVIEW_LENGTH,
    MESSAGE_COLUMN_WIDTH,
    PATH_COLUMN_WIDTH,
    PROJECT_COLUMN_WIDTH,
    TIME_COLUMN_WIDTH,
)
from cc_fi.models.session import SessionData


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace for single-line display.

    @param text Text to normalize
    @returns Text with newlines/tabs replaced by spaces, collapsed
    @complexity O(n) where n is text length
    @pure true
    """
    import re

    normalized = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def truncate_message(message: str, max_length: int) -> str:
    """
    Truncate message to max length with ellipsis.

    @param message Message text to truncate
    @param max_length Maximum length (including ellipsis)
    @returns Truncated message with normalized whitespace
    @complexity O(n) where n is max_length
    @pure true
    """
    normalized = normalize_whitespace(message)

    if len(normalized) <= max_length:
        return normalized

    return normalized[: max_length - 3] + "..."


def format_timestamp(dt: datetime) -> str:
    """
    Format timestamp in 12-hour format.

    @param dt Datetime to format
    @returns Formatted string like "Nov 05, 10:00 PM"
    @complexity O(1)
    @pure true
    """
    return dt.strftime("%b %d, %I:%M %p")


def shorten_path(path: str) -> str:
    """
    Shorten path by replacing home directory with ~.

    @param path Full path string
    @returns Shortened path
    @complexity O(n) where n is path length
    @pure true
    """
    home = str(Path.home())
    if path.startswith(home):
        return path.replace(home, "~", 1)
    return path


def format_list_row(session: SessionData) -> str:
    """
    Format session as colored columnar row for list view.

    @param session SessionData to format
    @returns Formatted string with ANSI colors
    @complexity O(1)
    @pure true
    """
    project = session.project_name[:PROJECT_COLUMN_WIDTH].ljust(PROJECT_COLUMN_WIDTH)
    path = shorten_path(session.cwd)[:PATH_COLUMN_WIDTH].ljust(PATH_COLUMN_WIDTH)
    time_str = format_timestamp(session.timestamp).ljust(TIME_COLUMN_WIDTH)

    # Use first message, fall back to last message if empty
    msg_to_display = session.first_message.strip()
    if not msg_to_display:
        msg_to_display = session.last_message.strip()
    if not msg_to_display:
        msg_to_display = "(no messages)"

    message = truncate_message(msg_to_display, MESSAGE_COLUMN_WIDTH)

    return (
        f"{COLOR_GREEN}{project}{COLOR_RESET}  "
        f"{COLOR_BLUE}{path}{COLOR_RESET}  "
        f"{COLOR_YELLOW}{time_str}{COLOR_RESET}  "
        f"{COLOR_GRAY}{message}{COLOR_RESET}"
    )


def format_list_header() -> str:
    """
    Format header row for list view with bold colored columns.

    @returns Formatted header string with bold colors matching data columns
    @complexity O(1)
    @pure true
    """
    project = "PROJECT".ljust(PROJECT_COLUMN_WIDTH)
    path = "DIRECTORY".ljust(PATH_COLUMN_WIDTH)
    time_str = "TIME".ljust(TIME_COLUMN_WIDTH)
    message = "FIRST MESSAGE"

    return (
        f"{COLOR_BOLD}{COLOR_GREEN}{project}{COLOR_RESET}  "
        f"{COLOR_BOLD}{COLOR_BLUE}{path}{COLOR_RESET}  "
        f"{COLOR_BOLD}{COLOR_YELLOW}{time_str}{COLOR_RESET}  "
        f"{COLOR_BOLD}{COLOR_GRAY}{message}{COLOR_RESET}"
    )


def format_header_separator() -> str:
    """
    Format separator line under header with colored spans.

    @returns Formatted separator line with colors matching columns
    @complexity O(1)
    @pure true
    """
    project_sep = "─" * PROJECT_COLUMN_WIDTH
    path_sep = "─" * PATH_COLUMN_WIDTH
    time_sep = "─" * TIME_COLUMN_WIDTH
    message_sep = "─" * MESSAGE_COLUMN_WIDTH

    return (
        f"{COLOR_GREEN}{project_sep}{COLOR_RESET}  "
        f"{COLOR_BLUE}{path_sep}{COLOR_RESET}  "
        f"{COLOR_YELLOW}{time_sep}{COLOR_RESET}  "
        f"{COLOR_GRAY}{message_sep}{COLOR_RESET}"
    )


def format_fzf_preview(session: SessionData) -> str:
    """
    Format session details for fzf preview pane.

    @param session SessionData to format
    @returns Multi-line formatted string
    @complexity O(1)
    @pure true
    """
    short_path = shorten_path(session.cwd)
    time_str = format_timestamp(session.timestamp)
    first_msg = truncate_message(session.first_message, MESSAGE_DETAIL_LENGTH)
    last_msg = truncate_message(session.last_message, MESSAGE_DETAIL_LENGTH)

    lines = [
        f"{COLOR_BOLD}{COLOR_GRAY}Session:{COLOR_RESET}       {session.session_id}",
        f"{COLOR_BOLD}{COLOR_GREEN}Project:{COLOR_RESET}       {session.project_name}",
        f"{COLOR_BOLD}{COLOR_BLUE}Path:{COLOR_RESET}          {short_path}",
    ]

    if session.git_branch:
        lines.append(f"{COLOR_BOLD}{COLOR_GREEN}Branch:{COLOR_RESET}        {session.git_branch}")

    lines.extend(
        [
            f"{COLOR_BOLD}{COLOR_YELLOW}Time:{COLOR_RESET}          {time_str}",
            f"{COLOR_BOLD}{COLOR_GRAY}Messages:{COLOR_RESET}      {session.message_count}",
            "",
            f"{COLOR_BOLD}{COLOR_GRAY}First:{COLOR_RESET}",
            first_msg,
            "",
            f"{COLOR_BOLD}{COLOR_GRAY}Recent:{COLOR_RESET}",
            last_msg,
        ]
    )

    return "\n".join(lines)
