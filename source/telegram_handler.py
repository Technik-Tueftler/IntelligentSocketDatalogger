#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
All functions to operate the features for the telegram bot.
"""
import os
import json
import requests
from source import logging_helper as lh
from source import communication as com
from source.constants import CONFIGURATION_FILE_PATH, CHAT_ID_FILE_PATH


TOKEN = os.getenv("TB_TOKEN", "")
CHAT_ID = os.getenv("TB_CHAT_ID", "")

verified_bot_connection = {
    "verified": True,
    "token": False,
    "token_value": TOKEN,
    "chat_id": False,
    "chat_id_value": CHAT_ID,
    "last_received_message": 0,
    "bot_update_time": 10,
    "bot_request_handle_time": 5,
}


def start(chat_id: str) -> None:
    """
    Function to handle the <start> command from user via telegram bot.
    :param chat_id: chat id as string
    :return: None
    """
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
            with open(CHAT_ID_FILE_PATH, "w", encoding="utf-8") as file:
                file.write(str(chat_id))
        elif data["telegrambot"]["chat_id_source"] == "manuel":
            verified_bot_connection["chat_id_value"] = chat_id
            verified_bot_connection["chat_id"] = True


def pull_messages() -> None:
    """
    This function fetches the last messages and filter which ones have already checked.
    In the last step it handles the commands which was sent by user and add them to the Queue.
    :return:
    """
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


def handle_communication() -> None:
    """
    Check all the items in main to bot queue and handle the output to the user or further actions.
    :return: None
    """
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
    last_message = (
        token_check_response["result"][-1]["message"]["message_id"]
        if token_check_response["result"]
        else 0
    )
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
        verified_bot_connection["verified"] = False
        return
    if "update_time" not in data["telegrambot"]:
        message = "Configuration for Telegram-Bot is missing in config.json."
        lh.write_log(lh.LoggingLevel.ERROR.value, message)
        verified_bot_connection["verified"] = False
        return
    try:
        update_time_value = int(data["telegrambot"]["update_time"])
        if update_time_value >= 2:
            verified_bot_connection["bot_update_time"] = update_time_value
            verified_bot_connection["bot_request_handle_time"] = update_time_value // 2
        else:
            verified_bot_connection["bot_update_time"] = 1
            verified_bot_connection["bot_request_handle_time"] = 1
    except (TypeError, ValueError) as _:
        message = (
            "Not valid value for Telegram-Bot update time. Default value (10s) is used."
        )
        lh.write_log(lh.LoggingLevel.ERROR.value, message)


def schedule_bot() -> None:
    """
    Schedule which functions should be called regular to ensure the communication
    between bot and main app.
    :return: None
    """
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
