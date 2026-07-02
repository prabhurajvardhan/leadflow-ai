import sys
from loguru import logger
from app.core.config import settings

# Remove default handler
logger.remove()

# Configure logger
log_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)

logger.add(
    sys.stderr,
    format=log_format,
    level="DEBUG" if settings.DEBUG else "INFO",
    colorize=True,
)

# Add file logging in production
if not settings.DEBUG:
    logger.add(
        "logs/app.log",
        rotation="500 MB",
        retention="10 days",
        level="INFO",
        format=log_format,
    )

# Add separate error logging
logger.add(
    "logs/error.log",
    rotation="100 MB",
    retention="30 days",
    level="ERROR",
    format=log_format,
    backtrace=True,
    diagnose=True,
)


def get_logger(name: str):
    return logger.bind(name=name)
