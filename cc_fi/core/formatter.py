"""Output formatting for sessions."""

import shutil
import textwrap
from datetime import datetime
from pathlib import Path

from cc_fi.constants import (
    COLOR_BLUE,
    COLOR_BOLD,
    COLOR_CATPPUCCIN_BLUE,
    COLOR_GRAY,
    COLOR_GREEN,
    COLOR_LAVENDER,
    COLOR_MAUVE,
    COLOR_OVERLAY0,
    COLOR_RESET,
    COLOR_YELLOW,
    ICON_PROJECT,
    ICON_FOLDER,
    ICON_CLOCK,
    ICON_COMMENT,
    ICON_RECENT,
    ICON_FIRST,
    ICON_BRANCH,
    ICON_SESSION,
    MESSAGE_DETAIL_LENGTH,
    MESSAGE_PREVIEW_LENGTH,
    PATH_COLUMN_WIDTH,
    PROJECT_COLUMN_WIDTH,
    TIME_COLUMN_WIDTH,
)
from cc_fi.models.session import SessionData


def get_dynamic_column_widths() -> tuple[int, int]:
    """
    Calculate dynamic widths for RECENT and FIRST columns based on terminal width.

    @returns Tuple of (recent_width, first_width)
    @complexity O(1)
    @pure false - reads terminal size
    """
    try:
        terminal_width = shutil.get_terminal_size().columns
        # If terminal reports 80 (common fallback), assume modern wide terminal
        if terminal_width == 80:
            terminal_width = 200  # Modern terminals are typically 150-300 chars wide
    except Exception:
        terminal_width = 200  # Fallback to wide terminal assumption

    # Reserve space for fzf border (2 chars: 1 on each side) and some padding
    usable_width = terminal_width - 6  # 2 for border, 4 for safety margin and fzf padding

    # Fixed column widths + separators (2 spaces between each = 8 total)
    fixed_width = PROJECT_COLUMN_WIDTH + PATH_COLUMN_WIDTH + TIME_COLUMN_WIDTH + 8

    # Remaining space for RECENT and FIRST columns
    remaining = usable_width - fixed_width

    # If terminal is too narrow for fixed columns, use absolute minimum
    if remaining < 2:
        # Terminal can't even fit fixed columns - use bare minimum
        # This will still truncate but at least won't crash
        return (5, 5)

    # Split remaining space equally between RECENT and FIRST
    # Account for 2-space separator between them
    # Total: recent_width + 2 (separator) + first_width = remaining
    available_for_columns = max(remaining - 2, 10)  # At least 10 total for both columns

    recent_width = available_for_columns // 2
    first_width = available_for_columns - recent_width  # Give any extra char to FIRST

    return (recent_width, first_width)


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


