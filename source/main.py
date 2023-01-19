#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main function for cyclic call of all set devices and capture of the energy and the
device temperature.
"""
import sys
import json
import time
from datetime import datetime

import schedule
from influxdb.exceptions import InfluxDBClientError

from source.supported_devices import plugins
from source import support_functions
from source import cost_calculation as cc
from source import logging_helper as lh
from source.constants import DEVICES_FILE_PATH

fetch_watch_hen = lh.WatchHen(device_name="fetch_handler")
write_watch_hen = lh.WatchHen(device_name="write_handler")


def fetch_device_data(settings: dict) -> None:
    """
    Call up data page of the transferred device. Save the energy and device
    temperature to an InfluxDB.
    :param settings: Settings of the transferred device
    :return: None
    """
    try:
        device_data = plugins[settings["type"]](settings)
        write_data(device_data)
        fetch_watch_hen.normal_processing()
    except KeyError as err:
        fetch_watch_hen.failure_processing(
            type(err).__name__,
            err,
            f'- handler for {settings["device_name"]} is not implemented in plugin file.',
        )


def write_data(device_data: list) -> bool:
    """
    Write fetched data to Db with own context manager.
    :param device_data: fetched data
    :return: Feedback if write to database was successful
    """
    try:
        with support_functions.InfluxDBConnection() as conn:
            conn.switch_database(support_functions.login_information.db_name)
            conn.write_points(device_data)
            write_watch_hen.normal_processing()
    except InfluxDBClientError as err:
        write_watch_hen.failure_processing(
            type(err).__name__, err, "- data could not be saved to database."
        )
    except ConnectionError as err:
        write_watch_hen.failure_processing(
            type(err).__name__, err, "- no connection to database."
        )


def main() -> None:
    """
    Scheduling function for regular call.
    :return: None
    """
    try:
        data = {}
        keys = ["ip", "update_time", "type"]
        with open(DEVICES_FILE_PATH, encoding="utf-8") as file:
            data = json.load(file)
        request_start_time = cc.check_cost_calc_request_time()
        for device_name, settings in data.items():
            if all(key in settings for key in keys):
                device_settings = settings | {
                    "device_name": device_name,
                    "watch_hen": lh.WatchHen(device_name=device_name),
                }
                schedule.every(settings["update_time"]).seconds.do(
                    fetch_device_data, device_settings
                )
            cost_calc_requested = cc.check_cost_calc_requested(settings)
            if cost_calc_requested["start_schedule_task"] is True:
                schedule.every().day.at(request_start_time).do(
                    cc.cost_calc_handler,
                    device_name,
                    settings,
                    cost_calc_requested,
                )

        while True:
            schedule.run_pending()
            time.sleep(1)
    except FileNotFoundError as err:
        error_message = (
            f"The configuration file for the devices could not be found: {err}"
        )
        lh.write_log(lh.LoggingLevel.CRITICAL.value, error_message)
        sys.exit(0)


if __name__ == "__main__":
    timestamp_now = datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S")
    message = f"Start Program: {timestamp_now} UTC"
    lh.write_log(lh.LoggingLevel.INFO.value, message)
    support_functions.check_and_verify_db_connection()
    if support_functions.login_information.verified is not False:
        main()
