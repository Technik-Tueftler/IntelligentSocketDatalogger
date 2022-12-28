#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def setup(plugins):
    @plugins.register("derGeraet:version-7")
    def handler(resp):
        parsed_content = {"name": "ich bin ein Gerät Nr 7"}
        # Parse reponse
        return parsed_content
