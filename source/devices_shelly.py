#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module contains all the handlers needed for Shelly intelligent sockets.
"""
import json
import urllib.request
import urllib.parse
from urllib.error import HTTPError, URLError
from datetime import datetime
from source.constants import TIMEOUT_RESPONSE_TIME
from source.communication import SwitchDevice
from source.logging_helper import WatchHen


def switch_status(settings: dict) -> bool:
    try:
        if settings["type"] == "shelly:plug-s":
            request_url = "http://" + settings["ip"] + "/relay/0"
            with urllib.request.urlopen(
                    request_url, timeout=TIMEOUT_RESPONSE_TIME
            ) as url:
                data = json.loads(url.read().decode())
            return data["ison"]
        return False
    except (HTTPError, URLError, ConnectionResetError, TimeoutError) as err:
        return False


def setup(plugins) -> None:
    """
    Configuration function to register all possible shelly devices in a
    collection. Here a handler is defined for each device type and how the
    data collection and processing must be done.
    :param plugins: Collection of all possible devices that have been registered.
    :return: None
    """

    @plugins.register("shelly:plug-s")
    def handler(settings):  # pylint: disable=function-redefined
        device_name = settings["device_name"]
        request_url = "http://" + settings["ip"] + "/status"
        try:
            with urllib.request.urlopen(
                    request_url, timeout=TIMEOUT_RESPONSE_TIME
            ) as url:
                data = json.loads(url.read().decode())
                device_data = [
                    {
                        "measurement": "census",
                        "tags": {"device": device_name},
                        "time": datetime.utcnow(),
                        "fields": {
                            "power": data["meters"][0]["power"],
                            "is_valid": data["meters"][0]["is_valid"],
                            "device_temperature": data["temperature"],
                            "fetch_success": True,
                            "energy_wh": data["meters"][0]["power"]
                                         * settings["update_time"]
                                         / 3600,
                        },
                    }
                ]
                settings["watch_hen"].normal_processing()
                return device_data
        except (HTTPError, URLError, ConnectionResetError, TimeoutError) as err:
            settings["watch_hen"].failure_processing(
                type(err).__name__, err, "could not be reached"
            )
            device_data = [
                {
                    "measurement": "census",
                    "tags": {"device": device_name},
                    "time": datetime.utcnow(),
                    "fields": {"fetch_success": False},
                }
            ]
            return device_data

    @plugins.register("shelly:3em")
    def handler(settings):  # pylint: disable=function-redefined
        device_name = settings["device_name"]
        request_url = "http://" + settings["ip"] + "/status"
        try:
            with urllib.request.urlopen(
                    request_url, timeout=TIMEOUT_RESPONSE_TIME
            ) as url:
                data = json.loads(url.read().decode())
                total_power = (
                        data["emeters"][0]["power"]
                        + data["emeters"][1]["power"]
                        + data["emeters"][2]["power"]
                )
                total_energy_wh = total_power * settings["update_time"] / 3600
                device_data = [
                    {
                        "measurement": "census",
                        "tags": {"device": device_name},
                        "time": datetime.utcnow(),
                        "fields": {
                            "power": total_power,
                            "energy_wh": total_energy_wh,
                            "fetch_success": True,
                            "power_a": data["emeters"][0]["power"],
                            "power_factor_a": data["emeters"][0]["pf"],
                            "current_a": data["emeters"][0]["current"],
                            "voltage_a": data["emeters"][0]["voltage"],
                            "is_valid_a": data["emeters"][0]["is_valid"],
                            "energy_wh_a": data["emeters"][0]["power"]
                                           * settings["update_time"]
                                           / 3600,
                            "power_b": data["emeters"][1]["power"],
                            "power_factor_b": data["emeters"][1]["pf"],
                            "current_b": data["emeters"][1]["current"],
                            "voltage_b": data["emeters"][1]["voltage"],
                            "is_valid_b": data["emeters"][1]["is_valid"],
                            "energy_wh_b": data["emeters"][1]["power"]
                                           * settings["update_time"]
                                           / 3600,
                            "power_c": data["emeters"][2]["power"],
                            "power_factor_c": data["emeters"][2]["pf"],
                            "current_c": data["emeters"][2]["current"],
                            "voltage_c": data["emeters"][2]["voltage"],
                            "is_valid_c": data["emeters"][2]["is_valid"],
                            "energy_wh_c": data["emeters"][2]["power"]
                                           * settings["update_time"]
                                           / 3600,
                        },
                    }
                ]
                settings["watch_hen"].normal_processing()
                return device_data
        except (HTTPError, URLError, ConnectionResetError, TimeoutError) as err:
            settings["watch_hen"].failure_processing(
                type(err).__name__, err, "could not be reached"
            )
            device_data = [
                {
                    "measurement": "census",
                    "tags": {"device": device_name},
                    "time": datetime.utcnow(),
                    "fields": {"fetch_success": False},
                }
            ]
            return device_data

    @plugins.register("shelly:plug-s:switch-status")
    def handler(device: SwitchDevice, watcher: WatchHen):  # pylint: disable=function-redefined
        try:
            request_url = "http://" + device.ip + "/relay/0"
            with urllib.request.urlopen(request_url, timeout=10) as url:
                data = json.loads(url.read().decode())
                return data["ison"]
        except (HTTPError, URLError, ConnectionResetError, TimeoutError) as err:
            watcher.failure_processing(
                type(err).__name__,
                err,
                "- could not be reached",
            )
            return False

    @plugins.register("shelly:plug-s:switch-off")
    def handler(device: SwitchDevice, watcher: WatchHen):  # pylint: disable=function-redefined
        request_url = "http://" + device.ip + "/relay/0"
        data = urllib.parse.urlencode({"turn": "off"}).encode("utf-8")
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        req = urllib.request.Request(request_url, data, headers)

        try:
            response = urllib.request.urlopen(req, timeout=10)
            _ = response.read()
        except urllib.error.URLError as err:
            watcher.failure_processing(
                type(err).__name__,
                err,
                "- could not be reached for switching",
            )

    @plugins.register("shelly:plug-s:switch-on")
    def handler(device: SwitchDevice, watcher: WatchHen):  # pylint: disable=function-redefined
        request_url = "http://" + device.ip + "/relay/0"
        data = urllib.parse.urlencode({"turn": "on"}).encode("utf-8")
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        req = urllib.request.Request(request_url, data, headers)

        try:
            response = urllib.request.urlopen(req, timeout=10)
            _ = response.read()
        except urllib.error.URLError as err:
            watcher.failure_processing(
                type(err).__name__,
                err,
                "- could not be reached for switching",
            )


def main() -> None:
    """
    Scheduling function for regular call.
    :return: None
    """


if __name__ == "__main__":
    main()
