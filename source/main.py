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

from supported_devices import plugins
from source import support_functions
from source import cost_calculation as cc
from source import logging_helper as lh
from source.constants import DEVICES_FILE_PATH


def fetch_device_data(device_name: str, settings: dict) -> None:
    """
    Call up data page of the transferred device. Save the energy and device
    temperature to an InfluxDB.
    :param device_name: Transferred device name
    :param settings: Settings of the transferred device
    :return: None
    """
    device_settings = settings | {"device_name": device_name}
    try:
        device_data = plugins[settings["type"]](device_settings)
        write_data(device_name, device_data)
    except KeyError as err:
        print(err)
        error_message = (
            f'Error occurred during fetch data from {device_name} with type: {settings["type"] }'
            f"with key-error. Is the handler available for this type?"
        )
        lh.write_log(lh.LoggingLevel.ERROR.value, error_message)


def write_data(device_name: str, device_data: list) -> None:
    """
    Write fetched data to Db with own context manager.
    :param device_name: Transferred device name
    :param device_data: fetched data
    :return: None
    """
    try:
        with support_functions.InfluxDBConnection() as conn:
            conn.switch_database(support_functions.login_information.db_name)
            conn.write_points(device_data)
    except InfluxDBClientError as err:
        error_message = f"Error occurred during data saving with error message: {err}."
        lh.write_log(lh.LoggingLevel.ERROR.value, error_message)
    except ConnectionError as err:
        error_message = (
            f"Error occurred during connecting to the database from {device_name} "
            f"with error message: {err}"
        )
        lh.write_log(lh.LoggingLevel.ERROR.value, error_message)


def main() -> None:
    """
    Scheduling function for regular call.
    :return: None
    """
    try:
        data = {}
        with open(DEVICES_FILE_PATH, encoding="utf-8") as file:
            data = json.load(file)
        request_start_time = cc.check_cost_calc_request_time()
        for device_name, settings in data.items():
            if ("ip" and "update_time" and "type") in settings:
                schedule.every(settings["update_time"]).seconds.do(
                    fetch_device_data, device_name, settings
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
        lh.write_log(lh.LoggingLevel.ERROR.value, error_message)
        sys.exit(0)


if __name__ == "__main__":
    timestamp_now = datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S")
    message = f"Start Program: {timestamp_now} UTC"
    lh.write_log(lh.LoggingLevel.INFO.value, message)
    support_functions.check_and_verify_db_connection()
    if support_functions.login_information.verified is not False:
        main()
