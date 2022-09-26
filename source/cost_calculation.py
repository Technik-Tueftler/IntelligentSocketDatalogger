#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collection of calculation function for main app to calculate the energy for device
in Daily, monthly, and yearly rhythm.
"""
import re
import json
from datetime import datetime, timedelta
import support_functions as sf
from dateutil.relativedelta import relativedelta

TIME_OF_DAY_SCHEDULE_MATCH = r"^(?:[01]\d|2[0-3]):(?:[0-5]\d)$"
DAY_OF_MONTH_SCHEDULE_MATCH = r"^[\d]{2}$"
DATE_OF_YEAR_SCHEDULE_MATCH = r"^[\d]{2}[.][\d]{2}$"
TIMESTAMP_FORMAT_INPUT = "%Y-%m-%dT%H:%M:%S.%fZ"
TIMESTAMP_FORMAT_OUTPUT = "%Y-%m-%dT%H:%M:%S"


def check_cost_calc_request_time() -> str:
    """
    Check if a start time is given for cost calculation and have the right format. If something is
    wrong, a default time is returned.
    :return: Start time in string format
    """
    # Wenn es fehlschlägt, muss auch ein log Eintrag erstellt werden
    try:
        checked_requested_start_time = "00:00"
        with open("../files/config.json", encoding="utf-8") as file:
            data = json.load(file)
            if ("general" in data) and ("cost_calc_request_time" in data["general"]):
                requested_start_time = data["general"]["cost_calc_request_time"]
                if (
                    re.search(TIME_OF_DAY_SCHEDULE_MATCH, requested_start_time)
                    is not None
                ):
                    checked_requested_start_time = requested_start_time
        return checked_requested_start_time

    except FileNotFoundError as err:
        print(
            f"The file for general configuration could not be found. Please put it in the "
            f"folder you passed with the environment variables. The default values are used. "
            f"Error occurred during start the app with error message: {err}."
        )
        return checked_requested_start_time


def check_cost_config() -> float:
    """
    Check if a cost config for KWh is given for cost calculation and have the right format.
    If something is wrong, a default time is returned and a log entry is written.
    :return: price per KWh as a float
    """
    # Wenn es fehlschlägt, muss auch ein log Eintrag erstellt werden
    default_price = 0.3
    try:
        with open("../files/config.json", encoding="utf-8") as file:
            data = json.load(file)
            if ("general" in data) and ("price_kwh" in data["general"]):
                requested_kwh_price = data["general"]["price_kwh"]
                if not isinstance(requested_kwh_price, float):
                    requested_kwh_price = requested_kwh_price.replace(",", ".")
                checked_requested_kwh_price = round(float(requested_kwh_price), 3)
        return checked_requested_kwh_price

    except FileNotFoundError as err:
        print(
            f"The file for general configuration could not be found. Please put it in the "
            f"folder you passed with the environment variables. The default values are used. "
            f"Error occurred during start the app with error message: {err}."
        )
        return default_price
    except ValueError as err:
        print(
            f"The setting for the price is not a number. A default value of 0.30€ was assumed. "
            f"Error message: {err}"
        )
        return default_price


def cost_calc(
    device_name: str,
    settings: dict,
    current_timestamp: datetime,
    time_difference: relativedelta,
) -> None:
    """
    Calculate the monthly cost for a specific device.
    :param device_name: Name of the device
    :param settings: device parameters
    :param current_timestamp: Now date and time from request
    :param time_difference: needed time difference for calculation
    :return: None
    """
    start_date = current_timestamp - time_difference
    start_date_format = start_date.strftime("%Y-%m-%d %H:%M:%S")
    end_date = current_timestamp
    end_date_format = end_date.strftime("%Y-%m-%d %H:%M:%S")

    result = sf.fetch_measurements(
        {
            "device": device_name,
            "target_date": start_date_format,
            "current_date": end_date_format,
        }
    )

    success_measurements = list(
        filter(
            lambda measurement: measurement["fetch_success"] is True,
            result.get_points(),
        )
    )
    failed_measurements = list(
        filter(
            lambda measurement: measurement["fetch_success"] is False,
            result.get_points(),
        )
    )
    sum_of_energy_in_kwh = round(
        (sum(element["energy_wh"] for element in success_measurements) / 1000), 2
    )
    cost_kwh = check_cost_config()
    if (len(success_measurements) + len(failed_measurements)) == 0:
        return
    max_values = ((end_date - start_date).total_seconds()) / settings["update_time"]

    data = {
        "start_date": start_date_format,
        "end_date": end_date_format,
        "sum_of_energy": sum_of_energy_in_kwh,
        "total_cost": sum_of_energy_in_kwh * cost_kwh,
        "cost_kwh": cost_kwh,
        "error_rate_one": len(failed_measurements)
        * 100
        / (len(success_measurements) + len(failed_measurements)),
        "error_rate_two": (max_values - len(success_measurements)) * 100 / max_values,
    }
    if time_difference.days == 1:
        sf.cost_logging(device_name + "_day", data)
    elif time_difference.months == 1:
        sf.cost_logging(device_name + "_month", data)
    elif time_difference.years == 1:
        sf.cost_logging(device_name + "_year", data)
    # Logging-Eintrag erstellen, dass keine Summe berechnet werden konnte


def last_day_of_month(date):
    """
    Functions calculate the last day of the provided date.
    :param date: Date from which the last day is to be returned.
    :return: Returns a date with changed day which is the last of the month.
    """
    if date.month == 12:
        return date.replace(day=31)
    return date.replace(month=date.month + 1, day=1) - timedelta(days=1)


def check_month_parameter(month: str) -> int:
    """
    Check the month parameter and set default value if it is not plausible.
    :param month: Parameter for month calculation as String
    :return: Returns the plausibilized value as Integer
    """
    checked_month = int(month)
    if checked_month < 1 or checked_month > 12:
        return 1
    return checked_month


def check_year_parameter(month_year: str) -> dict:
    """
    Check the month and year parameter and set default value if it is not plausible.
    :param month_year: Parameter year calculation as String
    :return: Returns the plausibilized values in a List
    """
    values = {"day": 1, "month": 1}
    split_date = month_year["cost_year"].split(".")
    values["month"] = check_month_parameter(split_date[1])
    values["day"] = int(split_date[0])
    return values


def check_cost_calc_requested(settings: dict) -> dict:
    """
    Check if a cost calculation is requested for this device and if it has the correct formatting.
    :param settings: Settings for the selected device
    :return: The requested calculations in a dict
    """
    start_schedule_task = {
        "start_schedule_task": False,
        "cost_day": False,
        "cost_month": None,
        "cost_year": None,
    }
    if ("cost_calc_day" in settings) and (settings["cost_calc_day"]):
        start_schedule_task["cost_day"] = True
        start_schedule_task["start_schedule_task"] |= True
    if "cost_month" in settings:
        if re.search(DAY_OF_MONTH_SCHEDULE_MATCH, settings["cost_month"]) is not None:
            start_schedule_task["cost_month"] = check_month_parameter(
                settings["cost_month"]
            )
            start_schedule_task["start_schedule_task"] |= True
    if "cost_year" in settings:
        if re.search(DATE_OF_YEAR_SCHEDULE_MATCH, settings["cost_year"]) is not None:
            start_schedule_task["cost_year"] = check_year_parameter(
                settings["cost_year"]
            )
            start_schedule_task["start_schedule_task"] |= True
    return start_schedule_task


def check_matched_day(current_date: datetime.datetime, target_day: int) -> bool:
    """
    Checks if the current day matches the set day. In addition, if the set day is not possible,
    the last day in this month is checked.
    :param current_date: Current timestamp.
    :param target_day: Target day for the calculation.
    :return: Day matched as a boolean.
    """
    last_day_of_current_month = last_day_of_month(current_date)
    if target_day > last_day_of_current_month.day:
        if current_date.day == last_day_of_current_month.day:
            return True
    else:
        if current_date.day == target_day:
            return True
    return False


def check_matched_day_and_month(
    current_date: datetime.datetime, target_day: int, target_month: int
) -> bool:
    """
    Checks if the current day and month matches the set date. In addition, if the set day is not
    possible, the last day in this month is checked.
    :param current_date: Current timestamp.
    :param target_day: Target day for the calculation.
    :param target_month: Target month for the calculation.
    :return: Day matched as a boolean.
    """
    if check_matched_day(current_date, target_day):
        if current_date.month == target_month:
            return True
    return False


def cost_calc_handler(
    device_name: str,
    settings: dict,
    cost_calc_requested: dict,
) -> None:
    """
    Check with costs are requested and call the correct calculations.
    :param device_name: Name of the device
    :param settings: device parameters
    :param cost_calc_requested: Structure which calculations are requested
    :return: None
    """
    current_timestamp = datetime.utcnow()
    if cost_calc_requested["cost_day"]:
        cost_calc(
            device_name,
            settings,
            current_timestamp,
            relativedelta(days=1),
        )
    if cost_calc_requested["cost_month"] is not None:
        if check_matched_day(current_timestamp, cost_calc_requested["cost_month"]):
            cost_calc(
                device_name,
                settings,
                current_timestamp,
                relativedelta(months=1),
            )
    if cost_calc_requested["cost_year"] is not None:
        if check_matched_day_and_month(
            current_timestamp, cost_calc_requested["day"], cost_calc_requested["month"]
        ):
            cost_calc(device_name, settings, current_timestamp, relativedelta(years=1))


def main() -> None:
    """
    Scheduling function for regular call.
    :return: None
    """
    data = {
        "ip": "192.168.178.200",
        "update_time": 30,
        "cost_calc_day": True,
        "cost_calc_month": "01",
        "cost_calc_year": "01.01",
    }
    cost_calc(
        "Kuehlschrank",
        data,
        datetime.utcnow(),
        relativedelta(years=1),
    )


if __name__ == "__main__":
    main()
