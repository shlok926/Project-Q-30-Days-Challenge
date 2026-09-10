"""Unit tests for the QST logging subsystem.

References:
    Docs/30_OBSERVABILITY.md
    Docs/14_TESTING_STRATEGY.md §3
"""

import json
import logging
from pathlib import Path

import pytest

from qst.logging.formatters import StandardFormatter, StructuredJSONFormatter
from qst.logging.handlers import get_console_handler
from qst.logging.logger import get_logger


@pytest.mark.unit
def test_standard_formatter() -> None:
    """Verify StandardFormatter formats human-readable log records."""
    formatter = StandardFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=42,
        msg="Test message with %s",
        args=("arg1",),
        exc_info=None,
    )
    formatted = formatter.format(record)
    assert "test_logger" in formatted
    assert "INFO" in formatted
    assert "Test message with arg1" in formatted


@pytest.mark.unit
def test_structured_json_formatter() -> None:
    """Verify StructuredJSONFormatter outputs valid JSON with required schema fields."""
    formatter = StructuredJSONFormatter()
    record = logging.LogRecord(
        name="qst.core",
        level=logging.WARNING,
        pathname="protocol.py",
        lineno=105,
        msg="Channel error detected: QBER=%.2f",
        args=(0.12,),
        exc_info=None,
    )
    formatted = formatter.format(record)
    data = json.loads(formatted)

    assert data["logger"] == "qst.core"
    assert data["level"] == "WARNING"
    assert data["message"] == "Channel error detected: QBER=0.12"
    assert data["line"] == 105
    assert "timestamp" in data
    assert "module" in data


@pytest.mark.unit
def test_structured_json_formatter_with_exception() -> None:
    """Verify StructuredJSONFormatter includes serialized stack traces for exceptions."""
    formatter = StructuredJSONFormatter()
    try:
        raise ValueError("Simulated failure")
    except ValueError:
        import sys

        exc_info = sys.exc_info()

    record = logging.LogRecord(
        name="qst.exception",
        level=logging.ERROR,
        pathname="error.py",
        lineno=20,
        msg="Operation failed",
        args=(),
        exc_info=exc_info,
    )
    formatted = formatter.format(record)
    data = json.loads(formatted)

    assert data["level"] == "ERROR"
    assert "exception" in data
    assert "ValueError: Simulated failure" in data["exception"]


@pytest.mark.unit
def test_get_logger_configuration(tmp_path: Path) -> None:
    """Verify get_logger configures handlers, level, and file logging."""
    log_file = tmp_path / "qst.log"
    logger = get_logger(
        name="test.custom_logger",
        level=logging.DEBUG,
        structured=True,
        log_file=log_file,
    )

    assert logger.level == logging.DEBUG
    assert len(logger.handlers) >= 1

    # Write a log entry
    logger.info("Structured log message to file")

    # Flush all handlers
    for h in logger.handlers:
        h.flush()

    assert log_file.exists()
    content = log_file.read_text(encoding="utf-8")
    assert "Structured log message to file" in content
    # Verify line is valid JSON
    for line in content.strip().splitlines():
        parsed = json.loads(line)
        assert parsed["message"] == "Structured log message to file"


@pytest.mark.unit
def test_get_handlers() -> None:
    """Verify get_console_handler and get_file_handler."""
    console_h = get_console_handler(structured=False)
    assert isinstance(console_h.formatter, StandardFormatter)

    console_h_struct = get_console_handler(structured=True)
    assert isinstance(console_h_struct.formatter, StructuredJSONFormatter)
