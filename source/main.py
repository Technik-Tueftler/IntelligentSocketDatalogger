#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main function for cyclic call of all set devices and capture of the energy and the
device temperature.
"""
import os
import sys
import json
import time
import urllib.request
from urllib.error import HTTPError, URLError
from datetime import datetime

import schedule
from influxdb.exceptions import InfluxDBClientError

from source import support_functions
from source import cost_calculation as cc
from source import logging_helper as lh
from source.constants import DEVICES_FILE_PATH, TIMEOUT_RESPONSE_TIME

# D:\Workspace\git\ShellyPlugDatalogger
# D:\Workspace\git\ShellyPlugDatalogger\source
# sys.path.append(r"D:\Workspace\git\ShellyPlugDatalogger")
print("----------------")
print(os.getcwd())
print("----------------")
for p in sys.path:
    print(p)


def fetch_shelly_data(device_name: str, settings: dict) -> None:
    """
    Call up data page of the transferred device. Save the energy and device
    temperature to an InfluxDB.
    :param device_name: Transferred device name
    :param settings: Settings of the transferred device
    :return: None
    """
    request_url = "http://" + settings["ip"] + "/status"
    device_data = []
    try:
        with urllib.request.urlopen(request_url, timeout=TIMEOUT_RESPONSE_TIME) as url:
            data = json.loads(url.read().decode())
            # Jedes Tag abfragen, ob es wirklich vorhanden ist und nur dann eintragen. So
            # könnten mehr Steckdosen unterstützt werden.
            device_data = [
                {
                    "measurement": "census",
                    "tags": {"device": device_name},
                    "time": datetime.utcnow(),
                    "fields": {
                        "power": data["meters"][0]["power"],
                        "is_valid": data["meters"][0]["is_valid"],
                        "device_temperature": data["temperature"],
                        "fetch_success": True,
                        "energy_wh": data["meters"][0]["power"]
                        * settings["update_time"]
                        / 3600,
                    },
                }
            ]
    except (HTTPError, URLError, ConnectionResetError, TimeoutError) as err:
        error_message = (
            f"Error occurred while fetching data from {device_name} with error "
            f"message: {err}."
        )
        lh.write_log(lh.LoggingLevel.ERROR.value, error_message)
        device_data = [
            {
                "measurement": "census",
                "tags": {"device": device_name},
                "time": datetime.utcnow(),
                "fields": {"fetch_success": False},
            }
        ]
    finally:
        write_data(device_name, device_data)


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
            if "ip" in settings and "update_time" in settings:
                schedule.every(settings["update_time"]).seconds.do(
                    fetch_shelly_data, device_name, settings
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
