"""Constants for cc-fi application."""

from pathlib import Path

# Cache settings
CACHE_TTL_SECONDS = 30
CACHE_FILE_PATH = Path("/tmp/cc-fi-cache.json")

# Session settings
CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"
AGENT_FILE_PREFIX = "agent-"
SESSION_FILE_EXTENSION = ".jsonl"

# Message truncation
MESSAGE_PREVIEW_LENGTH = 60
MESSAGE_DETAIL_LENGTH = 400  # Doubled from 200 for more preview content

# Display settings
PROJECT_COLUMN_WIDTH = 20
PATH_COLUMN_WIDTH = 40  # Reduced to fit RECENT column
TIME_COLUMN_WIDTH = 16
RECENT_COLUMN_WIDTH = 40  # New column for recent message
FIRST_COLUMN_WIDTH = 50  # Renamed from MESSAGE_COLUMN_WIDTH, reduced

# ANSI color codes (per CLAUDE.md: no emoji, ASCII/ANSI allowed)
COLOR_GREEN = "\033[32m"
COLOR_BLUE = "\033[34m"
COLOR_YELLOW = "\033[33m"
COLOR_GRAY = "\033[90m"
COLOR_BOLD = "\033[1m"
COLOR_RESET = "\033[0m"

# Catppuccin Mocha color palette (24-bit RGB)
COLOR_MAUVE = "\033[38;2;198;160;246m"  # #c6a0f6 - Recent messages
COLOR_LAVENDER = "\033[38;2;183;189;248m"  # #b7bdf8 - First messages
COLOR_OVERLAY0 = "\033[38;2;110;115;141m"  # #6e738d - Instruction text
COLOR_CATPPUCCIN_BLUE = "\033[38;2;138;173;244m"  # #8aadf4 - Highlights

# NerdFont icons (requires NerdFont-patched terminal font)
ICON_PROJECT = "\ueb30"  # U+EB30 (nf-cod-project)
ICON_FOLDER = "\uea83"    # U+EA83 (nf-cod-folder)
ICON_CLOCK = "\uf017"      # U+F017 (nf-fa-clock)
ICON_COMMENT = "\uea6b"  # U+EA6B (nf-cod-comment)
ICON_BRANCH = "\ue725"    # U+E725 (nf-dev-git_branch)
ICON_RECENT = "\uf27b"  # U+F27B (nf-fa-comment_dots)
ICON_FIRST = "\uf4ad"    # U+F4AD (nf-fa-comment_alt)
ICON_SESSION = "\uf15c"  # U+F15C (nf-fa-file_text)



# FZF settings
FZF_PREVIEW_HEIGHT_PERCENT = 40  # Preview pane height (bottom position)
FZF_HEIGHT_PERCENT = 100

# Performance limits
MAX_TAIL_LINES_FOR_LAST_MSG = 200  # Increased for sessions with many tool results

# Deduplication settings
DEDUPLICATION_STRATEGY = "both"  # Options: "session_id", "fingerprint", "both", "none"
BOILERPLATE_PATTERNS_FILE = None  # Optional: Load patterns from external file (future)
