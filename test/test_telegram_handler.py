"""
Tests for telegram_handler.py
"""
import unittest
from unittest.mock import patch, mock_open
from source.telegram_handler import (
    verified_bot_connection,
    check_and_verify_token,
    check_and_verify_chat_id
)


class TestCheckAndVerifyToken(unittest.TestCase):
    """
    Unit test for function check_and_verify_token()
    """
    @patch('requests.get')
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

    @patch('requests.get')
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
        self.mock_chat_id_value = ""

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='12345')
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
        self.assertEqual('12345', verified_bot_connection["chat_id_value"])
        self.assertTrue(verified_bot_connection["chat_id"])

    @patch('os.path.exists')
    def test_missing_chat_id_file(self, mock_exists):
        """
        The function checks if the flag for the chat_id is set to False
        and an empty string for the value of the chat_id if the chat ID
        file does not exist.
        :param mock_exists: mock for os.path.exists
        :return: None
        """
        verified_bot_connection = {"chat_id_value": self.mock_chat_id_value, "chat_id": False}
        mock_exists.return_value = False
        check_and_verify_chat_id()
        self.assertFalse(verified_bot_connection["chat_id"])
        self.assertEqual("", verified_bot_connection["chat_id_value"])

    @patch('os.path.exists')
    @patch('source.telegram_handler.CHAT_ID', '54321')
    def test_existing_chat_id(self, mock_exists):
        """
        The function checks the value of the global variable CHAT_ID
        if the chat ID file does not exist and sets the value.
        :param mock_exists: mock for os.path.exists
        :return: None
        """
        mock_exists.return_value = False
        check_and_verify_chat_id()
        self.assertEqual('54321', verified_bot_connection["chat_id_value"])
        self.assertTrue(verified_bot_connection["chat_id"])

    @patch('os.path.exists')
    @patch('source.telegram_handler.CHAT_ID', '')
    def test_missing_chat_id(self, mock_exists):
        """
        The function checks the value of the global variable CHAT_ID
        if the chat ID file does not exist and sets the default value.
        :param mock_exists: mock for os.path.exists
        :return: None
        """
        # verified_bot_connection["chat_id"] <- Steht hier noch True vom letzten Test drin?
        verified_bot_connection = {"chat_id_value": self.mock_chat_id_value, "chat_id": False}
        mock_exists.return_value = False
        check_and_verify_chat_id()
        self.assertEqual('', verified_bot_connection["chat_id_value"])
        self.assertFalse(verified_bot_connection["chat_id"])


if __name__ == '__main__':
    unittest.main()
