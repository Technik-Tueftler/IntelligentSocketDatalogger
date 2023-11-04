#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collection of switch function with definition of classes and device handle functions.
"""
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
                ip_address=data[device]["ip"],
                status=False,
            )
        )


def handle_switch_information(switchable_devices: list) -> None:
    """
    Call up data page of the transferred device. Save the energy and device
    temperature to an InfluxDB. This function can theoretically also be called
    cyclically via schedule.every
    :param switchable_devices:
    :return: None
    """
    for device in switchable_devices:
        device.status = plugins[device.type + ":switch-status"](device, switch_watcher)


def toggle_switch(device_name: str, state: bool) -> str:
    """
    Function to handle the switch request of a device from user callback.
    :param device_name: Device to be switched
    :param state: Switch state for device
    :return: User information for switch request as string
    """
    try:
        device = None
        for element in com.shared_information["switchable_devices"]:
            if element.name == device_name:
                device = element
                break
        if device is None:
            return f"Error - no device with the name {device_name} was found."
        if device.status == state:
            return (f"Error - Device {device_name} cannot be switched to value because it is "
                    f"already in this state.")
        if state is True:
            plugins[device.type + ":switch-on"](device, switch_watcher)
            device.status = True
            return "Device has been switched on"
        plugins[device.type + ":switch-off"](device, switch_watcher)
        device.status = False
        return "Device has been switched off"
    except KeyError as err:
        message = f"Implementation for switching {device.type} in plugin file was not found"
        switch_watcher.failure_processing(
            type(err).__name__,
            err,
            ("- " + message),
        )
        return message


def get_switch_information_for_user() -> str:
    """
    Function create the information for user which device have which status of
    the switch.
    :return: User information
    """
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
    """
    Scheduling function for regular call.
    :return: None
    """


if __name__ == "__main__":
    main()
