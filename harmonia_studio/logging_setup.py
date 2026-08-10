from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
from .settings import logs_dir

def configure_logging(level: int = logging.INFO, directory: Path | None = None) -> Path:
    directory = directory or logs_dir()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "harmonia-studio.log"
    logger = logging.getLogger("harmonia")
    logger.setLevel(level)
    if not logger.handlers:
        handler = RotatingFileHandler(path, maxBytes=2_000_000, backupCount=3, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
        logger.addHandler(handler)
    return path
