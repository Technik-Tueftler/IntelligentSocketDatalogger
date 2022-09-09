#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collection of calculation function for main app to calculate the energy for device
in Daily, monthly, and yearly rhythm.
"""
import os
import re
from datetime import datetime
import support_functions as sf

DAY_SCHEDULE_MATCH = r"^[\d]{2}:[\d]{2}$"
TIMESTAMP_FORMAT_INPUT = "%Y-%m-%dT%H:%M:%S.%fZ"
TIMESTAMP_FORMAT_OUTPUT = "%Y-%m-%dT%H:%M:%S"


def calc_day_cost(device_name: str, login_information: sf.DataApp) -> None:
    """
    Calculate the daily cost for a specific device.
    :param device_name: Name of the device
    :param login_information: Login information to connect with the InfluxDB
    :return: None
    """
    with sf.InfluxDBConnection(login_information=login_information) as conn:
        result = conn.query(
            f'SELECT * FROM {conn.login_information.db_name}."autogen"."census" '
            f'WHERE time > now() - 1d GROUP BY "device"'
        )

        success_measurements = list(
            filter(
                lambda measurement: measurement["fetch_success"] is True,
                result.get_points(tags={"device": device_name}),
            )
        )

        failed_measurements = list(
            filter(
                lambda measurement: measurement["fetch_success"] is False,
                result.get_points(tags={"device": device_name}),
            )
        )
        sum_of_energy = round(
            sum(element["energy_wh"] for element in success_measurements), 2
        )
        start_time = datetime.strptime(
            success_measurements[0]["time"], TIMESTAMP_FORMAT_INPUT
        )
        end_time = datetime.strptime(
            success_measurements[-1]["time"], TIMESTAMP_FORMAT_INPUT
        )
        count_measurements = len(success_measurements) + len(failed_measurements)
        if count_measurements == 0:
            return
        with open(
            os.path.join("..", "files", device_name + ".txt"), "a", encoding="utf-8"
        ) as file:
            file.write(
                f"Von {start_time.strftime(TIMESTAMP_FORMAT_OUTPUT)} bis "
                f"{end_time.strftime(TIMESTAMP_FORMAT_OUTPUT)} UTC | Verbrauch: {sum_of_energy}Wh "
                f"| {len(failed_measurements) * 100 / count_measurements}"
                f"% fehlende Messwerte.\n"
            )
        # Logging-Eintrag erstellen, dass keine Summe berechnet werden konnte"""


def calc_month_year_cost() -> None:
    """
    Calculate the daily cost for a specific device.
    :return: None
    """


def check_cost_day_requested(settings: dict) -> bool:
    """
    Check if the parameter for cost-day is available for the time and if it has the correct
    formatting.
    :param settings: Settings for the selected device
    :return: bool
    """
    if "cost_day" not in settings:
        return False
    if re.search(DAY_SCHEDULE_MATCH, settings["cost_day"]) is None:
        return False
    return True


def check_cost_month_year_requested() -> bool:
    """
    Check if the parameter for cost-month and cost-year is available for the time and if it has
    the correct formatting.
    :return: bool
    """


def main() -> None:
    """
    Scheduling function for regular call.
    :return: None
    """


if __name__ == "__main__":
    main()
