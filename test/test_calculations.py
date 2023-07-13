"""
Tests for cost_calculation.py
"""
import json
from datetime import datetime
import unittest
from unittest.mock import patch, mock_open

import pytest
from source.calculations import (
    last_day_of_month,
    check_month_parameter,
    check_day_parameter,
    check_matched_day,
    check_matched_day_and_month,
    check_cost_calc_request_time,
    config_request_time,
    check_cost_config,
)
from source.constants import CONFIGURATION_FILE_PATH


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


class TestCheckCostCalcRequestTime(unittest.TestCase):
    """
    Unit test for function check_cost_calc_request_time()
    """

    def test_check_cost_calc_request_time(self):
        """
        Check if correct config file is open and if the general exist with correct data.
        """
        mocked_config = {
            "general": {
                "calc_request_time_daily": "00:00",
                "calc_request_time_monthly": "01",
                "calc_request_time_yearly": "01.01",
            }
        }
        with patch("builtins.open", mock_open(read_data=json.dumps(mocked_config))):
            check_cost_calc_request_time()
        self.assertEqual(config_request_time["calc_request_time_daily"], "00:00")
        self.assertEqual(config_request_time["calc_request_time_monthly"], "01")
        self.assertEqual(config_request_time["calc_request_time_yearly"], "01.01")

    def test_check_cost_calc_request_time_wrong_config(self):
        """
        Check incorrect daily time or if config is not available.
        """
        mocked_config = {
            "general": {
                "calc_request_time_daily": "00:71",
                "calc_request_time_yearly": "01.01",
            }
        }
        with patch("builtins.open", mock_open(read_data=json.dumps(mocked_config))):
            check_cost_calc_request_time()
        self.assertEqual(config_request_time["calc_request_time_daily"], "00:00")
        self.assertEqual(config_request_time["calc_request_time_monthly"], "01")
        self.assertEqual(config_request_time["calc_request_time_yearly"], "01.01")

    def test_check_cost_calc_request_time_no_general(self):
        """
        Check if function act correct if setting for general is not available.a
        """
        mocked_config = {"not_general": {"start_time": "2023-03-17 10:00:00"}}
        with patch("builtins.open", mock_open(read_data=json.dumps(mocked_config))):
            check_cost_calc_request_time()
        self.assertIsNone(config_request_time.get("start_time"))


class TestCheckCostConfig(unittest.TestCase):
    """
    Unit test for function check_cost_config()
    """

    def test_check_cost_config(self):
        """
        Test if key value of price have the correct format and type. Also test if
        value is correct rounded.
        """
        mock_file_contents = '{"general": {"price_kwh": "0,1234"}}'
        mock = mock_open(read_data=mock_file_contents)

        with patch("builtins.open", mock):
            result = check_cost_config()

            mock.assert_called_once_with(CONFIGURATION_FILE_PATH, encoding="utf-8")
            self.assertEqual(result, 0.123)

    def test_check_cost_config_default(self):
        """
        Test default value in case of no configuration
        """
        mock_file_contents = '{"general": {"wrong_config": "hello"}}'

        with patch("builtins.open", mock_open(read_data=mock_file_contents)):
            result = check_cost_config()
            self.assertEqual(result, 0.3)

    def test_check_cost_config_default_no_value(self):
        """
        Test default value in case of no configuration
        """
        mock_file_contents = '{"general": {"price_kwh": true}}'

        with patch("builtins.open", mock_open(read_data=mock_file_contents)):
            result = check_cost_config()
            self.assertEqual(result, 0.3)
