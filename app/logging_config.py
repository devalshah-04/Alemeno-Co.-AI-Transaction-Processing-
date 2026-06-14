# Configures all loggers to emit single-line JSON
import logging
import json
import sys


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {"level": record.levelname, "logger": record.name, "message": record.getMessage()}
        if hasattr(record, "extra_fields"):
            log_record.update(record.extra_fields)
        return json.dumps(log_record)


def configure_logging():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)