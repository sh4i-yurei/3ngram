"""Smoke test — validates package can be imported."""

import re

from engram import __version__


def test_version_exists() -> None:
    """Package version is defined and follows semver."""
    assert isinstance(__version__, str)
    assert __version__
    assert re.match(r"^\d+\.\d+\.\d+", __version__) is not None
