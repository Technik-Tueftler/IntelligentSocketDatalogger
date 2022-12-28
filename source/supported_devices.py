#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from shelly import setup


class Collection:
    def __init__(self):
        self.map = {}

    def register(self, name):
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


#@plugins.register("shelly:plug-x")
#def handler(resp):
 #   parsed_content = {"name": "ich bin ein shelly plug x"}
  #  return parsed_content


def main() -> None:
    pass


if __name__ == "__main__":
    main()
