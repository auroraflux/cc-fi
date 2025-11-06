"""Session deduplication with configurable strategies."""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cc_fi.models.session import SessionData

logger = logging.getLogger(__name__)


class SessionDeduplicator:
    """Remove duplicate sessions using configurable strategy."""

    def deduplicate_by_session_id(
        self, sessions: list["SessionData"]
    ) -> list["SessionData"]:
        """
        Keep most recently modified file for each session_id.

        @param sessions List of sessions to deduplicate
        @returns Deduplicated list (session_id unique)
        @complexity O(n)
        @pure true
        """
        seen_ids: dict[str, "SessionData"] = {}

        for session in sessions:
            session_id = session.session_id
            if session_id not in seen_ids:
                seen_ids[session_id] = session
            else:
                # Keep the one with higher last_modified
                existing = seen_ids[session_id]
                if session.last_modified > existing.last_modified:
                    seen_ids[session_id] = session

        return list(seen_ids.values())

    def deduplicate_by_fingerprint(
        self, sessions: list["SessionData"]
    ) -> list["SessionData"]:
        """
        Remove sessions with identical content fingerprint.

        Fingerprint = (timestamp, first_message[:100], cwd)

        @param sessions List of sessions to deduplicate
        @returns Deduplicated list (fingerprint unique)
        @complexity O(n)
        @pure true
        """
        seen_fingerprints: dict[tuple, "SessionData"] = {}

        for session in sessions:
            fingerprint = session.content_fingerprint
            if fingerprint not in seen_fingerprints:
                seen_fingerprints[fingerprint] = session
            # Keep first occurrence, discard duplicates

        return list(seen_fingerprints.values())

    def deduplicate(
        self, sessions: list["SessionData"], strategy: str = "both"
    ) -> list["SessionData"]:
        """
        Apply deduplication strategy.

        @param sessions List of sessions to deduplicate
        @param strategy One of: "session_id", "fingerprint", "both", "none"
        @returns Deduplicated list based on strategy
        @complexity O(n)
        @pure true
        """
        original_count = len(sessions)

        if strategy == "none":
            return sessions

        if strategy == "session_id":
            result = self.deduplicate_by_session_id(sessions)
        elif strategy == "fingerprint":
            result = self.deduplicate_by_fingerprint(sessions)
        elif strategy == "both":
            # Apply both strategies sequentially
            result = self.deduplicate_by_session_id(sessions)
            result = self.deduplicate_by_fingerprint(result)
        else:
            logger.warning(f"Unknown deduplication strategy: {strategy}, using 'both'")
            result = self.deduplicate_by_session_id(sessions)
            result = self.deduplicate_by_fingerprint(result)

        removed_count = original_count - len(result)
        if removed_count > 0:
            logger.info(
                f"Deduplication ({strategy}): {original_count} → {len(result)} "
                f"sessions ({removed_count} duplicates removed)"
            )

        return result
