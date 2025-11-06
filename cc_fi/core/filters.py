"""Centralized filtering system for boilerplate messages."""

from dataclasses import dataclass


@dataclass
class BoilerplatePattern:
    """
    Registry entry for boilerplate message patterns.

    @param pattern_type Type of pattern: "prefix", "xml_tag", "comment"
    @param pattern Pattern string to match
    @param case_sensitive Whether matching is case-sensitive
    """

    pattern_type: str
    pattern: str
    case_sensitive: bool = False


# Centralized registry of boilerplate patterns
BOILERPLATE_PATTERNS = [
    # Continuation messages
    BoilerplatePattern("prefix", "caveat:", case_sensitive=False),
    BoilerplatePattern("prefix", "this session is being continued", case_sensitive=False),
    BoilerplatePattern(
        "prefix", "this conversation is being continued", case_sensitive=False
    ),
    BoilerplatePattern("prefix", "continuing from previous session", case_sensitive=False),
    # Command invocations
    BoilerplatePattern("xml_tag", "<command-name>", case_sensitive=True),
    BoilerplatePattern("xml_tag", "<command-message>", case_sensitive=True),
    BoilerplatePattern("prefix", "<local-command-", case_sensitive=True),
    # OpenSpec system messages
    BoilerplatePattern("comment", "<!-- OPENSPEC:", case_sensitive=True),
]


def matches_pattern(text: str, pattern: BoilerplatePattern) -> bool:
    """
    Check if text matches a boilerplate pattern.

    @param text Text to check
    @param pattern Pattern to match against
    @returns True if text matches pattern
    @complexity O(1)
    @pure true
    """
    text_to_check = text.strip()
    pattern_str = pattern.pattern

    if not pattern.case_sensitive:
        text_to_check = text_to_check.lower()
        pattern_str = pattern_str.lower()

    if pattern.pattern_type == "prefix":
        return text_to_check.startswith(pattern_str)
    elif pattern.pattern_type == "xml_tag":
        return pattern_str in text_to_check
    elif pattern.pattern_type == "comment":
        return text_to_check.startswith(pattern_str)

    return False


def is_boilerplate(text: str) -> bool:
    """
    Check if message text matches any boilerplate pattern.

    @param text Message text to check
    @returns True if text matches any registered pattern
    @complexity O(n) where n is number of patterns
    @pure true
    """
    for pattern in BOILERPLATE_PATTERNS:
        if matches_pattern(text, pattern):
            return True
    return False
