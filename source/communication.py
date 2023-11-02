#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collection of classes and structures needed to ensure communication
between the main app and the telegram bot.
"""
from datetime import datetime
from dataclasses import dataclass, field
from queue import Queue

to_main = Queue()
to_bot = Queue()
to_energy_mon = Queue()

shared_information = {
    "started_devices": [],
    "observed_devices": [],
    "switchable_devices": [],
}


@dataclass
class SwitchDevice:
    """
    A device that has been registered for switch functionality
    """

    name: str
    type: str
    ip: str
    status: bool


@dataclass
class Device:
    """
    A device that has been registered for monitoring
    """

    name: str
    reference_wh_last_period: int
    threshold_wh: int
    period_min: int


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
    data: dict = field(default_factory=lambda: {})
    timestamp: datetime = field(default_factory=datetime.utcnow)


def main() -> None:
    """
    Scheduling function for regular call.
    :return: None
    """


if __name__ == "__main__":
    main()
