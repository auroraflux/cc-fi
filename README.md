# cc-fi

Find and resume Claude Code sessions across all directories.

## Requirements

- Python 3.12+
- fzf (for interactive mode)
- uv (Python package manager)

## Installation

```bash
git clone https://github.com/yourusername/cc-fi.git
cd cc-fi
./install.sh
```

Or manually:

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Usage

Interactive browser (default):
```bash
cc-fi
```

List all sessions:
```bash
cc-fi -l
```

Search sessions:
```bash
cc-fi -l search-term
```

Force cache rebuild:
```bash
cc-fi -r
```

Clear cache:
```bash
cc-fi --clear-cache
```

## Configuration

Cache location: `/tmp/cc-fi-cache.json`
Cache TTL: 30 seconds

To change cache settings, edit `cc_fi/constants.py`:
```python
CACHE_TTL_SECONDS = 30
CACHE_FILE_PATH = Path("/tmp/cc-fi-cache.json")
```

## Development

Run tests:
```bash
source .venv/bin/activate
pytest tests/unit/ -v
```

Format and lint:
```bash
ruff check cc_fi/
mypy cc_fi/
```

## Troubleshooting

If no sessions found, check Claude Code installation:
```bash
ls ~/.claude/projects
```

If fzf not found:
```bash
brew install fzf  # macOS
apt install fzf   # Linux
```

If icons show as boxes, install a NerdFont:
```bash
brew install --cask font-hack-nerd-font  # macOS
```

Or download from https://www.nerdfonts.com/

## How It Works

cc-fi scans `~/.claude/projects/` for session files (`.jsonl`), extracts metadata (project name, working directory, messages), and caches results for 30 seconds. Interactive mode uses fzf for browsing with a preview pane.

Session files are discovered by:
- Scanning all subdirectories under `~/.claude/projects/`
- Excluding agent sessions (`agent-*.jsonl`)
- Parsing JSONL to extract first and most recent user messages

## License

MIT
