"""Cache management with TTL and invalidation."""

import json
import logging
import time
from pathlib import Path

from cc_fi.constants import (
    CACHE_FILE_PATH,
    CACHE_TTL_SECONDS,
    DEDUPLICATION_STRATEGY,
)
from cc_fi.models.session import SessionData

logger = logging.getLogger(__name__)


def is_cache_valid(cache_path: Path, ttl_seconds: int) -> bool:
    """
    Check if cache file exists and is within TTL.

    @param cache_path Path to cache file
    @param ttl_seconds Time-to-live in seconds
    @returns True if cache is valid, False otherwise
    @complexity O(1)
    @pure false - checks filesystem
    """
    if not cache_path.exists():
        return False

    cache_age = time.time() - cache_path.stat().st_mtime
    return cache_age < ttl_seconds


def load_cache(cache_path: Path) -> list[SessionData]:
    """
    Load sessions from cache file.

    @param cache_path Path to cache file
    @returns List of SessionData objects
    @throws FileNotFoundError When cache doesn't exist
    @throws json.JSONDecodeError When cache is malformed
    @complexity O(n) where n is number of sessions
    @pure false - reads filesystem
    """
    with cache_path.open("r", encoding="utf-8") as f:
        cache_data = json.load(f)

    sessions = [SessionData.from_dict(item) for item in cache_data["sessions"]]
    logger.info(f"Loaded {len(sessions)} sessions from cache")
    return sessions


def save_cache(sessions: list[SessionData], cache_path: Path) -> None:
    """
    Save sessions to cache file.

    @param sessions List of SessionData to cache
    @param cache_path Path to cache file
    @throws OSError When cache directory is not writable
    @complexity O(n) where n is number of sessions
    @pure false - writes to filesystem
    """
    cache_data = {
        "timestamp": time.time(),
        "sessions": [session.to_dict() for session in sessions],
    }

    cache_path.parent.mkdir(parents=True, exist_ok=True)

    with cache_path.open("w", encoding="utf-8") as f:
        json.dump(cache_data, f, indent=2)

    logger.info(f"Cached {len(sessions)} sessions to {cache_path}")


def has_content(session: SessionData) -> bool:
    """
    Check if session has any meaningful content.

    @param session SessionData to check
    @returns True if session has user messages, False otherwise
    @complexity O(1)
    @pure true
    """
    return bool(session.first_message.strip() or session.last_message.strip())


def filter_empty_sessions(sessions: list[SessionData]) -> list[SessionData]:
    """
    Filter out sessions with no user messages.

    @param sessions List of sessions to filter
    @returns List of sessions with content only
    @complexity O(n) where n is number of sessions
    @pure true
    """
    return [s for s in sessions if has_content(s)]


def sort_sessions_by_recency(sessions: list[SessionData]) -> list[SessionData]:
    """
    Sort sessions by most recent first (last_modified descending).

    @param sessions List of sessions to sort
    @returns Sorted list with newest sessions first
    @complexity O(n log n) where n is number of sessions
    @pure true - does not modify input list
    """
    return sorted(sessions, key=lambda s: s.last_modified, reverse=True)


def get_sessions_with_cache(force_rebuild: bool = False) -> list[SessionData]:
    """
    Get sessions using cache if valid, otherwise rebuild.

    Applies deduplication before filtering and caching.

    @param force_rebuild Force cache rebuild if True
    @returns List of SessionData with content, sorted by recency
    @complexity O(n*m) worst case (rebuild), O(n log n) best case (cache)
    @pure false - may read/write filesystem
    """
    from cc_fi.core.deduplicator import SessionDeduplicator
    from cc_fi.core.indexer import index_sessions

    cache_path = CACHE_FILE_PATH
    ttl = CACHE_TTL_SECONDS

    if not force_rebuild and is_cache_valid(cache_path, ttl):
        try:
            sessions = load_cache(cache_path)
            sessions = filter_empty_sessions(sessions)
            return sort_sessions_by_recency(sessions)
        except Exception as e:
            logger.warning(f"Cache load failed: {e}, rebuilding")

    sessions = index_sessions(force_rebuild=force_rebuild)

    # Deduplicate before filtering empty sessions
    deduplicator = SessionDeduplicator()
    sessions = deduplicator.deduplicate(sessions, strategy=DEDUPLICATION_STRATEGY)

    sessions = filter_empty_sessions(sessions)
    save_cache(sessions, cache_path)
    return sessions


def invalidate_cache(cache_path: Path = CACHE_FILE_PATH) -> None:
    """
    Delete cache file if it exists.

    @param cache_path Path to cache file
    @complexity O(1)
    @pure false - modifies filesystem
    """
    if cache_path.exists():
        cache_path.unlink()
        logger.info(f"Cache invalidated: {cache_path}")
