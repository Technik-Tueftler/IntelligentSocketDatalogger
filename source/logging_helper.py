#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration and functions for logging
"""
import time
import logging
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import deque
from source.constants import CONFIGURATION_FILE_PATH, LOGGING_MAX_LEN_FAILURE


@dataclass
class WatchHen:
    device_name: str
    online_status: bool = field(default=True)
    last_failures: deque = field(
        default_factory=lambda: deque(maxlen=LOGGING_MAX_LEN_FAILURE)
    )

    def normal_processing(self):
        if not self.online_status:
            self.online_status = True
            self.last_failures.clear()
            message = f"Device {self.device_name} online again."
            logging.log(logging.Info, message)

    def failure_processing(self, error_type, error_message, error_context):
        self.last_failures.append(
            Failure(error_type=error_type, message=error_message, context=error_context)
        )
        count_simular_failure = len(
            [
                True
                for element in self.last_failures
                if element.error_type == error_type
            ]
        )
        message = f"{self.device_name} {error_context} | {error_type} | {error_message}"
        logging.log(logging.DEBUG, message)
        if count_simular_failure == 1:
            logging.log(logging.WARNING, message)
        elif count_simular_failure == 2:
            message = f"Device {self.device_name} {error_context} multiple times and was marked as offline."
            logging.log(logging.ERROR, message)
            self.online_status = False
        else:
            pass

    def __repr__(self):
        return "Fehlerliste: " + str(self.last_failures)


@dataclass
class Failure:
    error_type: None
    message: str  # Gibt z.B. bei Key Error den fehlerhaften Key mit
    context: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


class LoggingLevel(Enum):
    """
    Collection for logging levels
    """

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


@dataclass
class LogLevel:
    """
    Configuration class for reding the logging level and provide to application.
    """

    log_levels = {
        "debug": LoggingLevel.DEBUG.value,
        "info": LoggingLevel.INFO.value,
        "warning": LoggingLevel.WARNING.value,
        "error": LoggingLevel.ERROR.value,
        "critical": LoggingLevel.CRITICAL.value,
    }
    config_level: str = logging.CRITICAL
    try:
        with open(CONFIGURATION_FILE_PATH, encoding="utf-8") as file:
            general_config = json.load(file)["general"]
            if "log_level" in general_config:
                config_level = log_levels[general_config["log_level"]]
    except FileNotFoundError as err:
        print(
            f"The configuration file could not be found. Please put it in the folder you passed "
            f"with the environment variables. Error occurred message: {err}."
        )


program_logging_level = LogLevel()
logging.basicConfig(
    filename="../files/main.log",
    encoding="utf-8",
    filemode="a",
    level=program_logging_level.config_level,
    format="%(asctime)s: %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)
logging.Formatter.converter = time.gmtime


def write_log(level: int, message: str):
    """
    Write function for logging debug information
    :param level: log level for the message
    :param message: log message
    :return: No return value
    """
    logging.log(level, message)
    print(message)


def main() -> None:
    """
    Scheduling function for regular call.
    :return: None
    """


if __name__ == "__main__":
    main()
