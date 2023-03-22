#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import requests
from source import logging_helper as lh

TOKEN = os.getenv("TB_TOKEN")
CHAT_ID = os.getenv("TB_CHAT_ID")

verified_bot_connection = {"verified": True, "token": False, "chat_id": False}


def send_message(message: str) -> None:
    if not verified_bot_connection["verified"]:
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    requests.get(url).json()


def check_and_verify_bot_connection() -> None:
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    token_check_response = requests.get(url).json()
    if token_check_response["ok"]:
        verified_bot_connection["token"] = True
    url = f"https://api.telegram.org/bot{TOKEN}/getChat?chat_id={CHAT_ID}"
    channel_id_check_response = requests.get(url).json()
    if channel_id_check_response["ok"]:
        verified_bot_connection["chat_id"] = True
    if not all(verified_bot_connection.values()):
        verified_bot_connection["verified"] = False
        message = f"Telegram-Bot could not be started. Check token and chat-id. Status of " \
                  f"TOKEN:{verified_bot_connection['token']} | " \
                  f"CHAT-ID:{verified_bot_connection['chat_id']}"
        lh.write_log(lh.LoggingLevel.ERROR.value, message)
        return


def main() -> None:
    pass


if __name__ == "__main__":
    main()
