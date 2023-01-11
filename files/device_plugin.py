#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The module includes all the handler to register any sockets that the user wants to have.
"""


def setup(plugins) -> None:
    """
    The configuration function for registering user devices that are not
    yet available as generic devices. This allows the end user to add any device
    to the app, as long as the device provides an interface.
    :param plugins: Collection of all possible devices that have been registered.
    :return: None

    Check implemented devices in source/devices_shelly.py as example
    """
    @plugins.register("intelligent_socket:version-7")
    def handler(settings):   # pylint: disable=function-redefined
        # Get device name with:
        _ = settings["device_name"]
        # request url under which the socket can be reached e.g.
            # --> request_url = "http://" + settings["ip"] + "/status"
            # with <urllib.request>
        # Edit returned data from device and return:
            # Parsing the data into the format for the database.
            # All shown tags and fields are necessary to provide all functionalities.
                # "measurement": "census",
                # "tags": {"device": device_name},
                # "time": timestamp in UTC of the measurement with datetime.utcnow(),
                # "fields": {
                    # "power": value of power in W,
                    # "fetch_success": must contain an fetch_succes key being a boolean,
                        # saying if the request succeeded or not
                    # "energy_wh": converted power into energy in Wh
