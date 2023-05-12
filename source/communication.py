#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collection of classes and structures needed to ensure communication
between the main app and the telegram bot.
"""
from datetime import datetime
from dataclasses import dataclass, field
from queue import Queue

bot_to_main = Queue()
main_to_bot = Queue()


@dataclass
class Response:
    """
    Response object for communication that comes to a request.
    """

    command: str
    data: dict = field(default_factory=lambda: {})
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Request:
    """
    Request object to request a command.
    """

    command: str
    timestamp: datetime = datetime.utcnow()


def main() -> None:
    """
    Scheduling function for regular call.
    :return: None
    """


if __name__ == "__main__":
    main()
