"""Session search and filtering."""

from cc_fi.models.session import SessionData


def matches_search_term(session: SessionData, search_term: str) -> bool:
    """
    Check if session matches search term (case insensitive).

    Searches across all indexed fields including:
    - Metadata: session_id, cwd, project_name, git_branch
    - Messages: first_message, last_message (visible in table)
    - Deep content: full_content (all user messages in conversation)

    @param session SessionData to check
    @param search_term Search string (case insensitive)
    @returns True if any field contains search term
    @complexity O(n) where n is total string length in session
    @pure true
    """
    search_lower = search_term.lower()

    fields_to_search = [
        session.session_id,
        session.cwd,
        session.project_name,
        session.git_branch,
        session.first_message,
        session.last_message,
        session.full_content,  # Deep search across all user messages
    ]

    for field in fields_to_search:
        if search_lower in field.lower():
            return True

    return False


def filter_sessions(
    sessions: list[SessionData], search_term: str
) -> list[SessionData]:
    """
    Filter sessions by search term across all fields.

    @param sessions List of sessions to filter
    @param search_term Search string (case insensitive)
    @returns Filtered list of matching sessions
    @complexity O(n*m) where n=sessions, m=avg field length
    @pure true
    """
    if not search_term:
        return sessions

    return [s for s in sessions if matches_search_term(s, search_term)]


def get_session_by_id(
    sessions: list[SessionData], session_id: str
) -> SessionData | None:
    """
    Find session by exact session ID match.

    @param sessions List of sessions to search
    @param session_id Session ID to find
    @returns SessionData if found, None otherwise
    @complexity O(n) where n is number of sessions
    @pure true
    """
    for session in sessions:
        if session.session_id == session_id:
            return session
    return None


def get_unique_projects(sessions: list[SessionData]) -> set[str]:
    """
    Extract unique project names from sessions.

    @param sessions List of sessions
    @returns Set of unique project names
    @complexity O(n) where n is number of sessions
    @pure true
    """
    return {session.project_name for session in sessions}
