"""
Tests for telegram_handler.py
"""
import unittest
from unittest.mock import patch, mock_open
from source.logging_helper import LoggingLevel
from source.constants import CONFIGURATION_FILE_PATH, CHAT_ID_FILE_PATH
from source.telegram_handler import (
    verified_bot_connection,
    check_and_verify_token,
    check_and_verify_chat_id,
    check_and_verify_bot_config,
    start
)
from source.constants import (
    DEFAULT_BOT_UPDATE_TIME,
    DEFAULT_BOT_REQUEST_HANDLE_TIME,
    DEFAULT_INLINE_KEYS_COLUMNS,
)


class TestStart(unittest.TestCase):
    """
    Unit test for function start()
    """

    def setUp(self):
        verified_bot_connection["chat_id_value"] = ""
        verified_bot_connection["chat_id"] = False

    @patch("builtins.open")
    @patch("json.load")
    @patch("source.logging_helper.write_log")
    def test_no_configuration(self, mock_helper_write_log, mock_load, mock_file_open):
        """
        Test correct behaviour if the configuration is wrong or not available.
        """
        mock_load.return_value = {"not_telegrambot": {"chat_id_source": "auto"}}
        mock_file = mock_file_open()
        mock_file_open.return_value.__enter__.return_value = mock_file

        start(1234)

        # Asserting that the open function was called with the expected arguments from config
        mock_file_open.assert_any_call(CONFIGURATION_FILE_PATH, encoding="utf-8")
        mock_helper_write_log.assert_called_once_with(
            LoggingLevel.ERROR.value,
            "Configuration for Telegram-Bot is missing in config.json.",
        )
        self.assertEqual("", verified_bot_connection["chat_id_value"])
        self.assertFalse(verified_bot_connection["chat_id"])

    @patch("builtins.open")
    @patch("json.load")
    def test_auto_configuration(self, mock_json_load, mock_file_open):
        """
        Test if file will be created in configuration "auto" is active for chat_id
        """
        chat_id = "123456"
        mock_data = {"telegrambot": {"chat_id_source": "auto"}}
        mock_json_load.return_value = mock_data

        mock_file = mock_file_open()
        mock_file_open.return_value.__enter__.return_value = mock_file

        start(chat_id)

        # Asserting that the open function was called with the expected arguments from config
        mock_file_open.assert_any_call(CONFIGURATION_FILE_PATH, encoding="utf-8")
        # Asserting that json.load was called with the file object returned by open
        mock_json_load.assert_called_once_with(mock_file)
        # Asserting that the open function was called with the expected arguments from config
        mock_file_open.assert_any_call(CHAT_ID_FILE_PATH, "w", encoding="utf-8")
        # Asserting that the write method was called on the file object returned by open
        mock_file.write.assert_called_once_with(str(chat_id))

        self.assertEqual(chat_id, verified_bot_connection["chat_id_value"])
        self.assertTrue(verified_bot_connection["chat_id"])

    @patch("builtins.open")
    @patch("json.load")
    def test_manuel_configuration(self, mock_json_load, mock_file_open):
        """
        Test correct behaviour if the configuration for chat_id is set to manuel
        """
        chat_id = "1234567"
        mock_data = {"telegrambot": {"chat_id_source": "manuel"}}
        mock_json_load.return_value = mock_data

        mock_file = mock_file_open()
        mock_file_open.return_value.__enter__.return_value = mock_file

        start(chat_id)

        self.assertEqual(chat_id, verified_bot_connection["chat_id_value"])
        self.assertTrue(verified_bot_connection["chat_id"])


class TestCheckAndVerifyToken(unittest.TestCase):
    """
    Unit test for function check_and_verify_token()
    """

    @patch("requests.get")
    def test_successful_token_check(self, mock_get):
        """
        This test checks whether the TOKEN read in is correct and the value
        for a successful connection has been entered.
        :param mock_get: Result and return value of the requests.get function
        :return: None
        """
        mock_get.return_value.json.return_value = {"ok": True, "result": []}
        check_and_verify_token()
        self.assertTrue(verified_bot_connection["token"])

    @patch("requests.get")
    def test_failed_token_check(self, mock_get):
        """
        This test checks whether the TOKEN read in is not correct and the value
        for a not successful connection has been entered.
        :param mock_get: Result and return value of the requests.get function
        :return: None
        """
        mock_get.return_value.json.return_value = {"ok": False, "result": []}
        check_and_verify_token()
        self.assertFalse(verified_bot_connection["verified"])


