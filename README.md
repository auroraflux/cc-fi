# cc-fi

Ever done this?

```
❯ claude -r
No conversations found to resume
```

*"Ah crap, what directory did I run that Claude Code session in again!?"*

`cc-fi` fixes that. It's a fast, fuzzy search tool for finding your Claude Code sessions across your entire filesystem. Search through conversation history, jump straight into any session, and get warned if the directory's moved since you last worked there.

I built this with Claude Code because I kept losing track of my own sessions. It's vibe-coded, rough around the edges, and makes zero claims about being professional software. But it works really well for what I need.

Take it, break it, extend it. Whatever you want.

## Features

- **Interactive fuzzy search** - Type to filter sessions by project, path, or any message content
- **Deep search** - Searches entire conversation history, not just first/last messages
- **Live preview** - See session details with syntax highlighting as you browse
- **Fuzzy match highlighting** - Visual feedback showing exactly what matched your query
- **Smart resume** - One-step session resumption with directory handling
- **Cached indexing** - Sub-10ms search after initial scan
- **Dynamic columns** - Table adapts to terminal width for maximum content visibility

## Requirements

- Python 3.12+
- [fzf](https://github.com/junegunn/fzf) (for interactive mode)
- [fd](https://github.com/sharkdp/fd) (for directory browser)
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- [eza](https://github.com/eza-community/eza) (optional, for colored directory previews)

## Installation

### Option 1: pipx (Recommended)

**Works from anywhere, no venv activation needed:**

```bash
# From GitHub (when published)
pipx install git+https://github.com/auroraflux/cc-fi.git

# Or from local clone
git clone https://github.com/auroraflux/cc-fi.git
cd cc-fi
pipx install .

# Run from anywhere
cc-fi
```

**Installing pipx:**
```bash
brew install pipx      # macOS
apt install pipx       # Linux
pipx ensurepath        # Add to PATH
```

### Option 2: uv tool (Modern Alternative)

**Fast, isolated install:**

```bash
# From GitHub (when published)
uv tool install git+https://github.com/auroraflux/cc-fi.git

# Or from local clone
git clone https://github.com/auroraflux/cc-fi.git
cd cc-fi
uv tool install .

# Run from anywhere
cc-fi
```

### Option 3: Manual Install (Development)

**Interactive installer with multiple options:**

```bash
git clone https://github.com/auroraflux/cc-fi.git
cd cc-fi
./install.sh

# Follow prompts to choose:
#   1) pipx install (if available)
#   2) uv tool install (if available)
#   3) Manual with wrapper script at ~/.local/bin/cc-fi
```

**Manual installation creates a wrapper script so you can run `cc-fi` from anywhere without venv activation.**

### Installing Dependencies

**Required tools:**
```bash
# macOS (Homebrew)
brew install fzf fd eza

# Linux (Debian/Ubuntu)
apt install fzf fd-find
cargo install eza  # or download from GitHub releases
```

**Optional - Install pipx for easier management:**
```bash
brew install pipx && pipx ensurepath  # macOS
apt install pipx && pipx ensurepath   # Linux
```

## Usage

### Interactive Mode (Default)

```bash
cc-fi
```

**Interactive controls:**
- **Type** - Filter sessions by any content (project, path, messages)
- **↑/↓** - Navigate through sessions
- **Enter** - Select session to resume
- **Esc** - Cancel

**Preview pane features:**
- Shows project name, path, git branch, timestamp
- Displays first and last messages (up to 400 chars each)
- **Fuzzy highlighting** - Matched characters appear in red (same as table)
- **Deep search mode** - When typing, shows matching snippets from entire conversation

**Resume workflow:**
1. Select a session
2. Prompt: "Resume this session? (Y/n):"
3. Press Enter (or Y) to launch Claude Code
4. If original directory missing, choose:
   - Browse for new directory (fzf directory picker)
   - Run from current directory
   - Cancel

### List Mode

List all sessions:
```bash
cc-fi -l
```

Search sessions:
```bash
cc-fi -l search-term
```

### Cache Management

Force cache rebuild:
```bash
cc-fi -r
```

Clear cache:
```bash
cc-fi --clear-cache
```

Enable verbose logging:
```bash
cc-fi -v
```

## Configuration

**Cache settings** (`cc_fi/constants.py`):
```python
CACHE_TTL_SECONDS = 30  # Cache lifetime
CACHE_FILE_PATH = Path("/tmp/cc-fi-cache.json")  # Cache location
```

**Display settings** (`cc_fi/constants.py`):
```python
PROJECT_COLUMN_WIDTH = 20
PATH_COLUMN_WIDTH = 40
TIME_COLUMN_WIDTH = 16
MESSAGE_PREVIEW_LENGTH = 60  # Table truncation
MESSAGE_DETAIL_LENGTH = 400  # Preview/full text length
MAX_PREVIEW_MATCHES = 5  # Deep search results shown
```

## How It Works

### Architecture

1. **Scanner** - Reads `~/.claude/projects/*.jsonl` session files
2. **Parser** - Extracts metadata and indexes full conversation content
3. **Cache** - Stores parsed sessions for 30 seconds (invalidates on new sessions)
4. **Formatter** - Renders table and preview with ANSI colors
5. **FZF Integration** - Pipes formatted data to fzf with live preview

### Deep Search

cc-fi indexes **entire conversation history**, not just first/last messages:

**Indexed fields:**
- Project name
- Working directory path
- Git branch
- All user messages (full content)
- Session metadata

**Search modes:**

1. **Browse mode** (no query):
   - Shows first and last messages
   - Full metadata display

2. **Search mode** (typing query):
   - Filters table by fuzzy match
   - Preview shows matching snippets with context
   - Highlights matched characters in red
   - Shows up to 5 matches with 50-char context each

**Example:** Type "refactor api" to find any session where you discussed refactoring an API, even if that was in the middle of the conversation.

### Performance

- **First run**: ~1-2 seconds for 100+ sessions
- **Cached runs**: <10ms (instant)
- **Cache size**: ~1-2MB per 100 sessions
- **Search latency**: Real-time (fzf fuzzy matching)

### Missing Directory Handling

When a session's original directory no longer exists:

1. **Warning displayed**: "Original directory no longer exists: /path"
2. **Options menu**:
   - **Browse** - Interactive directory picker (fd + fzf)
     - Lists directories recursively
     - Type to filter by path segments
     - Preview shows directory contents
     - No depth limit - find any subdirectory
   - **Current** - Resume from current working directory
   - **Cancel** - Exit without resuming

Claude Code restores session context regardless of working directory, so resuming from a different location works correctly.

## Troubleshooting

**No sessions found:**
```bash
ls ~/.claude/projects  # Verify Claude Code installation
```

**fzf not found:**
```bash
brew install fzf  # macOS
apt install fzf   # Linux
```

**Icons show as boxes:**

Install a [NerdFont](https://www.nerdfonts.com/):
```bash
brew install --cask font-hack-nerd-font  # macOS
```

Then configure your terminal to use the NerdFont.

**fd not found:**
```bash
brew install fd  # macOS
apt install fd-find  # Linux (binary may be named fdfind)
```

**eza not found (optional):**

Directory previews fall back to `ls` if `eza` is unavailable. For colored previews:
```bash
brew install eza  # macOS
cargo install eza  # Linux
```

## Development

**Setup:**
```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

**Run tests:**
```bash
pytest tests/unit/ -v
```

**Format and lint:**
```bash
ruff check cc_fi/
mypy cc_fi/
```

**Project structure:**
```
cc-fi/
├── cc_fi/
│   ├── core/
│   │   ├── cache.py       # Session caching with TTL
│   │   ├── fzf.py         # FZF integration
│   │   ├── formatter.py   # ANSI formatting and fuzzy highlighting
│   │   ├── parser.py      # JSONL parsing and metadata extraction
│   │   └── search.py      # Session filtering
│   ├── models/
│   │   └── session.py     # SessionData model
│   ├── constants.py       # Configuration constants
│   └── main.py            # CLI entry point
├── tests/
│   └── unit/              # Unit tests
└── install.sh             # Installation script
```

## License

MIT
