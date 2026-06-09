"""app/utils/logger.py"""
import logging
import structlog


def get_logger(name: str):
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    )
    return structlog.get_logger(name)
