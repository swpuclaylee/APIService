import logging.config
import os

from .config import log_name

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
log_dir = os.path.join(root_dir, 'logs')


def configure_logging():
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "[%(asctime)s] [%(thread)d] [%(name)s] [%(filename)s:%(lineno)d] [%(module)s:%(funcName)s] [%(levelname)s]- %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "verbose"
            },
            "file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "when": "midnight",
                "interval": 1,
                "filename": f"{log_dir}/{log_name}.log",
                "backupCount": 7,
                "level": "INFO",
                "formatter": "verbose",
                "encoding": "utf-8"
            }
        },
        "loggers": {
            log_name: {
                "handlers": ["console", "file"],
                "level": "INFO"
            }
        }
    }
    logging.config.dictConfig(log_config)
    return logging.getLogger(log_name)
