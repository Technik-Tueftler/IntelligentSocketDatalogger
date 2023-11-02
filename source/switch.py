#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from source import communication as com
from source.supported_devices import plugins
from source import logging_helper as lh
from source.constants import DEVICES_FILE_PATH

switch_watcher = lh.WatchHen(device_name="Switch-Handler")


def check_switch_mode_requested(started_devices: list) -> None:
    """
    Check if a switch functionality is requested and create the devices for
    handling functions
    :param started_devices: List of started devices
    :return: None
    """
    with open(DEVICES_FILE_PATH, encoding="utf-8") as file:
        data = json.load(file)
    for device in started_devices:
        device_energy_alarm = data.get(device, {}).get("switch", {})
        device_active = device_energy_alarm.get("active", False)
        if not device_active:
            continue
        com.shared_information["switchable_devices"].append(
            com.SwitchDevice(
                name=device,
                type=data[device]["type"],
                ip=data[device]["ip"],
                status=False,
            )
        )


def handle_switch_information(switchable_devices: list) -> None:
    """
    Call up data page of the transferred device. Save the energy and device
    temperature to an InfluxDB.
    :param switchable_devices:
    :return: None
    """
    for device in switchable_devices:
        device.status = plugins[device.type + ":switch-status"](device, switch_watcher)


def get_switch_information_for_user() -> str:
    return_string = ""
    if not com.shared_information["switchable_devices"]:
        return "No devices are configured for switching."
    for device in com.shared_information["switchable_devices"]:
        if device.status:
            return_string += f"{device.name}: On\n"
        else:
            return_string += f"{device.name}: Off\n"
    return return_string


def main() -> None:
    pass


if __name__ == "__main__":
    main()
