#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from supported_plugs import plugins


def main() -> None:
    data_to_parse = {"unsinn": "das ist der response vom Geraet"}
    # run the handler
    # breakpoint()
    parsed_data = plugins["shelly:plug-s"](data_to_parse)
    print(parsed_data)
    parsed_data = plugins["shelly:em3"](data_to_parse)
    print(parsed_data)
    #parsed_data = plugins["shelly:plug-x"](data_to_parse)
    #print(parsed_data)
    #parsed_data = plugins["derGeraet:version-7"](data_to_parse)
    #print(parsed_data)


if __name__ == "__main__":
    main()
