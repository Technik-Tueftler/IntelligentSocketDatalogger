import os
import unittest
from unittest.mock import patch, MagicMock
from source.telegram_handler import verified_bot_connection, check_and_verify_bot_connection
from source.logging_helper import write_log

class TestCheckAndVerifyBotConnection(unittest.TestCase):
    @patch('requests.get')
    def test_check_and_verify_bot_connection_success(self, mock_get):
        mock_get.return_value.json.side_effect = [
            {'ok': True},
            {'ok': True}
        ]

        check_and_verify_bot_connection()

        self.assertEqual(verified_bot_connection, {'verified': True, 'token': True, 'chat_id': True})

    @patch('requests.get')
    def test_check_and_verify_bot_connection_failure(self, mock_get):
        mock_get.return_value.json.side_effect = [
            {'ok': False},
            {'ok': True}
        ]

        check_and_verify_bot_connection()

        expected_log = "Telegram-Bot could not be started. Check token and chat-id. Status of TOKEN:False | CHAT-ID:True"
        #self.assertEqual(write_log.call_args[0][1], expected_log)
        self.assertEqual(verified_bot_connection, {'verified': False, 'token': False, 'chat_id': True})
