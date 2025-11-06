# cc-fi - Claude Code Session Finder

Ultrafast CLI tool for discovering and resuming Claude Code sessions across all directories.

## Features

- **Fast Indexing**: Scans 100+ sessions in <1 second
- **Smart Caching**: 30-second TTL cache for instant results
- **Powerful Search**: Filter sessions by project, path, or message content
- **Interactive Mode**: Browse sessions with fzf preview pane
- **Clean Output**: Colored columnar display with aligned fields

## Installation

### Prerequisites

- Python 3.12+
- `fzf` (for interactive mode)
- `uv` (for Python environment management)
- NerdFont-patched terminal font (recommended for best visual experience)

```bash
# Install fzf
brew install fzf  # macOS
apt install fzf   # Linux

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install a NerdFont (optional but recommended)
brew install --cask font-hack-nerd-font  # macOS
# Or download from: https://www.nerdfonts.com/
```

### Install cc-fi

```bash
# Clone or navigate to cc-fi directory
cd /path/to/cc-fi

# Create virtual environment and install
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Usage

### List All Sessions

```bash
cc-fi
```

Shows all sessions sorted by last modified (newest first) with colored output:
- Green: Project name
- Blue: Directory path
- Yellow: Timestamp
- Mauve (purple): Recent message preview
- Lavender (light purple): First message preview

### Search Sessions

```bash
cc-fi openspec
```

Searches across all fields (project name, path, messages, etc.) - case insensitive.

### Interactive Mode

```bash
cc-fi -i
```

Launches fzf with:
- **Instruction header** showing keyboard shortcuts with Catppuccin colors: "Type to search | ↑↓ Navigate | ↵ Select | Esc Cancel"
- **Fixed column headers** with NerdFont icons: ` PROJECT`, ` PATH`, ` TIME`, ` RECENT`, ` FIRST`
- **Newest sessions first** - starts at the top of the list
- **Full-width columnar list** (60% height) with Catppuccin-themed colors
- **Bottom preview pane** (40% height) showing complete session details with color-matched labels
- **Type to search**, **arrow keys** to navigate, **Enter** to select, **Esc** to cancel

After selection, shows the resume command:
```bash
cd "/path/to/project" && claude -r <session-id>
```

### Force Rebuild Cache

```bash
cc-fi -r
```

Rebuilds the session index, bypassing cache.

### Clear Cache

```bash
cc-fi --clear-cache
```

Deletes the cache file.

### Verbose Logging

```bash
cc-fi -v
```

Shows detailed logging including indexing performance.

## Examples

```bash
# Find sessions related to "bug fix"
cc-fi "bug fix"

# Browse all sessions interactively
cc-fi -i

# Rebuild cache and search
cc-fi -r docker

# Check indexing performance
cc-fi -v -r
```

## Performance

- **Indexing**: ~135 sessions in 0.4-0.5 seconds
- **Cache Read**: <10ms
- **Search**: <100ms for any query

## How It Works

### Session Discovery

cc-fi scans `~/.claude/projects/` for all `.jsonl` conversation files, excluding:
- Agent sessions (`agent-*.jsonl`)
- Empty or malformed files

### Data Extraction

For each session, extracts:
- Session ID (for `claude -r`)
- Working directory and project name
- Git branch (if in repo)
- Timestamp of first user message
- First and most recent user messages
- Total message count

### Caching Strategy

- Cache location: `/tmp/cc-fi-cache.json`
- TTL: 30 seconds
- Automatic invalidation on expiry
- Manual rebuild with `-r` flag

## Development

### Run Tests

```bash
source .venv/bin/activate
pytest tests/unit/ -v
```

### Project Structure

```
cc-fi/
├── cc_fi/
│   ├── models/
│   │   └── session.py      # SessionData dataclass
│   ├── core/
│   │   ├── parser.py       # JSONL parsing
│   │   ├── indexer.py      # Session discovery
│   │   ├── cache.py        # Cache management
│   │   ├── search.py       # Filtering
│   │   ├── formatter.py    # Output formatting
│   │   └── fzf.py          # fzf integration
│   ├── constants.py        # Configuration constants
│   └── main.py             # CLI entry point
├── tests/
│   └── unit/               # Unit tests
├── pyproject.toml          # Project metadata
└── README.md               # This file
```

## Troubleshooting

### No sessions found

Ensure Claude Code is installed and you've run `claude` at least once:

```bash
ls ~/.claude/projects
```

### fzf not found (interactive mode)

Install fzf:

```bash
brew install fzf  # macOS
apt install fzf   # Linux
```

### Parsing warnings

Some sessions may fail to parse if they're empty or corrupted. These warnings are normal and don't affect functionality. Valid sessions are still indexed.

### Icons show as boxes or missing characters

cc-fi uses NerdFont icons for visual consistency. If you see boxes (□) or missing characters instead of bullets (`) in headers:

1. Install a NerdFont-patched font:
   ```bash
   brew install --cask font-hack-nerd-font  # macOS
   ```
   Or download from [nerdfonts.com](https://www.nerdfonts.com/)

2. Configure your terminal to use the NerdFont

The tool remains fully functional without NerdFonts - icons are purely visual enhancements.

### Colors look wrong or hard to read

cc-fi uses the Catppuccin Mocha color palette for enhanced visual hierarchy:

- **Mauve** (#c6a0f6): Recent messages - purple for creative/recent activity
- **Lavender** (#b7bdf8): First messages - light purple for historical context
- **Blue** (#8aadf4): Interactive highlights in instruction bar
- **Overlay0** (#6e738d): Subtle UI chrome text

**Best experience**: Use a terminal with Catppuccin theme (Mocha, Frappe, Macchiato, or Latte)
- [Catppuccin for iTerm2](https://github.com/catppuccin/iterm)
- [Catppuccin for other terminals](https://github.com/catppuccin/catppuccin)

**Color support**:
- 24-bit RGB terminals: Full Catppuccin colors (recommended)
- 256-color terminals: Graceful fallback to nearest colors
- 16-color terminals: Basic color fallback (purple → magenta)

The tool remains fully functional on any terminal - colors enhance readability but aren't required.

## Design Philosophy

This tool follows strict coding standards from `guidelines.md`:

- Functions under 20 lines
- No magic numbers (all constants extracted)
- Comprehensive error handling
- Type hints on all functions
- Extensive documentation
- Fast and memory-efficient

## License

MIT

## Related

- [Claude Code](https://docs.claude.com/en/docs/claude-code) - Official Claude CLI
- [Original bash version](./claude-session-finder-POSTMORTEM.md) - Why we rebuilt in Python
