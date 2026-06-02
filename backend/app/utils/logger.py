"""
结构化日志配置模块
提供 JSON 格式日志输出，便于日志收集和分析
"""
import logging
import json
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """JSON 格式日志格式化器"""

    def format(self, record: logging.LogRecord) -> str:
        """将日志记录格式化为 JSON 字符串"""
        log_data = {
            "time": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 附加额外字段
        if hasattr(record, "extra_data"):
            log_data["data"] = record.extra_data

        # 异常信息
        if record.exc_info and record.exc_info[1]:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
            }

        return json.dumps(log_data, ensure_ascii=False)


class PlainFormatter(logging.Formatter):
    """纯文本格式日志格式化器（开发环境使用）"""

    FORMAT = "%(asctime)s | %(levelname)-8s | %(module)s:%(funcName)s:%(lineno)d | %(message)s"

    def __init__(self):
        super().__init__(fmt=self.FORMAT)


def setup_logging(debug: bool = False, json_output: bool = False) -> None:
    """
    配置全局日志

    Args:
        debug: 是否启用 DEBUG 级别
        json_output: 是否使用 JSON 格式输出（生产环境推荐）
    """
    level = logging.DEBUG if debug else logging.INFO

    formatter = JsonFormatter() if json_output else PlainFormatter()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # 降低第三方库日志级别
    for name in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
        logging.getLogger(name).setLevel(logging.WARNING)

    # SQLAlchemy 日志只在 DEBUG 模式下显示
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if debug else logging.WARNING
    )


def get_logger(name: str) -> logging.Logger:
    """
    获取命名日志器

    Args:
        name: 日志器名称，通常用 __name__

    Returns:
        Logger 实例
    """
    return logging.getLogger(name)
