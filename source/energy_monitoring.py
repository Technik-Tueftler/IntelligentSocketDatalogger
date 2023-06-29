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
import source.logging_helper as lh
from source.constants import (
    DEVICES_FILE_PATH,
    DEFAULT_ALARM_THRESHOLD_WH,
    DEFAULT_ALARM_PERIOD_MIN,
    DEFAULT_REFERENCE_WH,
)


observed_devices = []


@dataclass
class Device:
    """
    A device that has been registered for monitoring
    """

    name: str
    reference_wh_last_period: int
    threshold_wh: int
    period_min: int


def get_device_energy_last_period(device: Device) -> float:
    """
    Calculate the energy of the device for the last period.
    :param device: Device for which the calculation run
    :return: Sum of energy of the device
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
    return round(
        sum(
            measurement["energy_wh"]
            for measurement in result.get_points()
            if measurement["fetch_success"]
        ),
        2,
    )


def write_device_monitoring_values(device: Device) -> None:
    """
    Function to write the reference value of the device in the configuration file
    :param device: Device for which the update was requested
    :return: None
    """
    energy_wh = get_device_energy_last_period(device)
    device.reference_wh_last_period = energy_wh
    with open(DEVICES_FILE_PATH, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)

    data[device.name]["energy_alarm"]["reference_wh_last_period"] = energy_wh

    with open(DEVICES_FILE_PATH, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4)

    message = f"Change threshold for {device.name} to value: {energy_wh}wh"
    com.to_bot.put(com.Response("status", {"output_text": message}))


def run_monitoring(device: Device) -> None:
    """
    Checks whether a device exceeds the limit values in the set time period
    :param device: Device to be checked
    :return: None
    """
    energy_wh = get_device_energy_last_period(device)

    log_message = f"EM: {device.name} / {energy_wh} >= {device.threshold_wh}"
    lh.write_log(lh.LoggingLevel.INFO.value, log_message)

    if energy_wh >= device.threshold_wh:
        com.to_bot.put(
            com.Request(command="alarm_message", data={"device_name": device.name})
        )
        log_message = f"Energy consumption of {device.name} is unusually high."
        lh.write_log(lh.LoggingLevel.WARNING.value, log_message)


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
        ref_wh = device_energy_alarm.get(
            "reference_wh_last_period", DEFAULT_REFERENCE_WH
        )
        observed_devices.append(
            Device(
                name=device,
                reference_wh_last_period=ref_wh,
                threshold_wh=thr_wh,
                period_min=per_min,
            )
        )


def handle_communication() -> None:
    """
    Check all the items in monitoring queue and process the commands.
    :return: None
    """
    while not com.to_energy_mon.empty():
        req = com.to_energy_mon.get()
        if req.command == "set_alarm":
            device_name = req.data["device"]
            device_for_changing = next(
                filter(lambda device: device.name == device_name, observed_devices),
                None,
            )
            if device_for_changing is None:
                continue
            write_device_monitoring_values(device_for_changing)


def main() -> None:
    """
    Scheduling function for regular call.
    :return: None
    """


if __name__ == "__main__":
    main()
