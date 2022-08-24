#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main function for cyclic call of all set devices and capture of the energy and the
device temperature.
"""
import sys
import json
import time
import logging
import urllib.request
from datetime import datetime
from dataclasses import dataclass
import schedule
from influxdb.exceptions import InfluxDBClientError
import support_functions


@dataclass
class LogLevel:
    """
    Configuration class for reding the logging level and provide to application.
    """

    log_levels = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    config_level: str = logging.CRITICAL
    with open("../files/config.json", encoding="utf-8") as file:
        general_config = json.load(file)["general"]
        if "log_level" in general_config:
            temp_level = general_config["log_level"]
            config_level = log_levels[temp_level]


program_logging_level = LogLevel()
logging.basicConfig(
    filename="../files/main.log",
    encoding="utf-8",
    filemode="a",
    level=program_logging_level.config_level,
    format="%(asctime)s: %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)
logging.Formatter.converter = time.gmtime


def fetch_shelly_data(device_name: str, settings: dict) -> None:
    """
    Call up data page of the transferred device. Save the energy and device
    temperature to an InfluxDB.
    :param device_name: Transferred device name
    :param settings: Settings of the transferred device
    :return: None
    """
    request_url = "http://" + settings["ip"] + "/status"
    try:
        with support_functions.InfluxDBConnection(
            login_information=login_information
        ) as conn:
            with urllib.request.urlopen(request_url) as url:
                data = json.loads(url.read().decode())
                device_data = [
                    {
                        "measurement": "census",
                        "tags": {"device": device_name},
                        "time": datetime.utcnow(),
                        "fields": {
                            "power": data["meters"][0]["power"],
                            "is_valid": data["meters"][0]["is_valid"],
                            "device_temperature": data["temperature"],
                            "energy_wh": data["meters"][0]["power"]
                            * settings["update_time"]
                            / 3600,
                        },
                    }
                ]
                conn.client.switch_database(login_information.db_name)
                conn.client.write_points(device_data)
    except InfluxDBClientError as err:
        print(f"Error occurred during data saving with error message: {err}.")

        # Add missing measurement to queue
    except urllib.error.URLError as err:
        # logging File Eintrag hinzufügen und unter /files ablegen
        print(
            f"Error occurred during data fetching from {device_name} with error message: {err}."
        )
    except ConnectionError as err:
        print(
            f"Error occurred during connecting to the database with error message: {err}. The "
            f"service/app will be closed. Please check the environment variables for the "
            f"connection to database"
        )
        logging.error(
            "Error occurred during connecting to the database with error message: %s",
            err,
        )
        sys.exit(0)


def main() -> None:
    """
    Scheduling function for regular call.
    :param app_data: app connection information
    :return: None
    """
    try:
        # Check if file exist, if not close app with message
        with open("../files/devices.json", encoding="utf-8") as file:
            data = json.load(file)
        for device_name, settings in data.items():
            schedule.every(settings["update_time"]).seconds.do(
                fetch_shelly_data, device_name, settings
            )
        while True:
            schedule.run_pending()
            time.sleep(1)
    except FileNotFoundError as err:
        print(
            f"The configuration file for the devices could not be found. Please put it in the "
            f"folder you passed with the environment variables. Error occurred during start the "
            f"app with error message: {err}."
        )
        logging.error(
            "The configuration file for the devices could not be found: %s", err
        )
        sys.exit(0)


if __name__ == "__main__":
    print(f"Start Program: {datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S')}")
    logging.debug("Start Program: %s", datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"))
    login_information = support_functions.DataApp()
    support_functions.check_and_verify_db_connection(login_information)
    if login_information.verified is not False:
        main()
