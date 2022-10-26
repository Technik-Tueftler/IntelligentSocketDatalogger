#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration and functions for logging
"""
import time
import logging
import json
from dataclasses import dataclass
from enum import Enum
from source.constants import CONFIGURATION_FILE_PATH


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
