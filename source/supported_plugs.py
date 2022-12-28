#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from collect import Collection
from shelly import setup

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
