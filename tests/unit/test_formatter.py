"""Unit tests for formatter module."""

from datetime import datetime

from cc_fi.core.formatter import (
    format_timestamp,
    shorten_path,
    truncate_message,
)


def test_format_timestamp_12hour():
    """Test timestamp formatting in 12-hour format."""
    dt = datetime(2025, 11, 5, 22, 53, 41)
    result = format_timestamp(dt)
    assert result == "Nov 05, 10:53 PM"


def test_shorten_path_with_home():
    """Test path shortening replaces home directory."""
    from pathlib import Path

    home = str(Path.home())
    path = f"{home}/Tools/cc-fi"
    result = shorten_path(path)
    assert result == "~/Tools/cc-fi"


def test_shorten_path_without_home():
    """Test path shortening leaves non-home paths unchanged."""
    path = "/usr/local/bin"
    result = shorten_path(path)
    assert result == "/usr/local/bin"


def test_truncate_message_short():
    """Test message truncation with short message."""
    msg = "Hello world"
    result = truncate_message(msg, 20)
    assert result == "Hello world"


def test_truncate_message_long():
    """Test message truncation with long message."""
    msg = "A" * 100
    result = truncate_message(msg, 20)
    assert result == "A" * 17 + "..."
    assert len(result) == 20


def test_truncate_message_exact():
    """Test message truncation at exact length."""
    msg = "A" * 20
    result = truncate_message(msg, 20)
    assert result == msg


def test_truncate_message_with_newlines():
    """Test message truncation removes newlines."""
    msg = "Line 1\nLine 2\nLine 3"
    result = truncate_message(msg, 50)
    assert "\n" not in result
    assert result == "Line 1 Line 2 Line 3"


def test_truncate_message_with_multiple_spaces():
    """Test message truncation collapses multiple spaces."""
    msg = "Multiple   spaces   here"
    result = truncate_message(msg, 50)
    assert result == "Multiple spaces here"


def test_truncate_message_with_tabs():
    """Test message truncation replaces tabs."""
    msg = "Text\twith\ttabs"
    result = truncate_message(msg, 50)
    assert "\t" not in result
    assert result == "Text with tabs"


def test_fzf_preview_colors_match_columns():
    """Test that preview headers are bold and color-matched with column headers."""
    from datetime import datetime
    from pathlib import Path

    from cc_fi.constants import (
        COLOR_BLUE,
        COLOR_BOLD,
        COLOR_GRAY,
        COLOR_GREEN,
        COLOR_LAVENDER,
        COLOR_MAUVE,
        COLOR_YELLOW,
        ICON_PROJECT,
        ICON_FOLDER,
        ICON_CLOCK,
        ICON_COMMENT,
        ICON_RECENT,
        ICON_FIRST,
        ICON_BRANCH,
        ICON_SESSION,
    )
    from cc_fi.core.formatter import format_fzf_preview
    from cc_fi.models.session import SessionData

    session = SessionData(
        session_id="test-123",
        cwd="/Users/test/project",
        project_name="project",
        git_branch="main",
        timestamp=datetime(2025, 11, 5, 22, 53, 41),
        first_message="Test message",
        last_message="Last message",
        message_count=10,
        file_path=Path("/tmp/test.jsonl"),
        last_modified=1000.0,
    )

    result = format_fzf_preview(session)

    # Check that headers are bold and color-matched with specific icons
    assert f"{COLOR_BOLD}{COLOR_GRAY}{ICON_SESSION} Session:" in result
    assert f"{COLOR_BOLD}{COLOR_GREEN}{ICON_PROJECT} Project:" in result
    assert f"{COLOR_BOLD}{COLOR_BLUE}{ICON_FOLDER} Path:" in result
    assert f"{COLOR_BOLD}{COLOR_GREEN}{ICON_BRANCH} Branch:" in result
    assert f"{COLOR_BOLD}{COLOR_YELLOW}{ICON_CLOCK} Time:" in result
    assert f"{COLOR_BOLD}{COLOR_GRAY}{ICON_COMMENT} Messages:" in result
    assert f"{COLOR_BOLD}{COLOR_LAVENDER}{ICON_FIRST} First:" in result
    assert f"{COLOR_BOLD}{COLOR_MAUVE}{ICON_RECENT} Recent:" in result


def test_list_header_has_icons_and_path():
    """Test that list headers have NerdFont icons and use PATH terminology."""
    from cc_fi.constants import ICON_PROJECT, ICON_FOLDER, ICON_CLOCK, ICON_RECENT, ICON_FIRST
    from cc_fi.core.formatter import format_list_header

    header = format_list_header()

    # Check specific icons are present
    assert ICON_PROJECT in header
    assert ICON_FOLDER in header
    assert ICON_CLOCK in header
    assert ICON_RECENT in header
    assert ICON_FIRST in header

    # Check terminology
    assert "PROJECT" in header
    assert "PATH" in header
    assert "TIME" in header
    assert "RECENT" in header
    assert "FIRST" in header

    # Ensure old DIRECTORY and "FIRST MESSAGE" terminology is gone
    assert "DIRECTORY" not in header
    assert "FIRST MESSAGE" not in header


def test_instruction_header_format():
    """Test that instruction header has proper format and content."""
    from cc_fi.constants import COLOR_OVERLAY0, COLOR_CATPPUCCIN_BLUE, COLOR_RESET
    from cc_fi.core.formatter import format_instruction_header

    result = format_instruction_header()

    # Should be two lines (instruction + separator)
    lines = result.split("\n")
    assert len(lines) == 2

    # First line should contain keyboard shortcuts
    assert "Type to search" in lines[0] or "search" in lines[0]
    assert "Navigate" in lines[0]
    assert "Select" in lines[0]
    assert "Cancel" in lines[0]

    # Second line should be a separator
    assert "─" in lines[1]

    # Should use Catppuccin Overlay0 and Blue colors
    assert COLOR_OVERLAY0 in result
    assert COLOR_CATPPUCCIN_BLUE in result
    assert COLOR_RESET in result
