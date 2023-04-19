#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from dataclasses import dataclass
from queue import Queue

bot_to_main = Queue()
main_to_bot = Queue()


@dataclass
class Response:
    response: str
    command: str
    timestamp: datetime = datetime.utcnow()


@dataclass
class Request:
    command: str
    timestamp: datetime = datetime.utcnow()


def main() -> None:
    pass


if __name__ == "__main__":
    main()
