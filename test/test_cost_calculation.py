"""
Tests for cost_calculation.py
"""
from datetime import datetime

import pytest

from source.calculations import (
    last_day_of_month,
    check_month_parameter,
    check_day_parameter,
    check_matched_day,
    check_matched_day_and_month,
)


@pytest.mark.parametrize(
    "parameter_1, parameter_2, expected",
    [
        (2022, 1, 31),
        (2022, 2, 28),
        (2024, 2, 29),
        (2022, 3, 31),
        (2022, 4, 30),
        (2022, 5, 31),
        (2022, 6, 30),
        (2022, 7, 31),
        (2022, 8, 31),
        (2022, 9, 30),
        (2022, 10, 31),
        (2022, 11, 30),
        (2024, 12, 31),
    ],
)
def test_last_day_of_month(parameter_1, parameter_2, expected):
    """
    Pure test for function last_day_of_month()
    """
    result = last_day_of_month(datetime(parameter_1, parameter_2, 1))
    assert result == datetime(parameter_1, parameter_2, expected)


@pytest.mark.parametrize(
    "parameter_1, expected",
    [
        ("-1", 1),
        ("0", 1),
        ("1", 1),
        ("15", 15),
        ("31", 31),
        ("32", 1),
    ],
)
def test_check_day_parameter(parameter_1, expected):
    """
    Pure test for function check_day_parameter()
    """
    result = check_day_parameter(parameter_1)
    assert result == expected


@pytest.mark.parametrize(
    "parameter_1, expected",
    [
        ("-1", 1),
        ("0", 1),
        ("1", 1),
        ("5", 5),
        ("12", 12),
        ("13", 1),
    ],
)
def test_check_month_parameter(parameter_1, expected):
    """
    Pure test for function check_month_parameter()
    """
    result = check_month_parameter(parameter_1)
    assert result == expected


@pytest.mark.parametrize(
    "parameter_1, parameter_2, expected",
    [
        (datetime(2022, 2, 28), 15, False),
        (datetime(2022, 2, 28), 29, True),
        (datetime(2022, 2, 15), 15, True),
        (datetime(2024, 2, 28), 29, False),
    ],
)
def test_check_matched_day(parameter_1, parameter_2, expected):
    """
    Pure test for function check_matched_day()
    """
    result = check_matched_day(parameter_1, parameter_2)
    assert result == expected


@pytest.mark.parametrize(
    "parameter_1, parameter_2, parameter_3, expected",
    [
        (datetime(2022, 2, 28), 28, 2, True),
        (datetime(2022, 2, 28), 20, 2, False),
        (datetime(2022, 2, 28), 28, 3, False),
        (datetime(2022, 2, 28), 20, 3, False),
    ],
)
def test_check_matched_day_and_month(parameter_1, parameter_2, parameter_3, expected):
    """
    Pure test for function check_matched_day_and_month()
    """
    result = check_matched_day_and_month(parameter_1, parameter_2, parameter_3)
    assert result == expected
