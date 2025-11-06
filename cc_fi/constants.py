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
MESSAGE_DETAIL_LENGTH = 200

# Display settings
PROJECT_COLUMN_WIDTH = 20
PATH_COLUMN_WIDTH = 45
TIME_COLUMN_WIDTH = 16
MESSAGE_COLUMN_WIDTH = 60

# ANSI color codes (per CLAUDE.md: no emoji, ASCII/ANSI allowed)
COLOR_GREEN = "\033[32m"
COLOR_BLUE = "\033[34m"
COLOR_YELLOW = "\033[33m"
COLOR_GRAY = "\033[90m"
COLOR_BOLD = "\033[1m"
COLOR_RESET = "\033[0m"

# NerdFont icons (requires NerdFont-patched terminal font)
ICON_BULLET = " "  # U+F444 (nf-oct-dot_fill) - consistent bullet style

# FZF settings
FZF_PREVIEW_WIDTH_PERCENT = 50
FZF_HEIGHT_PERCENT = 100

# Performance limits
MAX_TAIL_LINES_FOR_LAST_MSG = 50

# Deduplication settings
DEDUPLICATION_STRATEGY = "both"  # Options: "session_id", "fingerprint", "both", "none"
BOILERPLATE_PATTERNS_FILE = None  # Optional: Load patterns from external file (future)
