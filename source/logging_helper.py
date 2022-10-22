#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration and functions for logging
"""
import time
import logging
import json
from dataclasses import dataclass
from source.constants import CONFIGURATION_FILE_PATH


@dataclass
class LogLevel:
    """
    Configuration class for reding the logging level and provide to application.
    """

    log_levels = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    config_level: str = logging.CRITICAL
    with open(CONFIGURATION_FILE_PATH, encoding="utf-8") as file:
        general_config = json.load(file)["general"]
        if "log_level" in general_config:
            temp_level = general_config["log_level"]
            config_level = log_levels[temp_level]


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


def write_debug_log(log_message: str) -> None:
    """
    Write function for logging debug information
    :param log_message: Message
    :return: No return value
    """
    logging.debug(log_message)


def write_error_log(log_message: str) -> None:
    """
    Write function for logging error information
    :param log_message: Message
    :return: No return value
    """
    logging.error(log_message)


def main() -> None:
    """
    Scheduling function for regular call.
    :return: None
    """


if __name__ == "__main__":
    main()