class TestCheckAndVerifyChatID(unittest.TestCase):
    """
    Unit test for function check_and_verify_chat_id()
    """

    def setUp(self):
        verified_bot_connection["chat_id_value"] = ""
        verified_bot_connection["chat_id"] = False

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="12345")
    def test_existing_chat_id_file(self, _, mock_exists):
        """
        The function tests whether the content of an existing chat ID
        file is read correctly and the corresponding values are set in
        verified_bot_connection.
        :param _: placeholder for mock_open
        :param mock_exists: mock for os.path.exists
        :return: None
        """
        mock_exists.return_value = True
        check_and_verify_chat_id()
        self.assertEqual("12345", verified_bot_connection["chat_id_value"])
        self.assertTrue(verified_bot_connection["chat_id"])

    @patch("os.path.exists")
    def test_missing_chat_id_file(self, mock_exists):
        """
        The function checks if the flag for the chat_id is set to False
        and an empty string for the value of the chat_id if the chat ID
        file does not exist.
        :param mock_exists: mock for os.path.exists
        :return: None
        """
        mock_exists.return_value = False
        check_and_verify_chat_id()
        self.assertFalse(verified_bot_connection["chat_id"])
        self.assertEqual("", verified_bot_connection["chat_id_value"])

    @patch("os.path.exists")
    @patch("source.telegram_handler.CHAT_ID", "54321")
    def test_existing_env_chat_id(self, mock_exists):
        """
        The function checks the value of the global variable CHAT_ID
        if the chat ID file does not exist and sets the value.
        :param mock_exists: mock for os.path.exists
        :return: None
        """
        mock_exists.return_value = False
        check_and_verify_chat_id()
        self.assertEqual("54321", verified_bot_connection["chat_id_value"])
        self.assertTrue(verified_bot_connection["chat_id"])

    @patch("os.path.exists")
    @patch("source.telegram_handler.CHAT_ID", "")
    def test_missing_env_chat_id(self, mock_exists):
        """
        The function checks the value of the global variable CHAT_ID
        if the chat ID file does not exist and sets the default value.
        :param mock_exists: mock for os.path.exists
        :return: None
        """
        mock_exists.return_value = False
        check_and_verify_chat_id()
        self.assertEqual("", verified_bot_connection["chat_id_value"])
        self.assertFalse(verified_bot_connection["chat_id"])


