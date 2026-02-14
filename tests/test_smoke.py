"""Smoke test — validates package can be imported."""

from engram import __version__


def test_version_exists() -> None:
    """Package version is defined."""
    assert __version__ == "0.0.0"
