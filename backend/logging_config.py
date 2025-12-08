"""Centralized structured logging configuration for AI Revenue Command Center."""

from __future__ import annotations

import logging
import logging.config
import os
from typing import Optional

import structlog


_DEFAULT_LEVEL = "INFO"


def configure_logging(level: Optional[str] = None) -> None:
    """Configure structured JSON logging for the entire application."""

    log_level = (level or os.getenv("LOG_LEVEL", _DEFAULT_LEVEL)).upper()

    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)
    pre_chain = [
        structlog.stdlib.add_log_level,
        timestamper,
    ]

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            timestamper,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "foreign_pre_chain": pre_chain,
                    "processor": structlog.processors.JSONRenderer(),
                }
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                }
            },
            "loggers": {
                "": {"handlers": ["default"], "level": log_level, "propagate": False},
                "uvicorn.error": {
                    "handlers": ["default"],
                    "level": log_level,
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": ["default"],
                    "level": log_level,
                    "propagate": False,
                },
                "audit": {
                    "handlers": ["default"],
                    "level": os.getenv("AUDIT_LOG_LEVEL", log_level),
                    "propagate": False,
                },
            },
        }
    )


__all__ = ["configure_logging"]
