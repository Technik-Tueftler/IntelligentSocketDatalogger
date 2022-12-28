#!/usr/bin/env python3
# -*- coding: utf-8 -*-
class Collection:
    def __init__(self):
        self.map = {}

    def register(self, name):
        def wrapper(func):
            self.map[name] = func
        return wrapper

    def __getitem__(self, key):
        return self.map[key]


def main() -> None:
    pass


if __name__ == "__main__":
    main()
