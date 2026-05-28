from loguru import logger
import sys

logger.remove()

LOG_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss} | "
    "{level} | "
    "{extra[ip]} | "
    "{extra[method]} {extra[path]} | "
    "{extra[status]} | "
    "{extra[process_time]}ms | "
    "{extra[user_agent]} | "
    "{message}"
)

logger.add(
    sys.stdout,
    level="INFO",
    format=LOG_FORMAT,
    backtrace=True,
)

logger.add(
    "app/logs/debug.log",
    filter=lambda record: record["level"].name in ["DEBUG", "INFO"],
    level="DEBUG",
    format=LOG_FORMAT,
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    backtrace=True,
)

logger.add(
    "app/logs/errors.log",
    level="ERROR",
    format=LOG_FORMAT,
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    backtrace=True,
    diagnose=True,
)
