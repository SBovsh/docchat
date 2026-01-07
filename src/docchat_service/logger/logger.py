import json
import logging
import sys
from contextvars import ContextVar
from logging import Formatter, Logger, StreamHandler
from typing import Any, Dict, Optional

trace_id_ctx: ContextVar[str] = ContextVar("trace_id", default="local")


class JsonFormatter(Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "trace_id": trace_id_ctx.get(),
        }
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data, ensure_ascii=False)


class ColoredFormatter(Formatter):
    COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[41m",
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        return (
            f"{color}%(asctime)s | %(levelname)-8s | %(trace_id)s{self.RESET} "
            f"| %(message)s [%(module)s.%(funcName)s]"
        )


class LoggerConfigurator:
    _instance: Optional["LoggerConfigurator"] = None

    def __new__(cls, log_lvl: int = logging.INFO, context_vars_container=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_logger(log_lvl)
        return cls._instance

    def _init_logger(self, log_lvl: int):
        self.logger = logging.getLogger("rag_app")
        self.logger.setLevel(log_lvl)
        self.logger.handlers.clear()

        console_handler = StreamHandler(sys.stdout)
        if log_lvl == logging.DEBUG:
            console_handler.setFormatter(ColoredFormatter(datefmt="%H:%M:%S"))
        else:
            console_handler.setFormatter(JsonFormatter())
        self.logger.addHandler(console_handler)

    @property
    def async_logger(self) -> Logger:
        return self.logger

    def metric(self, metric_name: str, metric_value: int):
        self.logger.debug(f"Metric stub: {metric_name}={metric_value}")

    def audit(self, event_name: str, event_params: Any):
        self.logger.debug(f"Audit stub: {event_name} | {event_params}")

    def remove_logger_handlers(self):
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)


__all__ = ["LoggerConfigurator"]