#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
All functions to operate the features for the telegram bot.
"""
import os

import requests
import json
from source import logging_helper as lh
from source import communication as com
from source.constants import CONFIGURATION_FILE_PATH


TOKEN = os.getenv("TB_TOKEN", "")
CHAT_ID = os.getenv("TB_CHAT_ID", "")

verified_bot_connection = {
    "verified": True,
    "token": False,
    "token_value": TOKEN,
    "chat_id": False,
    "chat_id_value": CHAT_ID,
    "last_received_message": 0,
    "bot_update_time": 10
}
# chat_id = token_check_response["result"][0]["message"]["chat"]["id"]
# url = f"https://api.telegram.org/bot{TOKEN}/getChat?chat_id={CHAT_ID}"
# channel_id_check_response = requests.get(url).json()


def start(chat_id: str) -> None:
    with open(CONFIGURATION_FILE_PATH, encoding="utf-8") as file:
        data = json.load(file)
    if "telegrambot" not in data:
        message = "Configuration for Telegram-Bot is missing in config.json."
        lh.write_log(lh.LoggingLevel.ERROR.value, message)
        return
    if "chat_id_source" in data["telegrambot"]:
        if data["telegrambot"]["chat_id_source"] == "auto":
            data["telegrambot"]["chat_id"] = chat_id
            verified_bot_connection["chat_id"] = True
            # ToDo: Speichern der Chat-ID in separates Textfile
            # with open(CONFIGURATION_FILE_PATH, "w", encoding="utf-8") as file:
            #     json.dump(CONFIGURATION_FILE_PATH, file)
        elif data["telegrambot"]["chat_id_source"] == "manuel":
            verified_bot_connection["chat_id_value"] = chat_id
            verified_bot_connection["chat_id"] = True


def pull_messages() -> None:
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    results = requests.get(url).json()
    messages = [
        result["message"]["text"]
        for result in results["result"]
        if result["message"]["message_id"]
        > verified_bot_connection["last_received_message"]
    ]
    messages_id = [
        result["message"]["message_id"]
        for result in results["result"]
        if result["message"]["message_id"]
        > verified_bot_connection["last_received_message"]
    ]
    for message in messages:
        if message.lower().strip() == "/start":
            chat_id = results["result"][0]["message"]["chat"]["id"]
            start(chat_id)
        elif message.lower().strip() == "/status":
            com.bot_to_main.put(com.Request("status"))
    if len(messages_id) <= 0:
        return
    verified_bot_connection["last_received_message"] = max(messages_id)


def handle_communication():
    while not com.main_to_bot.empty():
        req = com.main_to_bot.get()
        if req.command == "status":
            send_message(req.response)


def send_message(message: str) -> None:
    """
    Function send a message from bot to the chat.
    :param message: Transmitted message which is to be written by the bot to the chat
    :return: None
    """
    if not verified_bot_connection["verified"]:
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    requests.get(url).json()


def check_and_verify_bot_connection() -> None:
    """
    Function controls the passed env variables and checks if a connection
    to the chat can be established
    :return:
    """
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    token_check_response = requests.get(url).json()
    last_message = token_check_response["result"][-1]["message"]["message_id"] if token_check_response["result"] else 0
    verified_bot_connection["last_received_message"] = last_message
    if token_check_response["ok"]:
        verified_bot_connection["token"] = True
    else:
        verified_bot_connection["verified"] = False
        message = "Telegram-Bot could not be started. Check Bot-Token."
        lh.write_log(lh.LoggingLevel.ERROR.value, message)
    with open(CONFIGURATION_FILE_PATH, encoding="utf-8") as file:
        data = json.load(file)
    if "telegrambot" not in data:
        message = "Configuration for Telegram-Bot is missing in config.json."
        lh.write_log(lh.LoggingLevel.ERROR.value, message)
        return
    if "update_time" not in data["telegrambot"]:
        message = "Configuration for Telegram-Bot is missing in config.json."
        lh.write_log(lh.LoggingLevel.ERROR.value, message)
        return
    try:
        verified_bot_connection["bot_update_time"] = int(data["telegrambot"]["update_time"])
    except (TypeError, ValueError) as _:
        message = "Not valid value for Telegram-Bot update time. Default value (10s) is used."
        lh.write_log(lh.LoggingLevel.ERROR.value, message)


def schedule_bot():
    pull_messages()
    handle_communication()


def main() -> None:
    """
    Scheduling function for regular call.
    :return: None
    """
    # pull_messages()
    check_and_verify_bot_connection()
    # poll_messages()
    # send_message("geht doch")


if __name__ == "__main__":
    main()
