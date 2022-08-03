#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pip install schedule
# pip install influxdb
import os
import json
import schedule
import time
import urllib.request
from datetime import datetime
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError
from requests.exceptions import ConnectTimeout


def fetch_shelly_data(device_name: str, settings: dict):
    client = InfluxDBClient(host='192.168.178.39',
                            port=8086,
                            username='shellyplug',
                            password='',
                            ssl=False,
                            verify_ssl=False)

    request_url = "http://" + settings["ip"] + "/meter/0"
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
                    "energy": data["power"],
                    "is_valid": data["is_valid"]
                }
            }
        ]
        try:
            client.switch_database('power_consumption')
            client.write_points(device_data)
            client.close()
        except InfluxDBClientError as err:
            print(f"Error occurred during data saving with error message: {err}.")
            # Add missing measurement to queue


def check_and_verify_env_variables() -> dict:
    """Function controls the passed env variables and checks if they are valid."""
    environment_data = {
        "db_ip_address": os.getenv("DB_IP_ADDRESS"),
        "db_user_name": os.getenv("DB_USER_NAME"),
        "db_user_password": os.getenv("DB_USER_PASSWORD", ""),
        "db_name": os.getenv("DB_NAME"),
        "ssl": os.getenv("SSL", False),
        "verify_ssl": os.getenv("VERIFY_SSL", False),
        "all_verified": True
    }

    if any(True for value in environment_data.values() if value is None):
        environment_data["all_verified"] = False
        print(
            "Not all env variable are defined. Please check the documentation and add all "
            "necessary login information."
        )
        return
    try:
        client = InfluxDBClient(host=environment_data["db_ip_address"],
                                port=8086,
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


def main() -> None:
    with open("../files/devices.json") as f:
        data = json.load(f)
    for device_name, settings in data.items():
        schedule.every(settings["update_time"]).seconds.do(fetch_shelly_data, device_name, settings)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    # main()
    check_and_verify_env_variables()
