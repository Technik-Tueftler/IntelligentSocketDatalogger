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
from datetime import datetime
import schedule
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError
from requests.exceptions import ConnectTimeout


def fetch_shelly_data(device_name: str, settings: dict, env_data: dict) -> None:
    """
    Call up data page of the transferred device. Save the energy and device
    temperature to an InfluxDB.
    :param device_name: Transferred device name
    :param settings: Settings of the transferred device
    :param env_data: App settings
    :return: None
    """
    client = InfluxDBClient(host=env_data["db_ip_address"],
                            port=env_data["db_port"],
                            username=env_data["db_user_name"],
                            password=env_data["db_user_password"],
                            ssl=env_data["ssl"],
                            verify_ssl=env_data["verify_ssl"])
    request_url = "http://" + settings["ip"] + "/status"
    try:
        with urllib.request.urlopen(request_url) as url:
            data = json.loads(url.read().decode())
            device_data = [
                {
                    "measurement": "census",
                    "tags": {
                        "device": device_name
                    },
                    "time": datetime.utcnow(),
                    "fields": {
                        "power": data["meters"][0]["power"],
                        "is_valid": data["meters"][0]["is_valid"],
                        "device_temperature":data["temperature"],
                        "energy_wh": data["meters"][0]["power"] * settings["update_time"] / 3600
                    }
                }
            ]
            client.switch_database(env_data["db_name"])
            client.write_points(device_data)
            client.close()
    except InfluxDBClientError as err:
        print(f"Error occurred during data saving with error message: {err}.")
        # Add missing measurement to queue
    except urllib.error.URLError as err:
        # logging File Eintrag hinzufügen und unter /files ablegen
        print(f"Error occurred during data fetching from {device_name} with error message: {err}.")
    except ConnectionError as err:
        print(f"Error occurred during connecting to the database with error message: {err}. The "
              f"service/app will be closed. Please check the environment variables for the "
              f"connection to database")
        sys.exit(0)


def check_and_verify_env_variables() -> dict:
    """Function controls the passed env variables and checks if they are valid."""
    environment_data = {
        "db_ip_address": os.getenv("DB_IP_ADDRESS"),
        "db_user_name": os.getenv("DB_USER_NAME"),
        "db_user_password": os.getenv("DB_USER_PASSWORD", ""),
        "db_name": os.getenv("DB_NAME"),
        "all_verified": True
    }
    if os.getenv("DB_PORT") is None:
        environment_data["db_port"] = 8086
    if os.getenv("SSL") is None:
        environment_data["ssl"] = False
    if os.getenv("VERIFY_SSL") is None:
        environment_data["verify_ssl"] = False
    if any(True for value in environment_data.values() if value is None):
        environment_data["all_verified"] = False
        print(
            "Not all env variable are defined. Please check the documentation and add all "
            "necessary login information."
        )
        return environment_data
    try:
        client = InfluxDBClient(host=environment_data["db_ip_address"],
                                port=environment_data["db_port"],
                                username=environment_data["db_user_name"],
                                password=environment_data["db_user_password"],
                                ssl=environment_data["ssl"],
                                verify_ssl=environment_data["verify_ssl"])
        client.ping()
        client.switch_database(environment_data["db_name"])
        client.close()
    except (InfluxDBClientError, ConnectTimeout) as err:
        print(f"Error occurred during setting the database with error message: {err}. All login"
              f"information correct? Like database address, user name and so on? "
              f"Check dokumentation for all environment variables")
        environment_data["all_verified"] = False
    finally:
        return environment_data  # pylint: disable=lost-exception


def main(env_data: dict) -> None:
    """
    Scheduling function for regular call.
    :param env_data: Dictionary with app information.
    :return: None
    """
    try:
        # Check if file exist, if not close app with message
        with open("../files/devices.json", encoding="utf-8") as file:
            data = json.load(file)
        for device_name, settings in data.items():
            schedule.every(settings["update_time"]).seconds.do(fetch_shelly_data,
                                                               device_name,
                                                               settings,
                                                               env_data)
        while True:
            schedule.run_pending()
            time.sleep(1)
    except FileNotFoundError as err:
        print(f"The configuration file for the devices could not be found. Please put it in the "
              f"folder you passed with the environment variables. Error occurred during start the "
              f"app with error message: {err}.")
        sys.exit(0)


if __name__ == "__main__":
    print("Start program")
    verified_env_data = check_and_verify_env_variables()
    if verified_env_data["all_verified"] is not False:
        main(verified_env_data)