def wrap_colored_text(text: str, color: str, width: int) -> str:
    """
    Wrap text to specified width while preserving color codes.

    @param text Text to wrap
    @param color ANSI color code to apply to wrapped lines
    @param width Maximum width per line
    @returns Multi-line string with color codes preserved
    @complexity O(n) where n is text length
    @pure true
    """
    normalized = normalize_whitespace(text)

    # Wrap the text
    wrapped_lines = textwrap.wrap(
        normalized,
        width=width,
        break_long_words=False,
        break_on_hyphens=False
    )

    # Apply color to each line
    colored_lines = [f"{color}{line}{COLOR_RESET}" for line in wrapped_lines]

    return "\n".join(colored_lines)


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
    @pure false - reads terminal size
    """
    recent_width, first_width = get_dynamic_column_widths()

    project = session.project_name[:PROJECT_COLUMN_WIDTH].ljust(PROJECT_COLUMN_WIDTH)
    path = shorten_path(session.cwd)[:PATH_COLUMN_WIDTH].ljust(PATH_COLUMN_WIDTH)
    time_str = format_timestamp(session.timestamp).ljust(TIME_COLUMN_WIDTH)

    # Extract recent and first messages
    recent_msg = session.last_message.strip() if session.last_message else ""
    if not recent_msg:
        recent_msg = "(no recent message)"
    recent = truncate_message(recent_msg, recent_width).ljust(recent_width)

    first_msg = session.first_message.strip() if session.first_message else ""
    if not first_msg:
        first_msg = "(no first message)"
    first = truncate_message(first_msg, first_width).ljust(first_width)

    return (
        f"{COLOR_GREEN}{project}{COLOR_RESET}  "
        f"{COLOR_BLUE}{path}{COLOR_RESET}  "
        f"{COLOR_YELLOW}{time_str}{COLOR_RESET}  "
        f"{COLOR_MAUVE}{recent}{COLOR_RESET}  "
        f"{COLOR_LAVENDER}{first}{COLOR_RESET}"
    )


def format_list_header() -> str:
    """
    Format header row for list view with bold colored columns and NerdFont icons.

    @returns Formatted header string with bold colors matching data columns
    @complexity O(1)
    @pure false - reads terminal size
    """
    recent_width, first_width = get_dynamic_column_widths()

    project = f"{ICON_PROJECT} PROJECT".ljust(PROJECT_COLUMN_WIDTH)
    path = f"{ICON_FOLDER} PATH".ljust(PATH_COLUMN_WIDTH)
    time_str = f"{ICON_CLOCK} TIME".ljust(TIME_COLUMN_WIDTH)
    recent = f"{ICON_RECENT} RECENT MSG".ljust(recent_width)
    first = f"{ICON_FIRST} FIRST MSG".ljust(first_width)

    return (
        f"{COLOR_BOLD}{COLOR_GREEN}{project}{COLOR_RESET}  "
        f"{COLOR_BOLD}{COLOR_BLUE}{path}{COLOR_RESET}  "
        f"{COLOR_BOLD}{COLOR_YELLOW}{time_str}{COLOR_RESET}  "
        f"{COLOR_BOLD}{COLOR_MAUVE}{recent}{COLOR_RESET}  "
        f"{COLOR_BOLD}{COLOR_LAVENDER}{first}{COLOR_RESET}"
    )


def format_header_separator() -> str:
    """
    Format separator line under header with colored spans.

    @returns Formatted separator line with colors matching columns
    @complexity O(1)
    @pure false - reads terminal size
    """
    recent_width, first_width = get_dynamic_column_widths()

    project_sep = "─" * PROJECT_COLUMN_WIDTH
    path_sep = "─" * PATH_COLUMN_WIDTH
    time_sep = "─" * TIME_COLUMN_WIDTH
    recent_sep = "─" * recent_width
    first_sep = "─" * first_width

    return (
        f"{COLOR_GREEN}{project_sep}{COLOR_RESET}  "
        f"{COLOR_BLUE}{path_sep}{COLOR_RESET}  "
        f"{COLOR_YELLOW}{time_sep}{COLOR_RESET}  "
        f"{COLOR_MAUVE}{recent_sep}{COLOR_RESET}  "
        f"{COLOR_LAVENDER}{first_sep}{COLOR_RESET}"
    )


def format_instruction_header() -> str:
    """
    Format instruction header with keyboard shortcuts for interactive mode.

    @returns Two-line string: instructions + separator
    @complexity O(1)
    @pure true
    """
    # Instruction text with Catppuccin Blue highlights for key terms
    instructions = (
        f"{COLOR_OVERLAY0}Type to {COLOR_CATPPUCCIN_BLUE}search{COLOR_OVERLAY0} | "
        f"↑↓ {COLOR_CATPPUCCIN_BLUE}Navigate{COLOR_OVERLAY0} | "
        f"↵ {COLOR_CATPPUCCIN_BLUE}Select{COLOR_OVERLAY0} | "
        f"Esc {COLOR_CATPPUCCIN_BLUE}Cancel{COLOR_RESET}"
    )
    separator = f"{COLOR_OVERLAY0}{'─' * 80}{COLOR_RESET}"

    return f"{instructions}\n{separator}"


def format_fzf_preview(session: SessionData) -> str:
    """
    Format session details for fzf preview pane with NerdFont icons.
    Layout matches table order: Project, Path, Time, Recent, First, Session ID, Message count.

    @param session SessionData to format
    @returns Multi-line formatted string
    @complexity O(n) where n is message length
    @pure false - reads terminal size
    """
    try:
        terminal_width = shutil.get_terminal_size().columns
    except Exception:
        terminal_width = 120  # Fallback width

    short_path = shorten_path(session.cwd)
    time_str = format_timestamp(session.timestamp)

    # Truncate to max detail length, then wrap to terminal width
    first_msg_truncated = truncate_message(session.first_message, MESSAGE_DETAIL_LENGTH)
    last_msg_truncated = truncate_message(session.last_message, MESSAGE_DETAIL_LENGTH)

    # Wrap the messages to terminal width with color
    first_msg_wrapped = wrap_colored_text(first_msg_truncated, COLOR_LAVENDER, terminal_width)
    last_msg_wrapped = wrap_colored_text(last_msg_truncated, COLOR_MAUVE, terminal_width)

    # Start with project, path, time (matching table order)
    # Values are colored to match their header color for easy visual correlation
    lines = [
        f"{COLOR_BOLD}{COLOR_GREEN}{ICON_PROJECT} Project:{COLOR_RESET}     {COLOR_GREEN}{session.project_name}{COLOR_RESET}",
        f"{COLOR_BOLD}{COLOR_BLUE}{ICON_FOLDER} Path:{COLOR_RESET}        {COLOR_BLUE}{short_path}{COLOR_RESET}",
    ]

    # Add branch if it exists (between path and time)
    if session.git_branch:
        lines.append(f"{COLOR_BOLD}{COLOR_GREEN}{ICON_BRANCH} Branch:{COLOR_RESET}      {COLOR_GREEN}{session.git_branch}{COLOR_RESET}")

    # Continue with time, recent, first (matching table order)
    lines.extend(
        [
            f"{COLOR_BOLD}{COLOR_YELLOW}{ICON_CLOCK} Time:{COLOR_RESET}        {COLOR_YELLOW}{time_str}{COLOR_RESET}",
            "",
            f"{COLOR_BOLD}{COLOR_MAUVE}{ICON_RECENT} Recent Msg:{COLOR_RESET}",
            last_msg_wrapped,
            "",
            f"{COLOR_BOLD}{COLOR_LAVENDER}{ICON_FIRST} First Msg:{COLOR_RESET}",
            first_msg_wrapped,
            "",
            f"{COLOR_BOLD}{COLOR_GRAY}{ICON_SESSION} Session:{COLOR_RESET}     {COLOR_GRAY}{session.session_id}{COLOR_RESET}",
            f"{COLOR_BOLD}{COLOR_GRAY}{ICON_COMMENT} Messages:{COLOR_RESET}    {COLOR_GRAY}{session.message_count}{COLOR_RESET}",
        ]
    )

    return "\n".join(lines)
