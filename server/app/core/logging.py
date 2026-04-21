"""日志配置（使用 loguru）。"""
import sys
from pathlib import Path

from loguru import logger

from app.core.config import settings


def setup_logging() -> None:
    """配置全局日志。"""
    logger.remove()

    # 控制台输出（彩色）
    logger.add(
        sys.stderr,
        level=settings.log_level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        colorize=True,
    )

    # 文件输出
    log_path = Path(settings.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger.add(
        str(log_path),
        level=settings.log_level,
        rotation="100 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
    )