class TestCheckAndVerifyBotConfig(unittest.TestCase):
    """
    Unit test for function check_and_verify_bot_config()
    """

    def setUp(self):
        verified_bot_connection["bot_update_time"] = DEFAULT_BOT_UPDATE_TIME
        verified_bot_connection[
            "bot_request_handle_time"
        ] = DEFAULT_BOT_REQUEST_HANDLE_TIME
        verified_bot_connection["inline_keys_columns"] = DEFAULT_INLINE_KEYS_COLUMNS

    @patch("builtins.open")
    @patch("json.load")
    def test_no_telegram_config(self, mock_load, mock_file_open):
        """
        Test if default values are still set if no telegram config is available.
        :param mock_load: Return value with config
        :param mock_file_open: Mock to open file
        :return: None
        """
        _ = mock_file_open.return_value.__enter__.return_value
        mock_load.return_value = {
            "not_telegrambot": {
                "chat_id_source": "auto",
                "update_time": 10,
                "inline_keys_columns": 3,
            }
        }

        check_and_verify_bot_config()

        self.assertEqual(
            DEFAULT_BOT_UPDATE_TIME, verified_bot_connection["bot_update_time"]
        )
        self.assertEqual(
            DEFAULT_BOT_REQUEST_HANDLE_TIME,
            verified_bot_connection["bot_request_handle_time"],
        )
        self.assertEqual(
            DEFAULT_INLINE_KEYS_COLUMNS, verified_bot_connection["inline_keys_columns"]
        )

    @patch("builtins.open")
    @patch("json.load")
    def test_no_update_time_config(self, mock_load, mock_file_open):
        """
        Test if default values are still set if no update_time in config is available.
        :param mock_load: Return value with config
        :param mock_file_open: Mock to open file
        :return:
        """
        _ = mock_file_open.return_value.__enter__.return_value
        mock_load.return_value = {
            "telegrambot": {
                "chat_id_source": "auto",
                "no_update_time": 10,
                "inline_keys_columns": 3,
            }
        }

        check_and_verify_bot_config()

        self.assertEqual(
            DEFAULT_BOT_UPDATE_TIME, verified_bot_connection["bot_update_time"]
        )
        self.assertEqual(
            DEFAULT_BOT_REQUEST_HANDLE_TIME,
            verified_bot_connection["bot_request_handle_time"],
        )
        self.assertEqual(
            DEFAULT_INLINE_KEYS_COLUMNS, verified_bot_connection["inline_keys_columns"]
        )

    @patch("builtins.open")
    @patch("json.load")
    def test_wrong_type_update_time_config(self, mock_load, mock_file_open):
        """
        Test if default values are still set if update_time has the wrong type in config.
        :param mock_load: Return value with config
        :param mock_file_open: Mock to open file
        :return: None
        """
        _ = mock_file_open.return_value.__enter__.return_value
        mock_load.return_value = {
            "telegrambot": {
                "chat_id_source": "auto",
                "update_time": "string",
                "inline_keys_columns": 3,
            }
        }

        check_and_verify_bot_config()

        self.assertEqual(
            DEFAULT_BOT_UPDATE_TIME, verified_bot_connection["bot_update_time"]
        )
        self.assertEqual(
            DEFAULT_BOT_REQUEST_HANDLE_TIME,
            verified_bot_connection["bot_request_handle_time"],
        )
        self.assertEqual(
            DEFAULT_INLINE_KEYS_COLUMNS, verified_bot_connection["inline_keys_columns"]
        )

    @patch("builtins.open")
    @patch("json.load")
    def test_small_num_update_time_config(self, mock_load, mock_file_open):
        """
        Test if default values are still set if update_time is too small to process.
        :param mock_load: Return value with config
        :param mock_file_open: Mock to open file
        :return: None
        """
        _ = mock_file_open.return_value.__enter__.return_value
        mock_load.return_value = {
            "telegrambot": {
                "chat_id_source": "auto",
                "update_time": 1,
                "inline_keys_columns": 3,
            }
        }

        check_and_verify_bot_config()

        self.assertEqual(
            DEFAULT_BOT_UPDATE_TIME, verified_bot_connection["bot_update_time"]
        )
        self.assertEqual(
            DEFAULT_BOT_REQUEST_HANDLE_TIME,
            verified_bot_connection["bot_request_handle_time"],
        )
        self.assertEqual(
            DEFAULT_INLINE_KEYS_COLUMNS, verified_bot_connection["inline_keys_columns"]
        )

    @patch("builtins.open")
    @patch("json.load")
    def test_ok_update_time_config(self, mock_load, mock_file_open):
        """
        Test if config for telegram bot is correct.
        :param mock_load: Return value with config
        :param mock_file_open: Mock to open file
        :return: None
        """
        _ = mock_file_open.return_value.__enter__.return_value
        mock_load.return_value = {
            "telegrambot": {
                "chat_id_source": "auto",
                "update_time": 5,
                "inline_keys_columns": 3,
            }
        }

        check_and_verify_bot_config()

        self.assertEqual(5, verified_bot_connection["bot_update_time"])
        self.assertEqual(2, verified_bot_connection["bot_request_handle_time"])
        self.assertEqual(
            DEFAULT_INLINE_KEYS_COLUMNS, verified_bot_connection["inline_keys_columns"]
        )

    @patch("builtins.open")
    @patch("json.load")
    def test_no_keys_columns_config(self, mock_load, mock_file_open):
        """
        Test if default values are still set if keys_columns config is not available.
        :param mock_load: Return value with config
        :param mock_file_open: Mock to open file
        :return: None
        """
        _ = mock_file_open.return_value.__enter__.return_value
        mock_load.return_value = {
            "telegrambot": {
                "chat_id_source": "auto",
                "update_time": 5,
                "not_inline_keys_columns": 3,
            }
        }

        check_and_verify_bot_config()

        self.assertEqual(5, verified_bot_connection["bot_update_time"])
        self.assertEqual(2, verified_bot_connection["bot_request_handle_time"])
        self.assertEqual(
            DEFAULT_INLINE_KEYS_COLUMNS, verified_bot_connection["inline_keys_columns"]
        )

    @patch("builtins.open")
    @patch("json.load")
    def test_wrong_type_keys_columns_config(self, mock_load, mock_file_open):
        """
        Test if default values are still set if keys_columns config has the wrong type.
        :param mock_load: Return value with config
        :param mock_file_open: Mock to open file
        :return: None
        """
        _ = mock_file_open.return_value.__enter__.return_value
        mock_load.return_value = {
            "telegrambot": {
                "chat_id_source": "auto",
                "update_time": 5,
                "inline_keys_columns": 7.7,
            }
        }

        check_and_verify_bot_config()

        self.assertEqual(5, verified_bot_connection["bot_update_time"])
        self.assertEqual(2, verified_bot_connection["bot_request_handle_time"])
        self.assertEqual(
            DEFAULT_INLINE_KEYS_COLUMNS, verified_bot_connection["inline_keys_columns"]
        )

    @patch("builtins.open")
    @patch("json.load")
    def test_ok_keys_columns_config(self, mock_load, mock_file_open):
        """
        Test if config for keys_columns is correct.
        :param mock_load: Return value with config
        :param mock_file_open: Mock to open file
        :return: None
        """
        _ = mock_file_open.return_value.__enter__.return_value
        mock_load.return_value = {
            "telegrambot": {
                "chat_id_source": "auto",
                "update_time": 5,
                "inline_keys_columns": 7,
            }
        }

        check_and_verify_bot_config()

        self.assertEqual(5, verified_bot_connection["bot_update_time"])
        self.assertEqual(2, verified_bot_connection["bot_request_handle_time"])
        self.assertEqual(7, verified_bot_connection["inline_keys_columns"])


if __name__ == "__main__":
    unittest.main()
