#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collection of support function for main app with definition of classes and verification functions.
"""
from dataclasses import dataclass
import os
import influxdb.resultset
from requests.exceptions import ConnectTimeout
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError


@dataclass
class DataApp:  # pylint: disable=too-many-instance-attributes
    """
    Class to structure all environment variables and verify them.
    """

    db_ip_address: str = os.getenv("DB_IP_ADDRESS")
    db_user_name: str = os.getenv("DB_USER_NAME")
    db_user_password: str = os.getenv("DB_USER_PASSWORD", "")
    db_name: str = os.getenv("DB_NAME")
    ssl: bool = False
    verify_ssl: bool = False
    db_port: int = 0
    verified: bool = True
    try:
        if None in (db_ip_address, db_user_name, db_name):
            raise ValueError(
                "Not all needed env variable are defined. Please check the documentation and "
                "add all necessary login information."
            )
        db_port = os.getenv("DB_PORT")
        ssl = os.getenv("SSL")
        verify_ssl = os.getenv("VERIFY_SSL")
        if db_port is None:
            db_port = 8086
        elif db_port.isdecimal():
            db_port = int(db_port)
        else:
            raise ValueError("Environment variable DB_PORT is not a decimal number.")
        if ssl is None:
            ssl = False
        elif ssl == ("True" or "true"):
            ssl = True
        elif ssl == ("False" or "false"):
            ssl = False
        else:
            raise ValueError("Environment variable SSL is not True or False.")
        if verify_ssl is None:
            verify_ssl = False
        elif verify_ssl == ("True" or "true"):
            verify_ssl = True
        elif verify_ssl == ("False" or "false"):
            verify_ssl = False
        else:
            raise ValueError("Environment variable VERIFY_SSL is not True or False.")
    except ValueError as err:
        verified = False
        print(err)


class InfluxDBConnection(InfluxDBClient):
    """
    InfluxDB's connection class for handling in context manager
    """

    def __init__(self):
        self.login_information = login_information
        super().__init__(
            host=login_information.db_ip_address,
            port=login_information.db_port,
            username=login_information.db_user_name,
            password=login_information.db_user_password,
            ssl=login_information.ssl,
            verify_ssl=login_information.verify_ssl,
        )

    def __enter__(self):
        return self


def check_and_verify_db_connection() -> None:
    """Function controls the passed env variables and checks if they are valid."""
    try:
        with InfluxDBConnection() as connection:
            connection.ping()
            if not any(
                    True
                    for db in connection.get_list_database()
                    if db["name"] == login_information.db_name
            ):
                connection.create_database(login_information.db_name)
            connection.switch_database(login_information.db_name)
            login_information.verified = True
    except (InfluxDBClientError, ConnectTimeout, ConnectionError) as err:
        print(
            f"Error occurred during setting the database with error message: {err}. All login"
            f"information correct? Like database address, user name and so on? "
            f"Check dokumentation for all environment variables"
        )
        login_information.verified = False


def cost_logging(file_name: str, data: dict) -> None:
    """

    :param file_name:
    :param data: information for logging
    :return:
    """

    if not os.path.exists(os.path.join("..", "files", file_name + ".txt")):
        with open(
            os.path.join("..", "files", file_name + ".txt"), "a", encoding="utf-8"
        ) as file:
            file.write(
                "|               Period in UTC               |"
                " consumption in KWh |         Costs          |  Error rate in %  |\n"
            )
            file.write(
                "|-------------------------------------------|"
                "--------------------|------------------------|-------------------|\n"
            )

    checked_total_cost = round(data["total_cost"], 2)
    if data["cost_kwh"] >= 10:
        checked_cost_kwh = "9.99+"
    else:
        checked_cost_kwh = round(data["cost_kwh"], 3)
    checked_error_rate_one = min(100.0, round(data["error_rate_one"], 1))
    checked_error_rate_two = min(100.0, round(data["error_rate_two"], 1))

    with open(
        os.path.join("..", "files", file_name + ".txt"), "a", encoding="utf-8"
    ) as file:
        file.write(
            f"| {data['start_date']} - {data['end_date']} |{data['sum_of_energy']:>19} |"
            f"{checked_total_cost:>10} ({checked_cost_kwh:>4}€/KWh) |{checked_error_rate_one:>8} |"
            f"{checked_error_rate_two:>8} |\n"
        )


def fetch_measurements(bind_params: dict) -> influxdb.resultset.ResultSet:
    """
    Fetch measurements with transferred query parameters.
    :param bind_params: Parameters for query
    :return: All measurements which are matched tp parameters as a ResultSet
    """
    with InfluxDBConnection() as conn:
        query = (
            f'SELECT * FROM {conn.login_information.db_name}."autogen"."census" '
            f"WHERE device=$device AND time > $target_date AND time < $current_date"
        )
        return conn.query(query, bind_params=bind_params)


login_information = DataApp()


def main() -> None:
    """
    Scheduling function for regular call.
    :return: None
    """


if __name__ == "__main__":
    main()
