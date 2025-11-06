"""Unit tests for parser module."""

import json
from pathlib import Path

import pytest

from cc_fi.core.parser import extract_project_name, is_tool_result_message


def test_extract_project_name_simple_path():
    """Test extracting project name from simple path."""
    cwd = str(Path("projects") / "cc-fi")
    result = extract_project_name(cwd)
    assert result == "cc-fi"


def test_extract_project_name_with_trailing_slash():
    """Test extracting project name with trailing slash."""
    cwd = str(Path("projects") / "cc-fi") + "/"
    result = extract_project_name(cwd)
    assert result == "cc-fi"  # Path handles trailing slashes correctly


def test_extract_project_name_root():
    """Test extracting project name from root directory."""
    cwd = "/"
    result = extract_project_name(cwd)
    assert result == ""


def test_is_tool_result_message_pure_tool_result():
    """Test that pure tool result messages are identified."""
    data = {
        "type": "user",
        "message": {
            "content": [
                {
                    "type": "tool_result",
                    "content": "command output",
                    "tool_use_id": "toolu_123",
                    "is_error": False
                }
            ]
        }
    }
    assert is_tool_result_message(data) is True


def test_is_tool_result_message_pure_text():
    """Test that user text messages are not identified as tool results."""
    data = {
        "type": "user",
        "message": {
            "content": [
                {
                    "type": "text",
                    "text": "User's actual message"
                }
            ]
        }
    }
    assert is_tool_result_message(data) is False


def test_is_tool_result_message_mixed_content():
    """Test that mixed content messages are not identified as tool results."""
    data = {
        "type": "user",
        "message": {
            "content": [
                {
                    "type": "text",
                    "text": "Look at this output:"
                },
                {
                    "type": "tool_result",
                    "content": "command output",
                    "tool_use_id": "toolu_123"
                }
            ]
        }
    }
    assert is_tool_result_message(data) is False


def test_is_tool_result_message_empty_content():
    """Test that empty content is handled safely."""
    data = {
        "type": "user",
        "message": {
            "content": []
        }
    }
    assert is_tool_result_message(data) is False


def test_is_tool_result_message_malformed_content():
    """Test that malformed content is handled safely."""
    # Content is not a list
    data = {
        "type": "user",
        "message": {
            "content": "string instead of array"
        }
    }
    assert is_tool_result_message(data) is False

    # No content field
    data2 = {
        "type": "user",
        "message": {}
    }
    assert is_tool_result_message(data2) is False

    # No message field
    data3 = {
        "type": "user"
    }
    assert is_tool_result_message(data3) is False


def test_is_tool_result_message_multiple_tool_results():
    """Test that messages with multiple tool results are identified."""
    data = {
        "type": "user",
        "message": {
            "content": [
                {
                    "type": "tool_result",
                    "content": "output 1",
                    "tool_use_id": "toolu_123"
                },
                {
                    "type": "tool_result",
                    "content": "output 2",
                    "tool_use_id": "toolu_456"
                }
            ]
        }
    }
    assert is_tool_result_message(data) is True
