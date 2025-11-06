"""Unit tests for deduplicator module."""

from datetime import datetime
from pathlib import Path

from cc_fi.core.deduplicator import SessionDeduplicator
from cc_fi.models.session import SessionData


def create_test_session(
    session_id: str,
    timestamp: str,
    first_message: str,
    cwd: str,
    last_modified: float,
) -> SessionData:
    """Helper to create test SessionData."""
    return SessionData(
        session_id=session_id,
        cwd=cwd,
        project_name="test",
        git_branch="main",
        timestamp=datetime.fromisoformat(timestamp),
        first_message=first_message,
        last_message="last",
        message_count=5,
        file_path=Path("/tmp/test.jsonl"),
        last_modified=last_modified,
    )


def test_deduplicate_by_session_id_keeps_most_recent():
    """Test that duplicate session IDs keep most recent file."""
    deduplicator = SessionDeduplicator()

    sessions = [
        create_test_session(
            "abc123", "2025-11-05T10:00:00", "Message 1", "/Users/foo", 1000.0
        ),
        create_test_session(
            "abc123", "2025-11-05T10:00:00", "Message 1", "/Users/bar", 2000.0
        ),
        create_test_session(
            "def456", "2025-11-05T11:00:00", "Message 2", "/Users/baz", 1500.0
        ),
    ]

    result = deduplicator.deduplicate_by_session_id(sessions)

    assert len(result) == 2
    # Should keep session with highest last_modified for abc123
    abc_session = [s for s in result if s.session_id == "abc123"][0]
    assert abc_session.last_modified == 2000.0
    assert abc_session.cwd == "/Users/bar"


def test_deduplicate_by_session_id_multiple_duplicates():
    """Test deduplication with multiple duplicate IDs."""
    deduplicator = SessionDeduplicator()

    sessions = [
        create_test_session(
            "xyz", "2025-11-05T10:00:00", "Message 1", "/Users/a", 1000.0
        ),
        create_test_session(
            "xyz", "2025-11-05T10:00:00", "Message 1", "/Users/b", 1500.0
        ),
        create_test_session(
            "xyz", "2025-11-05T10:00:00", "Message 1", "/Users/c", 2000.0
        ),
    ]

    result = deduplicator.deduplicate_by_session_id(sessions)

    assert len(result) == 1
    assert result[0].last_modified == 2000.0
    assert result[0].cwd == "/Users/c"


def test_deduplicate_by_session_id_no_duplicates():
    """Test that unique session IDs are all retained."""
    deduplicator = SessionDeduplicator()

    sessions = [
        create_test_session(
            "abc", "2025-11-05T10:00:00", "Message 1", "/Users/foo", 1000.0
        ),
        create_test_session(
            "def", "2025-11-05T11:00:00", "Message 2", "/Users/bar", 2000.0
        ),
        create_test_session(
            "ghi", "2025-11-05T12:00:00", "Message 3", "/Users/baz", 3000.0
        ),
    ]

    result = deduplicator.deduplicate_by_session_id(sessions)

    assert len(result) == 3


def test_deduplicate_by_fingerprint_same_content():
    """Test fingerprint deduplication with identical content."""
    deduplicator = SessionDeduplicator()

    sessions = [
        create_test_session(
            "abc123",
            "2025-11-05T10:00:00",
            "Help me with code",
            "/Users/foo",
            1000.0,
        ),
        create_test_session(
            "def456",
            "2025-11-05T10:00:00",
            "Help me with code",
            "/Users/foo",
            2000.0,
        ),
    ]

    result = deduplicator.deduplicate_by_fingerprint(sessions)

    assert len(result) == 1
    # Should keep first occurrence
    assert result[0].session_id == "abc123"


def test_deduplicate_by_fingerprint_different_cwd():
    """Test that different cwd results in different fingerprints."""
    deduplicator = SessionDeduplicator()

    sessions = [
        create_test_session(
            "abc123",
            "2025-11-05T10:00:00",
            "Help me with code",
            "/Users/foo",
            1000.0,
        ),
        create_test_session(
            "def456",
            "2025-11-05T10:00:00",
            "Help me with code",
            "/Users/bar",
            2000.0,
        ),
    ]

    result = deduplicator.deduplicate_by_fingerprint(sessions)

    assert len(result) == 2  # Both kept due to different cwd


