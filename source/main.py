#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main function for cyclic call of all set devices and capture of the energy and the
device temperature.
"""
import sys
import json
import time
import urllib.request
from datetime import datetime
import schedule
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError
import support_functions


def fetch_shelly_data(device_name: str, settings: dict) -> None:
    """
    Call up data page of the transferred device. Save the energy and device
    temperature to an InfluxDB.
    :param device_name: Transferred device name
    :param settings: Settings of the transferred device
    :return: None
    """
    client = InfluxDBClient(
        host=connection.db_ip_address,
        port=connection.db_port,
        username=connection.db_user_name,
        password=connection.db_user_password,
        ssl=connection.ssl,
        verify_ssl=connection.verify_ssl,
    )
    request_url = "http://" + settings["ip"] + "/status"
    try:
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
            client.switch_database(connection.db_name)
            client.write_points(device_data)
            client.close()
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
        sys.exit(0)


if __name__ == "__main__":
    print("Start program")
    connection = support_functions.DataApp()
    support_functions.check_and_verify_db_connection(connection)
    if connection.verified is not False:
        main()
