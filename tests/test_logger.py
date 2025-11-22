
import json
import logging
from logging.handlers import RotatingFileHandler
from unittest import mock
import pytest
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)


@pytest.fixture
def setup_logger(tmp_path):
    # Clear any existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.INFO)

    # Add StreamHandler
    stream_handler = logging.StreamHandler()
    root_logger.addHandler(stream_handler)

    # Add RotatingFileHandler
    log_file = tmp_path / "app.log"
    file_handler = RotatingFileHandler(log_file, maxBytes=1024, backupCount=2)
    root_logger.addHandler(file_handler)

    # Configure structlog to use stdlib logging
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    return root_logger, file_handler, stream_handler


def test_logger_has_handlers(setup_logger):
    root_logger, file_handler, stream_handler = setup_logger
    handlers = root_logger.handlers
    assert any(isinstance(h, logging.StreamHandler) for h in handlers)
    assert any(isinstance(h, RotatingFileHandler) for h in handlers)



def test_console_handler_output(caplog):
    # configure structlog to integrate with stdlib logging
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logger = structlog.get_logger()

    with caplog.at_level(logging.INFO):
        logger.info("test_console", value=42)

    # check log message appears in captured records
    assert any("test_console" in r.getMessage() for r in caplog.records)


def test_file_handler_json(tmp_path):

    # JSON formatter for the handler
    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(),
        foreign_pre_chain=[structlog.processors.TimeStamper(fmt="iso")],
    )

    # Configure structlog so events are wrapped for ProcessorFormatter
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,  # critical!
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    log_file = tmp_path / "app.log"
    with mock.patch("logging.handlers.RotatingFileHandler") as mock_handler_class:
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10, backupCount=1, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        mock_handler_class.return_value = file_handler

        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)

        log = structlog.get_logger()
        log.info("test_file", value=123)

        file_handler.flush()
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
            assert content, "log file should not be empty"
            data = json.loads(content)   # now should succeed
            assert data["event"] == "test_file"
            assert data["value"] == 123



def test_rotating_file_handler_rotation(tmp_path):

    structlog.configure(
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    log_file = tmp_path / "app.log"
    handler = RotatingFileHandler(log_file, maxBytes=50, backupCount=2)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    log = structlog.get_logger()

    # generate enough logs to trigger rotation
    for i in range(100):  # ensure size > maxBytes
        log.info("rot_test " + ("x" * 20), i=i)

    handler.flush()

    # Check that at least one backup file exists
    backup_exists = any(tmp_path.glob("app.log.*"))
    assert backup_exists
