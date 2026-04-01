"""
Shared pytest fixtures for fre.make tests.

Provides common setup/teardown for test output directories and
environment variables used across the make test suite.
"""

import shutil
from pathlib import Path

import pytest

# Test directory paths — use __file__ so tests work from any working directory
TEST_DIR = Path(__file__).resolve().parent

@pytest.fixture
def checkout_out(monkeypatch):
    """
    Provide a clean checkout output directory and set TEST_BUILD_DIR.

    Ensures the output directory exists and is clean before each test,
    and cleans up after. Uses monkeypatch to set TEST_BUILD_DIR so it
    is automatically restored after the test.

    Note: Only cleans the experiment subtree (not the whole OUT dir)
    because checkout_create creates the full directory structure itself.
    """
    out = f"{TEST_DIR}/checkout_out"
    monkeypatch.setenv("TEST_BUILD_DIR", out)

    # Clean the experiment-specific subtree (not the whole out dir)
    experiment_dir = Path(f"{out}/fremake_canopy/test")
    if experiment_dir.exists():
        shutil.rmtree(experiment_dir)

    yield out

    # Post-test cleanup of experiment subtree
    if experiment_dir.exists():
        shutil.rmtree(experiment_dir, ignore_errors=True)

@pytest.fixture
def compile_out(monkeypatch):
    """
    Provide a clean compile output directory and set TEST_BUILD_DIR.

    Note: Recreates the entire OUT dir because compile_create expects
    the base output directory to already exist.
    """
    out = f"{TEST_DIR}/compile_out"
    monkeypatch.setenv("TEST_BUILD_DIR", out)

    if Path(out).exists():
        shutil.rmtree(out)
    Path(out).mkdir(parents=True, exist_ok=True)

    yield out

@pytest.fixture
def makefile_out(monkeypatch):
    """
    Provide a clean makefile output directory and set TEST_BUILD_DIR.

    Note: Recreates the entire OUT dir because makefile_create expects
    the base output directory to already exist.
    """
    out = f"{TEST_DIR}/makefile_out"
    monkeypatch.setenv("TEST_BUILD_DIR", out)

    if Path(out).exists():
        shutil.rmtree(out)
    Path(out).mkdir(parents=True, exist_ok=True)

    yield out
