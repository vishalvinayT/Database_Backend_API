from pydantic import BaseModel
import logging
import uvicorn.logging


class LogConfig(BaseModel):
    LOGGER_NAME: str = "__name__"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "INFO"

    # Logging config
    version = 1
    disable_existing_loggers = False
    formatters = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers = {
        "console": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "formatter": "default",
            "class": "logging.FileHandler",
            "filename": "./logs/api.log",
        },
    }
    loggers = {
        "": {"handlers": ["file"], "level": LOG_LEVEL},
        LOGGER_NAME: {"handlers": ["file"], "level": LOG_LEVEL},
    }