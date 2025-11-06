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
    COLOR_RED,
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


def highlight_fuzzy_matches(text: str, query: str) -> str:
    """
    Highlight fuzzy matches of query in text with red color (fzf-style).

    Fuzzy matching finds query characters in order but not necessarily consecutive.
    Example: "test" fuzzy matches "template string" by finding t-e-s-t in order.

    @param text Text to search in
    @param query Search query
    @returns Text with fuzzy matches highlighted in red
    @complexity O(n*m) where n is text length, m is query length
    @pure true
    """
    if not query or not text:
        return text

    query_lower = query.lower()
    text_lower = text.lower()

    # Find positions of fuzzy matches (greedy: first occurrence of each char)
    matched_positions = []
    search_pos = 0

    for query_char in query_lower:
        # Find next occurrence of this character
        pos = text_lower.find(query_char, search_pos)
        if pos == -1:
            # No complete fuzzy match found, return text unchanged
            return text
        matched_positions.append(pos)
        search_pos = pos + 1

    # Build highlighted string by inserting ANSI color codes
    if not matched_positions:
        return text

    result = []
    last_pos = 0

    for pos in matched_positions:
        # Add text before match
        result.append(text[last_pos:pos])
        # Add highlighted character (red + bold for visibility)
        result.append(f"{COLOR_RED}{COLOR_BOLD}{text[pos]}{COLOR_RESET}")
        last_pos = pos + 1

    # Add remaining text
    result.append(text[last_pos:])

    return "".join(result)


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


def wrap_text_preserve_colors(text: str, width: int) -> str:
    """
    Wrap text to specified width while preserving existing ANSI color codes.

    Used for text that already has fuzzy match highlighting or other colors.
    Does not add a base color - preserves whatever colors are in the text.

    @param text Text to wrap (may contain ANSI color codes)
    @param width Maximum width per line
    @returns Multi-line string with existing color codes preserved
    @complexity O(n) where n is text length
    @pure true
    """
    normalized = normalize_whitespace(text)

    # Wrap the text - textwrap doesn't count ANSI codes toward width
    # so this works correctly even with color codes in the text
    wrapped_lines = textwrap.wrap(
        normalized,
        width=width,
        break_long_words=False,
        break_on_hyphens=False
    )

    return "\n".join(wrapped_lines)


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

    # Extract recent and first messages - use _full fields for table display
    # (first_message/last_message are pre-truncated to 60 chars, but dynamic
    # columns can be much wider, so use the 400-char _full fields instead)
    recent_msg = session.last_message_full.strip() if session.last_message_full else ""
    if not recent_msg:
        recent_msg = "(no recent message)"
    recent = truncate_message(recent_msg, recent_width).ljust(recent_width)

    first_msg = session.first_message_full.strip() if session.first_message_full else ""
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

    @returns Two-line string: instructions + search note
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
    # Note about search scope
    search_note = f"{COLOR_OVERLAY0}Searching visible fields + conversation content{COLOR_RESET}"

    return f"{instructions}\n{search_note}"


