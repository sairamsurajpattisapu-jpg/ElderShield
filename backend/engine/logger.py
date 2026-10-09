import os
import re
import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict

from .privacy import redact_sensitive_data

class PrivacyFilter(logging.Filter):
    """
    Filters all log messages to redact any sensitive PII, telephone numbers,
    Aadhaar numbers, bank account numbers, or OTP tokens before they are emitted.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = redact_sensitive_data(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {
                    k: redact_sensitive_data(str(v)) if isinstance(v, str) else v
                    for k, v in record.args.items()
                }
            elif isinstance(record.args, (list, tuple)):
                record.args = tuple(
                    redact_sensitive_data(str(a)) if isinstance(a, str) else a
                    for a in record.args
                )
        return True

class JsonFormatter(logging.Formatter):
    """
    Formats log records as structured single-line JSON objects
    for production log aggregators (e.g. Datadog, CloudWatch, Loki).
    """
    def format(self, record: logging.LogRecord) -> str:
        log_payload: Dict[str, Any] = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "func": record.funcName,
            "line": record.lineno,
        }
        if hasattr(record, "session_id"):
            log_payload["session_id"] = record.session_id
        if hasattr(record, "correlation_id"):
            log_payload["correlation_id"] = record.correlation_id
        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_payload, ensure_ascii=False)

def setup_logger(name: str = "eldershield", level: str = "INFO", json_format: bool = False) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False

    # Avoid duplicate handlers if re-called
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.addFilter(PrivacyFilter())
        
        if json_format:
            handler.setFormatter(JsonFormatter())
        else:
            std_format = logging.Formatter(
                fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(std_format)
            
        logger.addHandler(handler)
    return logger

# Primary app logger instance
from config import settings
app_logger = setup_logger(
    name="eldershield",
    level=settings.log_level,
    json_format=settings.enable_json_logging
)
