#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def setup(plugins):
    print("Der Gerät ist registriert")

    @plugins.register("derGeraet:version-7")
    def handler(resp):
        parsed_content = {"name": "ich bin ein Gerät Nr 7"}
        # Parse reponse
        return parsed_content


def main() -> None:
    pass


if __name__ == "__main__":
    main()
