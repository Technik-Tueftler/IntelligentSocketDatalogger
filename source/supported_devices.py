#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module contains all necessary functions and classes to integrate
the plugin concept.
"""
from source.devices_shelly import setup


class Collection:
    """
    Collection class in which all registered devices are included and their respective handlers.
    """

    def __init__(self):
        self.map = {}

    def register(self, name: str):
        """
        Registration function for the collection. This is called to register a
        device treatment with a device type name.
        :param name: The name of the device type as string
        :return:
        """

        def wrapper(func):
            self.map[name] = func

        return wrapper

    def __getitem__(self, key):
        return self.map[key]


plugins = Collection()
setup(plugins)

try:
    from files import device_plugin

    device_plugin.setup(plugins)
except ImportError as _:
    pass


# It is also possible here to register individual devices in the generic solution.
# @plugins.register("shelly:plug-x")
# def handler(resp):
#    parsed_content = {data to store in database}
#    parsed_content


def main() -> None:
    """
    Scheduling function for regular call.
    :return: None
    """


if __name__ == "__main__":
    main()
