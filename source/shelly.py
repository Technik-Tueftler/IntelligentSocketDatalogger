#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def setup(plugins):
    @plugins.register("shelly:plug-s")
    def handler(resp):
        parsed_content = {"name": "ich bin ein shelly plug s"}
        # Parse reponse
        return parsed_content

    @plugins.register("shelly:em3")
    def handler(resp):
        parsed_content = {"name": "ich bin ein shelly 3EM"}
        # Parse reponse
        return parsed_content


def main() -> None:
    pass


if __name__ == "__main__":
    main()
