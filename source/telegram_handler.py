#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
All functions to operate the features for the telegram bot.
"""
import os
import requests
from source import logging_helper as lh

TOKEN = os.getenv("TB_TOKEN")
CHAT_ID = os.getenv("TB_CHAT_ID")

verified_bot_connection = {"verified": True, "token": False, "chat_id": False, "last_received_message": 33}


def poll_messages() -> None:
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    results = requests.get(url).json()
    messages = [result["message"]["text"] for result in results["result"] if result["message"]["message_id"] > verified_bot_connection["last_received_message"]]
    messages_id = [result["message"]["message_id"] for result in results["result"] if result["message"]["message_id"] > verified_bot_connection["last_received_message"]]
    for message in messages:
        # leerzeichen am Ende abschneiden
        if message.lower() == "!status":
            print("Ja ich bin am Leben, danke der Nachfrage")
    if len(messages_id) <= 0: return
    verified_bot_connection["last_received_message"] = max(messages_id)


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
    """
    Scheduling function for regular call.
    :return: None
    """
    poll_messages()

if __name__ == "__main__":
    main()
