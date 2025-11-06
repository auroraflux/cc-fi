"""Unit tests for search module."""

from datetime import datetime
from pathlib import Path

from cc_fi.core.search import filter_sessions, matches_search_term
from cc_fi.models.session import SessionData


def test_matches_search_term_project_name():
    """Test search matches project name."""
    session = SessionData(
        session_id="abc123",
        cwd="/Users/test/project",
        project_name="test-project",
        git_branch="main",
        timestamp=datetime.now(),
        first_message="Hello",
        last_message="Goodbye",
        message_count=10,
        file_path=Path("/tmp/test.jsonl"),
        last_modified=0.0,
    )

    assert matches_search_term(session, "test-project")
    assert matches_search_term(session, "TEST")  # Case insensitive
    assert not matches_search_term(session, "nonexistent")


def test_matches_search_term_message_content():
    """Test search matches message content."""
    session = SessionData(
        session_id="abc123",
        cwd="/Users/test/project",
        project_name="project",
        git_branch="",
        timestamp=datetime.now(),
        first_message="This is a test message",
        last_message="Final words",
        message_count=10,
        file_path=Path("/tmp/test.jsonl"),
        last_modified=0.0,
    )

    assert matches_search_term(session, "test message")
    assert matches_search_term(session, "final")
    assert not matches_search_term(session, "xyz")


def test_filter_sessions_empty_term():
    """Test filter returns all sessions with empty search term."""
    sessions = [
        SessionData(
            session_id=f"id{i}",
            cwd=f"/path/{i}",
            project_name=f"project{i}",
            git_branch="",
            timestamp=datetime.now(),
            first_message=f"msg{i}",
            last_message="",
            message_count=1,
            file_path=Path(f"/tmp/{i}.jsonl"),
            last_modified=0.0,
        )
        for i in range(3)
    ]

    result = filter_sessions(sessions, "")
    assert len(result) == 3


def test_filter_sessions_with_term():
    """Test filter returns matching sessions only."""
    sessions = [
        SessionData(
            session_id="id1",
            cwd="/path/one",
            project_name="alpha",
            git_branch="",
            timestamp=datetime.now(),
            first_message="hello",
            last_message="",
            message_count=1,
            file_path=Path("/tmp/1.jsonl"),
            last_modified=0.0,
        ),
        SessionData(
            session_id="id2",
            cwd="/path/two",
            project_name="beta",
            git_branch="",
            timestamp=datetime.now(),
            first_message="world",
            last_message="",
            message_count=1,
            file_path=Path("/tmp/2.jsonl"),
            last_modified=0.0,
        ),
    ]

    result = filter_sessions(sessions, "alpha")
    assert len(result) == 1
    assert result[0].project_name == "alpha"
