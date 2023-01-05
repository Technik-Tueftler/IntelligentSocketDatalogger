#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The module includes all the handler to register any sockets that the user wants to have.
"""
import urllib.request
from urllib.error import HTTPError, URLError
from datetime import datetime
import json


def setup(plugins) -> None:
    """
    The configuration function for registering user devices that are not
    yet available as generic devices. This allows the end user to add any device
    to the app, as long as the device provides an interface.
    :param plugins: Collection of all possible devices that have been registered.
    :return: None
    """
    @plugins.register("intelligent_socket:version-7")
    def handler(settings):   # pylint: disable=function-redefined
        device_name = settings["device_name"]
        # request url under which the socket can be reached
        request_url = "http://" + settings["ip"] + "/status"
        try:
            with urllib.request.urlopen(request_url, timeout=10) as url:
                # Response of the device as an example in which the data are stored as json.
                data = json.loads(url.read().decode())
                # Parsing the data into the format for the database.
                # All shown tags and fields are necessary to provide all functionalities.
                device_data = [
                    {
                        "measurement": "census",
                        "tags": {"device": device_name},
                        "time": datetime.utcnow(),
                        "fields": {
                            "power": data["meters"][0]["power"],
                            "is_valid": data["meters"][0]["is_valid"],
                            "fetch_success": True,
                            "energy_wh": data["meters"][0]["power"]
                            * settings["update_time"]
                            / 3600,
                        },
                    }
                ]
                return device_data
        except (HTTPError, URLError, ConnectionResetError, TimeoutError) as err:
            # Error handling, if the device does not respond.
            print(err)
            device_data = [
                {
                    "measurement": "census",
                    "tags": {"device": device_name},
                    "time": datetime.utcnow(),
                    "fields": {"fetch_success": False},
                }
            ]
            return device_data