def format_fzf_preview(session: SessionData, query: str = "") -> str:
    """
    Format session details for fzf preview pane with NerdFont icons and fuzzy match highlighting.
    Layout matches table order: Project, Path, Time, Recent, First, Session ID, Message count.

    @param session SessionData to format
    @param query Search query for fuzzy match highlighting
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

    # Apply fuzzy match highlighting if query present
    if query:
        project_display = highlight_fuzzy_matches(session.project_name, query)
        path_display = highlight_fuzzy_matches(short_path, query)
        branch_display = highlight_fuzzy_matches(session.git_branch, query) if session.git_branch else ""

        # Highlight messages then add base color
        first_highlighted = highlight_fuzzy_matches(session.first_message_full, query)
        last_highlighted = highlight_fuzzy_matches(session.last_message_full, query)
        first_msg_wrapped = wrap_text_preserve_colors(first_highlighted, terminal_width)
        last_msg_wrapped = wrap_text_preserve_colors(last_highlighted, terminal_width)
    else:
        project_display = session.project_name
        path_display = short_path
        branch_display = session.git_branch if session.git_branch else ""
        first_msg_wrapped = wrap_colored_text(session.first_message_full, COLOR_LAVENDER, terminal_width)
        last_msg_wrapped = wrap_colored_text(session.last_message_full, COLOR_MAUVE, terminal_width)

    # Start with project, path, time (matching table order)
    # Values are colored to match their header color for easy visual correlation
    lines = [
        f"{COLOR_BOLD}{COLOR_GREEN}{ICON_PROJECT} Project:{COLOR_RESET}     {COLOR_GREEN}{project_display}{COLOR_RESET}",
        f"{COLOR_BOLD}{COLOR_BLUE}{ICON_FOLDER} Path:{COLOR_RESET}        {COLOR_BLUE}{path_display}{COLOR_RESET}",
    ]

    # Add branch if it exists (between path and time)
    if session.git_branch:
        lines.append(f"{COLOR_BOLD}{COLOR_GREEN}{ICON_BRANCH} Branch:{COLOR_RESET}      {COLOR_GREEN}{branch_display}{COLOR_RESET}")

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


def find_search_matches(text: str, query: str) -> list[tuple[int, int]]:
    """
    Find all case-insensitive matches of query in text.

    @param text Text to search in
    @param query Search query
    @returns List of (start, end) tuples for each match
    @complexity O(n*m) where n is text length, m is query length
    @pure true
    """
    if not query or not text:
        return []

    matches = []
    query_lower = query.lower()
    text_lower = text.lower()
    start = 0

    while True:
        pos = text_lower.find(query_lower, start)
        if pos == -1:
            break
        matches.append((pos, pos + len(query)))
        start = pos + 1

    return matches


def extract_match_context(text: str, match_start: int, match_end: int, context_chars: int) -> str:
    """
    Extract context around a match with ellipsis if truncated.

    @param text Full text
    @param match_start Start position of match
    @param match_end End position of match
    @param context_chars Characters to show before/after match
    @returns Formatted string with context
    @complexity O(n) where n is context size
    @pure true
    """
    # Calculate context boundaries
    start = max(0, match_start - context_chars)
    end = min(len(text), match_end + context_chars)

    # Extract context
    context = text[start:end]

    # Add ellipsis if truncated
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(text) else ""

    return f"{prefix}{context}{suffix}"


def format_search_preview(session: "SessionData", query: str) -> str:
    """
    Format preview pane with search-aware context showing matching snippets and fuzzy highlighting.

    @param session SessionData to format
    @param query Search query from fzf
    @returns Multi-line formatted string with metadata and matches
    @complexity O(n) where n is full_content length
    @pure false - reads terminal size
    """
    from cc_fi.constants import (
        MAX_PREVIEW_MATCHES,
        MATCH_CONTEXT_CHARS,
    )
    from cc_fi.models.session import SessionData

    try:
        terminal_width = shutil.get_terminal_size().columns
    except Exception:
        terminal_width = 120

    short_path = shorten_path(session.cwd)
    time_str = format_timestamp(session.timestamp)

    # Apply fuzzy highlighting to metadata
    project_display = highlight_fuzzy_matches(session.project_name, query)
    path_display = highlight_fuzzy_matches(short_path, query)
    branch_display = highlight_fuzzy_matches(session.git_branch, query) if session.git_branch else ""

    # Start with metadata (always shown)
    lines = [
        f"{COLOR_BOLD}{COLOR_GREEN}{ICON_PROJECT} Project:{COLOR_RESET}     {COLOR_GREEN}{project_display}{COLOR_RESET}",
        f"{COLOR_BOLD}{COLOR_BLUE}{ICON_FOLDER} Path:{COLOR_RESET}        {COLOR_BLUE}{path_display}{COLOR_RESET}",
    ]

    if session.git_branch:
        lines.append(f"{COLOR_BOLD}{COLOR_GREEN}{ICON_BRANCH} Branch:{COLOR_RESET}      {COLOR_GREEN}{branch_display}{COLOR_RESET}")

    lines.extend([
        f"{COLOR_BOLD}{COLOR_YELLOW}{ICON_CLOCK} Time:{COLOR_RESET}        {COLOR_YELLOW}{time_str}{COLOR_RESET}",
        f"{COLOR_BOLD}{COLOR_GRAY}{ICON_SESSION} Session:{COLOR_RESET}     {COLOR_GRAY}{session.session_id}{COLOR_RESET}",
        f"{COLOR_BOLD}{COLOR_GRAY}{ICON_COMMENT} Messages:{COLOR_RESET}    {COLOR_GRAY}{session.message_count}{COLOR_RESET}",
        "",
        f"{COLOR_OVERLAY0}{'─' * min(60, terminal_width)}{COLOR_RESET}",
        "",
    ])

    # Search for matches in full_content
    matches = find_search_matches(session.full_content, query)

    if not matches:
        # No deep matches found, show standard messages with fuzzy highlighting
        first_highlighted = highlight_fuzzy_matches(session.first_message_full, query)
        last_highlighted = highlight_fuzzy_matches(session.last_message_full, query)

        lines.extend([
            f"{COLOR_OVERLAY0}No deep matches found{COLOR_RESET}",
            "",
            f"{COLOR_BOLD}{COLOR_MAUVE}{ICON_RECENT} Recent Msg:{COLOR_RESET}",
            wrap_text_preserve_colors(last_highlighted, terminal_width),
            "",
            f"{COLOR_BOLD}{COLOR_LAVENDER}{ICON_FIRST} First Msg:{COLOR_RESET}",
            wrap_text_preserve_colors(first_highlighted, terminal_width),
        ])
    else:
        # Show matching snippets with fuzzy highlighting
        total_matches = len(matches)
        display_count = min(MAX_PREVIEW_MATCHES, total_matches)

        if total_matches > MAX_PREVIEW_MATCHES:
            lines.append(f"{COLOR_BOLD}{COLOR_CATPPUCCIN_BLUE} Matches ({total_matches} found, showing first {display_count}):{COLOR_RESET}")
        else:
            lines.append(f"{COLOR_BOLD}{COLOR_CATPPUCCIN_BLUE} Matches ({total_matches}):{COLOR_RESET}")

        lines.append("")

        # Show first N matches with context and fuzzy highlighting
        for i, (start, end) in enumerate(matches[:MAX_PREVIEW_MATCHES]):
            context = extract_match_context(session.full_content, start, end, MATCH_CONTEXT_CHARS)

            # Apply fuzzy highlighting to context
            context_highlighted = highlight_fuzzy_matches(context, query)

            # Wrap context to terminal width
            wrapped = wrap_text_preserve_colors(context_highlighted, terminal_width - 15)

            # Add match number prefix
            first_line = wrapped.split("\n")[0] if "\n" in wrapped else wrapped
            remaining_lines = "\n".join(wrapped.split("\n")[1:]) if "\n" in wrapped else ""

            lines.append(f"{COLOR_BOLD}{COLOR_LAVENDER} [Match {i+1}]{COLOR_RESET} {first_line}")
            if remaining_lines:
                # Indent continuation lines
                for line in remaining_lines.split("\n"):
                    lines.append(f"          {line}")
            lines.append("")

        if total_matches > MAX_PREVIEW_MATCHES:
            remaining = total_matches - MAX_PREVIEW_MATCHES
            lines.append(f"{COLOR_OVERLAY0} ({remaining} more match{'es' if remaining > 1 else ''} not shown){COLOR_RESET}")

    return "\n".join(lines)


def format_preview_with_query(session: "SessionData", query: str = "") -> str:
    """
    Format preview pane with fuzzy match highlighting, switching between standard and search mode.

    @param session SessionData to format
    @param query Optional search query from fzf for fuzzy highlighting
    @returns Multi-line formatted preview string with highlighted matches
    @complexity O(n) where n is content size
    @pure false - reads terminal size
    """
    from cc_fi.models.session import SessionData

    if query and query.strip():
        # Search mode: show matching snippets with fuzzy highlighting
        return format_search_preview(session, query.strip())
    else:
        # Browse mode: show standard preview (no highlighting when no query)
        return format_fzf_preview(session, "")
