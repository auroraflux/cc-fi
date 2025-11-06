"""Unit tests for parser module."""

import json
from pathlib import Path

import pytest

from cc_fi.core.parser import extract_project_name


def test_extract_project_name_simple_path():
    """Test extracting project name from simple path."""
    cwd = "/Users/harsha/Tools/cc-fi"
    result = extract_project_name(cwd)
    assert result == "cc-fi"


def test_extract_project_name_with_trailing_slash():
    """Test extracting project name with trailing slash."""
    cwd = "/Users/harsha/Tools/cc-fi/"
    result = extract_project_name(cwd)
    assert result == "cc-fi"  # Path handles trailing slashes correctly


def test_extract_project_name_root():
    """Test extracting project name from root directory."""
    cwd = "/"
    result = extract_project_name(cwd)
    assert result == ""
