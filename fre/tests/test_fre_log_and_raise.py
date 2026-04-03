"""
Tests for the log_and_raise helper function in fre/__init__.py.

Validates that log_and_raise:
- logs an error message via fre_logger
- raises the correct exception type with the expected message
- supports exception chaining via the exc parameter
- defaults to ValueError when no exc_type is given
- reports the correct caller in log output (not log_and_raise itself)
"""

import logging

import pytest

from fre import log_and_raise


def test_log_and_raise_default_valueerror(caplog):
    ''' log_and_raise with default exc_type should raise ValueError and log an error '''
    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValueError, match="something went wrong"):
            log_and_raise("something went wrong")
    assert "something went wrong" in caplog.text


def test_log_and_raise_custom_exception_type(caplog):
    ''' log_and_raise with custom exc_type should raise that type '''
    with caplog.at_level(logging.ERROR):
        with pytest.raises(OSError, match="file not found"):
            log_and_raise("file not found", OSError)
    assert "file not found" in caplog.text


def test_log_and_raise_with_chained_exception(caplog):
    ''' log_and_raise with exc should chain exceptions via from '''
    original = KeyError("original key error")
    with caplog.at_level(logging.ERROR):
        with pytest.raises(KeyError, match="wrapped error") as exc_info:
            log_and_raise("wrapped error", KeyError, exc=original)
    assert exc_info.value.__cause__ is original
    assert "wrapped error" in caplog.text


def test_log_and_raise_caller_in_log(caplog):
    ''' log output should reference the calling function, not log_and_raise '''
    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValueError):
            log_and_raise("test caller context")
    # the log record funcName should be this test function, not 'log_and_raise'
    for record in caplog.records:
        if "test caller context" in record.message:
            assert record.funcName == "test_log_and_raise_caller_in_log"
            break
    else:
        pytest.fail("expected log record not found")
