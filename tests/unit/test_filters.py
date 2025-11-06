"""Unit tests for filters module."""

from cc_fi.core.filters import BOILERPLATE_PATTERNS, BoilerplatePattern, is_boilerplate


def test_continuation_message_caveat():
    """Test filtering continuation message with 'Caveat:' prefix."""
    assert is_boilerplate("Caveat: messages below...")
    assert is_boilerplate("caveat: test")
    assert is_boilerplate("CAVEAT: uppercase")


def test_continuation_message_session_continued():
    """Test filtering 'this session is being continued' messages."""
    assert is_boilerplate("This session is being continued from previous...")
    assert is_boilerplate("this session is being continued")


def test_continuation_message_conversation_continued():
    """Test filtering 'this conversation is being continued' messages."""
    assert is_boilerplate("This conversation is being continued...")
    assert is_boilerplate("THIS CONVERSATION IS BEING CONTINUED")


def test_continuation_message_continuing_from():
    """Test filtering 'continuing from previous session' messages."""
    assert is_boilerplate("Continuing from previous session")
    assert is_boilerplate("continuing from previous session")


def test_command_invocation():
    """Test filtering command invocations with <command-name> tags."""
    assert is_boilerplate("<command-name>/clear</command-name>")
    assert is_boilerplate("<command-name>foo</command-name>")


def test_command_message():
    """Test filtering command messages with <command-message> tags."""
    assert is_boilerplate("<command-message>Running...</command-message>")
    assert is_boilerplate("<command-message>test</command-message>")


def test_local_command_output():
    """Test filtering local command output."""
    assert is_boilerplate("<local-command-output>")
    assert is_boilerplate("<local-command-foo>")


def test_openspec_comments():
    """Test filtering OpenSpec system comments."""
    assert is_boilerplate("<!-- OPENSPEC:START -->")
    assert is_boilerplate("<!-- OPENSPEC:END -->")
    assert is_boilerplate("<!-- OPENSPEC: some content -->")


def test_interruption_messages():
    """Test filtering request interrupted messages."""
    assert is_boilerplate("[Request interrupted by user]")
    assert is_boilerplate("[request interrupted by user]")
    assert is_boilerplate("[REQUEST INTERRUPTED BY USER]")


def test_not_boilerplate():
    """Test that normal user messages are not filtered."""
    assert not is_boilerplate("Normal user message")
    assert not is_boilerplate("Help me with this code")
    assert not is_boilerplate("Can you explain this?")


def test_empty_string():
    """Test empty string is not boilerplate."""
    assert not is_boilerplate("")
    assert not is_boilerplate("   ")
    assert not is_boilerplate("\n")


def test_whitespace_trimming():
    """Test that whitespace is trimmed before matching."""
    assert is_boilerplate("  caveat: test  ")
    assert is_boilerplate("\n\tcaveat: test\n")


def test_case_insensitive_prefix():
    """Test case-insensitive matching for prefix patterns."""
    assert is_boilerplate("CAVEAT: test")
    assert is_boilerplate("Caveat: Test")
    assert is_boilerplate("cAvEaT: test")


def test_xml_tag_pattern_type():
    """Test XML tag pattern matching."""
    pattern = BoilerplatePattern("xml_tag", "<test>", case_sensitive=True)
    assert pattern.pattern_type == "xml_tag"
    assert pattern.pattern == "<test>"
    assert pattern.case_sensitive is True


def test_boilerplate_pattern_registry():
    """Test that registry contains expected patterns."""
    assert len(BOILERPLATE_PATTERNS) >= 9
    pattern_types = {p.pattern_type for p in BOILERPLATE_PATTERNS}
    assert "prefix" in pattern_types
    assert "xml_tag" in pattern_types
    assert "comment" in pattern_types


def test_parser_integration():
    """Test that parser.is_boilerplate_message uses filter registry."""
    from cc_fi.core.parser import is_boilerplate_message

    # Should filter continuation messages
    assert is_boilerplate_message("Caveat: test")

    # Should filter command messages
    assert is_boilerplate_message("<command-name>test</command-name>")

    # Should not filter normal messages
    assert not is_boilerplate_message("Normal user message")
