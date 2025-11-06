"""Session data model and factory methods."""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class SessionData:
    """
    Represents a Claude Code session with metadata.

    @description Immutable data container for session information
    @complexity O(1) for all field access
    @pure true - dataclass is immutable
    """

    session_id: str
    cwd: str
    project_name: str
    git_branch: str
    timestamp: datetime
    first_message: str
    last_message: str
    message_count: int
    file_path: Path
    last_modified: float
    full_content: str = ""  # All user messages for deep search

    @property
    def content_fingerprint(self) -> tuple[str, str, str]:
        """
        Compute content fingerprint for deduplication.

        Fingerprint is based on timestamp, first message, and working directory
        to identify sessions with identical content but different session IDs.

        @returns Tuple of (timestamp_iso, first_message_prefix, cwd)
        @complexity O(1)
        @pure true
        """
        timestamp_iso = self.timestamp.isoformat()
        message_prefix = self.first_message[:100]
        return (timestamp_iso, message_prefix, self.cwd)

    @classmethod
    def from_jsonl_file(cls, file_path: Path) -> "SessionData":
        """
        Create SessionData from a Claude Code session JSONL file.

        @param file_path Path to .jsonl session file
        @returns SessionData instance with extracted metadata
        @throws FileNotFoundError When file doesn't exist
        @throws json.JSONDecodeError When first line is malformed
        @throws KeyError When required fields are missing

        @example
        session = SessionData.from_jsonl_file(Path("session.jsonl"))
        print(session.project_name)  # "my-project"

        @complexity O(n) where n is lines in file (for message count)
        @pure false - reads from filesystem
        """
        from cc_fi.core.parser import extract_metadata_from_file

        return extract_metadata_from_file(file_path)

    def to_dict(self) -> dict:
        """
        Convert SessionData to dictionary for serialization.

        @returns Dictionary with all fields, datetime as ISO string
        @complexity O(1)
        @pure true - no side effects
        """
        return {
            "session_id": self.session_id,
            "cwd": self.cwd,
            "project_name": self.project_name,
            "git_branch": self.git_branch,
            "timestamp": self.timestamp.isoformat(),
            "first_message": self.first_message,
            "last_message": self.last_message,
            "message_count": self.message_count,
            "file_path": str(self.file_path),
            "last_modified": self.last_modified,
            "full_content": self.full_content,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SessionData":
        """
        Create SessionData from dictionary (cache deserialization).

        @param data Dictionary with session fields
        @returns SessionData instance
        @throws KeyError When required fields are missing
        @throws ValueError When timestamp format is invalid

        @complexity O(1)
        @pure true - no side effects beyond object creation
        """
        return cls(
            session_id=data["session_id"],
            cwd=data["cwd"],
            project_name=data["project_name"],
            git_branch=data["git_branch"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            first_message=data["first_message"],
            last_message=data["last_message"],
            message_count=data["message_count"],
            file_path=Path(data["file_path"]),
            last_modified=data["last_modified"],
            full_content=data.get("full_content", ""),  # Backwards compatible
        )
