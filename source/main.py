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
from queue import Queue

import requests
import schedule
from influxdb.exceptions import InfluxDBClientError

from source.supported_devices import plugins
from source import support_functions
from source import calculations as cc
from source import logging_helper as lh
from source import telegram_handler as th
from source.constants import DEVICES_FILE_PATH

write_watch_hen = lh.WatchHen(device_name="write_handler")
main_to_th = Queue()
th_to_main = Queue()


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
        if device_data[0]["fields"]["fetch_success"]:
            settings["watch_hen"].normal_processing()
    except KeyError as err:
        settings["watch_hen"].failure_processing(
            type(err).__name__,
            err,
            f'- handler for {settings["device_name"]} is not implemented in plugin file.',
        )


def write_data(device_data: list):
    """
    Write fetched data to Db with own context manager.
    :param device_data: fetched data
    :return: None
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
    except requests.exceptions.ConnectionError as err:
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
        cc.check_cost_calc_request_time()
        for device_name, settings in data.items():
            if all(key in settings for key in keys):
                device_settings = settings | {
                    "device_name": device_name,
                    "watch_hen": lh.WatchHen(device_name=device_name),
                }
                schedule.every(settings["update_time"]).seconds.do(
                    fetch_device_data, device_settings
                )
            calc_requested = cc.check_calc_requested(settings)
            if calc_requested["start_schedule_task"] is True:
                support_functions.validation_power_on_parameter(
                    settings, calc_requested
                )
                schedule.every().day.at(
                    cc.config_request_time["calc_request_time_daily"]
                ).do(
                    cc.calculation_handler,
                    settings | {"device_name": device_name},
                    calc_requested,
                )
                # Start Telegram-Bot and send message
                th.check_and_verify_bot_connection()
                if th.verified_bot_connection["verified"]:
                    th.send_message(message)

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
