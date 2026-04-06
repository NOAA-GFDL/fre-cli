"""
Tests for the log_and_raise helper function in fre/__init__.py.

Validates that log_and_raise:
- logs an error message via fre_logger
- raises the correct exception type with the expected message
- supports exception chaining via the exc parameter
- defaults to ValueError when no exc_type is given
- reports the correct caller in log output (not log_and_raise itself)
- writes stack trace info to a log file (simulating ``fre -l ./log.log``)
- writes exception traceback to a log file when exc is provided
"""

import logging
from pathlib import Path

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


def test_log_and_raise_stack_trace_in_log_file(tmp_path):
    """
    Simulates ``fre -l ./logger_output.log`` by attaching a FileHandler to
    the ``fre`` logger, then verifying that log_and_raise writes stack trace
    information to the log file via ``stack_info=True``.

    Per Python logging best practices (docs.python.org/3/howto/logging.html),
    ``stack_info=True`` causes the current call stack to appear in the log
    output, making it straightforward to locate the origin of an error.
    """
    from fre import FORMAT

    log_file = tmp_path / "logger_output.log"

    # Mirror fre.py: attach a FileHandler to the root 'fre' logger
    base_logger = logging.getLogger("fre")
    handler = logging.FileHandler(str(log_file), mode="w", encoding="utf-8")
    handler.setFormatter(logging.Formatter(fmt=FORMAT))
    handler.setLevel(logging.ERROR)
    base_logger.addHandler(handler)

    try:
        with pytest.raises(ValueError, match="stack trace test"):
            log_and_raise("stack trace test")
    finally:
        base_logger.removeHandler(handler)
        handler.close()

    log_content = log_file.read_text(encoding="utf-8")

    # The error message itself must appear
    assert "stack trace test" in log_content

    # stack_info=True produces a "Stack (most recent call last):" block
    assert "Stack (most recent call last):" in log_content

    # The call stack should reference THIS test function
    assert "test_log_and_raise_stack_trace_in_log_file" in log_content


def test_log_and_raise_traceback_in_log_file(tmp_path):
    """
    Simulates ``fre -l ./logger_output.log`` and verifies that when
    log_and_raise is called with ``exc`` (inside an except block), the
    caught exception's traceback appears in the log file via
    ``exc_info=True``.

    This matches the Python best practice of using ``exc_info=True`` to
    record the full traceback of a caught exception
    (see docs.python.org/3/library/logging.html#logging.Logger.error).
    """
    from fre import FORMAT

    log_file = tmp_path / "logger_output.log"

    base_logger = logging.getLogger("fre")
    handler = logging.FileHandler(str(log_file), mode="w", encoding="utf-8")
    handler.setFormatter(logging.Formatter(fmt=FORMAT))
    handler.setLevel(logging.ERROR)
    base_logger.addHandler(handler)

    try:
        try:
            raise RuntimeError("original failure")
        except RuntimeError as caught:
            with pytest.raises(OSError, match="wrapped failure"):
                log_and_raise("wrapped failure", OSError, exc=caught)
    finally:
        base_logger.removeHandler(handler)
        handler.close()

    log_content = log_file.read_text(encoding="utf-8")

    # The error message itself must appear
    assert "wrapped failure" in log_content

    # exc_info=True produces a "Traceback (most recent call last):" block
    assert "Traceback (most recent call last):" in log_content

    # The original exception type and message must appear in the traceback
    assert "RuntimeError: original failure" in log_content

    # stack_info=True also adds the call stack
    assert "Stack (most recent call last):" in log_content
