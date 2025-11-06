"""Session discovery and indexing."""

import logging
from pathlib import Path

from cc_fi.constants import (
    AGENT_FILE_PREFIX,
    CLAUDE_PROJECTS_DIR,
    SESSION_FILE_EXTENSION,
)
from cc_fi.models.session import SessionData

logger = logging.getLogger(__name__)


def is_agent_file(file_path: Path) -> bool:
    """
    Check if file is an agent session (should be skipped).

    @param file_path Path to check
    @returns True if agent file, False otherwise
    @complexity O(1)
    @pure true
    """
    return file_path.name.startswith(AGENT_FILE_PREFIX)


def is_session_file(file_path: Path) -> bool:
    """
    Check if file is a valid session file to index.

    @param file_path Path to check
    @returns True if valid session file, False otherwise
    @complexity O(1)
    @pure true
    """
    if not file_path.is_file():
        return False
    if not file_path.suffix == SESSION_FILE_EXTENSION:
        return False
    if is_agent_file(file_path):
        return False
    return True


def find_session_files(projects_dir: Path) -> list[Path]:
    """
    Find all valid session files in projects directory.

    @param projects_dir Path to ~/.claude/projects
    @returns List of session file paths
    @throws FileNotFoundError When projects directory doesn't exist
    @complexity O(n) where n is total files in directory tree
    @pure false - reads filesystem
    """
    if not projects_dir.exists():
        raise FileNotFoundError(
            f"Claude projects directory not found: {projects_dir}. "
            "Ensure Claude Code is installed and has been run at least once."
        )

    session_files = []
    for file_path in projects_dir.rglob(f"*{SESSION_FILE_EXTENSION}"):
        if is_session_file(file_path):
            session_files.append(file_path)

    return session_files


def index_sessions(force_rebuild: bool = False) -> list[SessionData]:
    """
    Index all Claude Code sessions.

    @param force_rebuild If True, skip cache and rebuild index
    @returns List of SessionData objects sorted by last modified
    @throws FileNotFoundError When Claude directory doesn't exist
    @complexity O(n*m) where n=files, m=avg lines per file
    @pure false - reads filesystem
    """
    import time

    start_time = time.perf_counter()

    session_files = find_session_files(CLAUDE_PROJECTS_DIR)
    sessions = []

    for file_path in session_files:
        try:
            session = SessionData.from_jsonl_file(file_path)
            sessions.append(session)
        except Exception as e:
            logger.warning(f"Failed to parse {file_path}: {e}")
            continue

    sessions.sort(key=lambda s: s.last_modified, reverse=True)

    elapsed = time.perf_counter() - start_time
    logger.info(f"Indexed {len(sessions)} sessions in {elapsed:.2f}s")

    return sessions