def test_deduplicate_by_fingerprint_different_timestamp():
    """Test that different timestamp results in different fingerprints."""
    deduplicator = SessionDeduplicator()

    sessions = [
        create_test_session(
            "abc123",
            "2025-11-05T10:00:00",
            "Help me with code",
            "/Users/foo",
            1000.0,
        ),
        create_test_session(
            "def456",
            "2025-11-05T11:00:00",
            "Help me with code",
            "/Users/foo",
            2000.0,
        ),
    ]

    result = deduplicator.deduplicate_by_fingerprint(sessions)

    assert len(result) == 2  # Both kept due to different timestamp


def test_deduplicate_strategy_session_id():
    """Test deduplication with session_id strategy."""
    deduplicator = SessionDeduplicator()

    sessions = [
        create_test_session(
            "abc", "2025-11-05T10:00:00", "Message 1", "/Users/foo", 1000.0
        ),
        create_test_session(
            "abc", "2025-11-05T10:00:00", "Message 1", "/Users/bar", 2000.0
        ),
    ]

    result = deduplicator.deduplicate(sessions, strategy="session_id")

    assert len(result) == 1


def test_deduplicate_strategy_fingerprint():
    """Test deduplication with fingerprint strategy."""
    deduplicator = SessionDeduplicator()

    sessions = [
        create_test_session(
            "abc", "2025-11-05T10:00:00", "Message 1", "/Users/foo", 1000.0
        ),
        create_test_session(
            "def", "2025-11-05T10:00:00", "Message 1", "/Users/foo", 2000.0
        ),
    ]

    result = deduplicator.deduplicate(sessions, strategy="fingerprint")

    assert len(result) == 1


def test_deduplicate_strategy_both():
    """Test deduplication with both strategy."""
    deduplicator = SessionDeduplicator()

    sessions = [
        # Same session_id, different files
        create_test_session(
            "abc", "2025-11-05T10:00:00", "Message 1", "/Users/foo", 1000.0
        ),
        create_test_session(
            "abc", "2025-11-05T10:00:00", "Message 1", "/Users/bar", 2000.0
        ),
        # Different session_id, same content
        create_test_session(
            "def", "2025-11-05T10:00:00", "Message 1", "/Users/bar", 3000.0
        ),
    ]

    result = deduplicator.deduplicate(sessions, strategy="both")

    assert len(result) == 1  # All duplicates removed


def test_deduplicate_strategy_none():
    """Test deduplication with none strategy."""
    deduplicator = SessionDeduplicator()

    sessions = [
        create_test_session(
            "abc", "2025-11-05T10:00:00", "Message 1", "/Users/foo", 1000.0
        ),
        create_test_session(
            "abc", "2025-11-05T10:00:00", "Message 1", "/Users/bar", 2000.0
        ),
    ]

    result = deduplicator.deduplicate(sessions, strategy="none")

    assert len(result) == 2  # No deduplication


def test_deduplicate_unknown_strategy_uses_both():
    """Test that unknown strategy defaults to 'both'."""
    deduplicator = SessionDeduplicator()

    sessions = [
        create_test_session(
            "abc", "2025-11-05T10:00:00", "Message 1", "/Users/foo", 1000.0
        ),
        create_test_session(
            "abc", "2025-11-05T10:00:00", "Message 1", "/Users/bar", 2000.0
        ),
    ]

    result = deduplicator.deduplicate(sessions, strategy="unknown")

    assert len(result) == 1  # Should apply both strategies


def test_content_fingerprint_property():
    """Test SessionData.content_fingerprint property."""
    session = create_test_session(
        "abc123",
        "2025-11-05T10:00:00",
        "This is a test message",
        "/Users/foo",
        1000.0,
    )

    fingerprint = session.content_fingerprint

    assert isinstance(fingerprint, tuple)
    assert len(fingerprint) == 3
    assert fingerprint[0] == "2025-11-05T10:00:00"  # timestamp
    assert fingerprint[1] == "This is a test message"  # first_message[:100]
    assert fingerprint[2] == "/Users/foo"  # cwd


def test_content_fingerprint_truncates_long_message():
    """Test that content fingerprint truncates long messages to 100 chars."""
    long_message = "A" * 150

    session = create_test_session(
        "abc123", "2025-11-05T10:00:00", long_message, "/Users/foo", 1000.0
    )

    fingerprint = session.content_fingerprint

    assert len(fingerprint[1]) == 100
    assert fingerprint[1] == "A" * 100
