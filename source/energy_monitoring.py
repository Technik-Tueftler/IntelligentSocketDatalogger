#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
All functions required to monitor a device and to send information
to the user if necessary.
"""
import json
from collections import namedtuple
from source.constants import (
    DEVICES_FILE_PATH,
    DEFAULT_ALARM_THRESHOLD_WH,
    DEFAULT_ALARM_PERIOD_MIN,
)


observed_devices = []
Device = namedtuple("Device", ["name", "threshold_wh", "period_min"])


def run_monitoring(device: Device) -> None:
    """
    Checks whether a device exceeds the limit values in the set time period
    :param device: Device to be checked
    :return: None
    """
    ...


def check_monitoring_requested(started_devices: list) -> None:
    """
    Check if a monitoring is requested, validates the parameters and
    creates an object for verification handling
    :param started_devices: List of started devices
    :return: None
    """
    with open(DEVICES_FILE_PATH, encoding="utf-8") as file:
        data = json.load(file)
    for device in started_devices:
        device_energy_alarm = data.get(device, {}).get("energy_alarm", {})
        device_active = device_energy_alarm.get("active", False)
        if not device_active:
            continue
        thr_wh = device_energy_alarm.get("threshold_wh", DEFAULT_ALARM_THRESHOLD_WH)
        per_min = device_energy_alarm.get("period_min", DEFAULT_ALARM_PERIOD_MIN)
        observed_devices.append(
            Device(name=device, threshold_wh=thr_wh, period_min=per_min)
        )


def main() -> None:
    """
    Scheduling function for regular call.
    :return: None
    """
    pass


if __name__ == "__main__":
    main()
