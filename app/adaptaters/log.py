import logging
import logging.config
import queue
from enum import Enum
from logging.handlers import QueueHandler, QueueListener
from pathlib import Path
from typing import Any

import uvicorn.logging

LOG_DEBUG_MESSAGES = True


class ColoredConsoleFormatter(uvicorn.logging.DefaultFormatter):
    class ConsoleColors(str, Enum):
        """Colors can be found here: https://talyian.github.io/ansicolors/"""

        DEBUG = "\033[38;5;12m"
        INFO = "\033[38;5;10m"
        WARNING = "\033[38;5;11m"
        ERROR = "\033[38;5;9m"
        CRITICAL = "\033[38;5;1m"
        BOLD = "\033[1m"
        END = "\033[0m"

    def __init__(self, *args, **kwargs):
        super().__init__(datefmt="%d-%b-%y %H:%M:%S")

        self.formatters = {}

        for level in [
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
        ]:
            fmt = (
                "%(asctime)s - %(name)s - "
                + self.ConsoleColors.BOLD
                + "%(levelname)s"
                + self.ConsoleColors.END
                + " - "
                + self.ConsoleColors[logging.getLevelName(level)]
                + "%(message)s"
                + self.ConsoleColors.END
            )
            level_formatter = logging.Formatter(fmt, self.datefmt)
            self.formatters[level] = level_formatter

    def format(self, record: logging.LogRecord) -> str:
        formatter: logging.Formatter = self.formatters.get(
            record.levelno,
            self.formatters[logging.ERROR],
        )
        return formatter.format(record)


class LogConfig:
    """
    Logging configuration to be set for the server
    We convert this class to a dict to be used by Python logging module.

    Call `LogConfig().initialize_loggers()` to configure the logging ecosystem.
    """

    # Uvicorn loggers config
    # https://github.com/encode/uvicorn/blob/b21ecabc5bf911f571e0629438315a1e5472065c/uvicorn/config.py#L95

    class console_color:
        DEBUG = "\033[38;5;12m"
        INFO = "\033[38;5;10m"
        WARNING = "\033[38;5;9m"
        BOLD = "\033[1m"
        END = "\033[0m"

    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    CONSOLE_LOG_FORMAT: str = (
        "%(asctime)s - %(name)s - "
        + console_color.BOLD
        + "%(levelname)s"
        + console_color.END
        + " - "
        + console_color.INFO
        + "%(message)s"
        + console_color.END
    )

    # Logging config
    # See https://docs.python.org/3/library/logging.config.html#logging-config-dictschema
    def get_config_dict(self) -> dict:
        # We can't use a dependency to access settings as this function is not an endpoint. The object must thus be passed as a parameter.

        MINIMUM_LOG_LEVEL: str = "DEBUG" if LOG_DEBUG_MESSAGES else "INFO"

        return {
            "version": 1,
            # If LOG_DEBUG_MESSAGES is set, we let existing loggers, including the database and uvicorn loggers
            "disable_existing_loggers": not LOG_DEBUG_MESSAGES,
            "formatters": {
                "log_formatter": {
                    "()": "uvicorn.logging.DefaultFormatter",
                    "fmt": self.LOG_FORMAT,
                    "datefmt": "%d-%b-%y %H:%M:%S",
                },
                "console_formatter": {
                    "()": "app.adaptaters.log.ColoredConsoleFormatter",
                },
            },
            "handlers": {
                # Console handler is always active, even in production.
                # It should be used to log errors and information about the server (starting up, hostname...)
                "console": {
                    "formatter": "console_formatter",
                    "class": ("logging.StreamHandler"),
                    "level": MINIMUM_LOG_LEVEL,
                },
                # There is a handler per log file #
                # They are based on RotatingFileHandler to logs in multiple 1024 bytes files
                # https://docs.python.org/3/library/logging.handlers.html#logging.handlers.RotatingFileHandler
                "file_errors": {
                    # File_errors should receive all errors, even when they are already logged elsewhere
                    "formatter": "log_formatter",
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": "logs/errors.log",
                    "maxBytes": 1024 * 1024 * 10,  # ~ 10 MB
                    "backupCount": 20,
                    "level": "DEBUG",
                },
            },
            # We define various loggers which can be used by Kognize.
            # Each logger has:
            #  - specific handlers (ex: file_access or file_security), they log targeted records like endpoint access or authentication
            #  - error related handlers (ex: file_errors and matrix_errors), they log all errors regardless of their provenance
            #  - default handler which logs to the console for development and debugging purpose
            "loggers": {
                # base should be used to log all message and error we want to trace
                # Other loggers can process error messages and may be more appropriated than kognize
                "base": {
                    "handlers": [
                        "file_errors",
                        "console",
                    ],
                    "level": MINIMUM_LOG_LEVEL,
                },
                # We disable "uvicorn.access"
                "uvicorn.access": {"handlers": []},
                "uvicorn.error": {
                    "handlers": [
                        "file_errors",
                        "console",
                    ],
                    "level": MINIMUM_LOG_LEVEL,
                },
            },
        }

    def initialize_loggers(self) -> None:
        """
        Initialize the logging ecosystem.

        The previous dict configuration will be used.

        Kognize is an async FastAPI application. Logging may be done by endpoints. In order to limit the speed impact of
        logging (especially for network operations, like sending a log record to a Matrix server), it will be realized in a specific thread.
        All handlers will then be encapsulated in QueueHandlers having their own thread.
        """
        # https://rob-blackbourn.medium.com/how-to-use-python-logging-queuehandler-with-dictconfig-1e8b1284e27a
        # https://www.zopatista.com/python/2019/05/11/asyncio-logging/

        # We may be interested in https://github.com/python/cpython/pull/93269 when it will be released. See https://discuss.python.org/t/a-new-feature-is-being-added-in-logging-config-dictconfig-to-configure-queuehandler-and-queuelistener/16124

        # If logs/ folder does not exist, the logging module won't be able to create file handlers
        Path("logs/").mkdir(parents=True, exist_ok=True)

        config_dict = self.get_config_dict()
        logging.config.dictConfig(config_dict)

        loggers = [logging.getLogger(name) for name in config_dict["loggers"]]

        for logger in loggers:
            # If the logger does not have any handler, we don't need to create a QueueHandler
            if len(logger.handlers) == 0:
                continue

            # We create a queue where all log records will be added
            log_queue: queue.Queue[Any] = queue.Queue(-1)

            # queue_handler is the handler which adds all log records to the queue
            queue_handler = QueueHandler(log_queue)

            # The listener will watch the queue and let the previous handler process logs records in their own thread
            listener = QueueListener(
                log_queue,
                *logger.handlers,
                respect_handler_level=True,
            )
            listener.start()

            # We remove all previous handlers
            logger.handlers = []

            # We add our new queue_handler
            logger.addHandler(queue_handler)
