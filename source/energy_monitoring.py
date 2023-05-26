#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
All functions required to monitor a device and to send information
to the user if necessary.
"""
import json
from datetime import datetime, timedelta
from dataclasses import dataclass
from source import communication as com
import source.support_functions as sf
from source.constants import (
    DEVICES_FILE_PATH,
    DEFAULT_ALARM_THRESHOLD_WH,
    DEFAULT_ALARM_PERIOD_MIN,
)


observed_devices = []


@dataclass
class Device:
    """
    A device that has been registered for monitoring
    """
    name: str
    threshold_wh: int
    period_min: int


def run_monitoring(device: Device) -> None:
    """
    Checks whether a device exceeds the limit values in the set time period
    :param device: Device to be checked
    :return: None
    """
    current_timestamp = datetime.utcnow()
    start_date = current_timestamp - timedelta(minutes=device.period_min)
    start_date_format = start_date.strftime("%Y-%m-%d %H:%M:%S")
    end_date = current_timestamp
    end_date_format = end_date.strftime("%Y-%m-%d %H:%M:%S")
    result = sf.fetch_measurements(
        {
            "device": device.name,
            "target_date": start_date_format,
            "current_date": end_date_format,
        }
    )
    energy_wh = sum(measurement["energy_wh"] for measurement in result.get_points())
    if energy_wh >= Device.threshold_wh:
        com.to_bot.put(com.Request(command="alarm_message",
                                   data={"device_name": device.name}))


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


def handle_communication() -> None:
    """
    Check all the items in monitoring queue and process the commands.
    :return: None
    """
    while not com.to_energy_mon.empty():
        req = com.to_bot.get()
        if req.command == "set_alarm":
            ...


def main() -> None:
    """
    Scheduling function for regular call.
    :return: None
    """


if __name__ == "__main__":
    main()
