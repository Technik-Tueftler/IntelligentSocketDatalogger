#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
All functions to operate the features for the telegram bot.
"""
import os
import json
import re
import copy
from collections import namedtuple
import requests
from source import logging_helper as lh
from source import communication as com
from source.constants import (
    CONFIGURATION_FILE_PATH,
    CHAT_ID_FILE_PATH,
    TIMEOUT_RESPONSE_TIME,
    DEFAULT_INLINE_KEYS_COLUMNS,
    DEFAULT_BOT_UPDATE_TIME,
    DEFAULT_BOT_REQUEST_HANDLE_TIME,
    USER_MESSAGE_INLINE_KEYBOARD_DEVICE,
    NUM_IS_INT_OR_FLOAT_MATCH,
)

TOKEN = os.getenv("TB_TOKEN", "")
CHAT_ID = os.getenv("TB_CHAT_ID", "")

Message = namedtuple("Message", ["chat_id", "message_id", "text"])
Callback = namedtuple("Callback", ["message_id", "action", "value"])

telegrambot_watcher = lh.WatchHen(device_name="Telegram-Bot")

open_requests = {"value_setalarmthr": None}

verified_bot_connection = {
    "verified": True,
    "token": False,
    "token_value": TOKEN,
    "chat_id": False,
    "chat_id_value": CHAT_ID,
    "last_received_message": 0,
    "bot_update_time": DEFAULT_BOT_UPDATE_TIME,
    "bot_request_handle_time": DEFAULT_BOT_REQUEST_HANDLE_TIME,
    "inline_keys_columns": DEFAULT_INLINE_KEYS_COLUMNS,
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
            with open(CHAT_ID_FILE_PATH, "w", encoding="utf-8") as file:
                file.write(str(chat_id))
    verified_bot_connection["chat_id_value"] = chat_id
    verified_bot_connection["chat_id"] = True
    send_message("Bot is successfully set up.")


def send_inline_keyboard_for_set_alarm(command, devices: list) -> None:
    """
    Function to create and send the inline keyboard to show all devices
    based on the adjustable display settings.
    :param command: Requested command from user
    :param devices: All configured devices for energy monitor from class Device
    :return:
    """
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    inline_keyboard = []
    while devices:
        temp_list = []
        for _ in range(verified_bot_connection["inline_keys_columns"]):
            if not devices:
                break
            device = devices.pop()
            temp_dict = {
                "text": device.name,
                "callback_data": json.dumps({"action": command, "device": device.name}),
            }
            temp_list.append(temp_dict)
        inline_keyboard.append(temp_list)

    user_message = USER_MESSAGE_INLINE_KEYBOARD_DEVICE
    payload = {
        "chat_id": CHAT_ID,
        "text": user_message,
        "reply_markup": {"inline_keyboard": inline_keyboard},
    }
    try:
        _ = requests.post(url, json=payload, timeout=TIMEOUT_RESPONSE_TIME)

    except requests.exceptions.ConnectTimeout as err:
        telegrambot_watcher.failure_processing(
            type(err).__name__,
            err,
            "- Connection to telegram api timed out during send inline.",
        )


def handle_message_input(message: Message) -> None:
    """
    Handle the message from type Message and call further actions.
    :param message: Message from user input.
    :return: None
    """
    cleaned_message = message.text.lower().strip().replace("/", "")
    if cleaned_message == "start":
        start(message.chat_id)
    elif cleaned_message == "status":
        com.to_main.put(com.Request("status"))
    elif cleaned_message == "runningdevices":
        return_string = "\n".join(com.shared_information["started_devices"])
        send_message(return_string)
    elif cleaned_message == "observeddevices":
        named_observed_devices = [
            device.name for device in com.shared_information["observed_devices"]
        ]
        return_string = "\n".join(named_observed_devices)
        send_message(return_string)
    elif cleaned_message in ("setalarmref", "setalarmthr", "energydevice"):
        copy_observed_devices = copy.deepcopy(
            com.shared_information["observed_devices"]
        )
        send_inline_keyboard_for_set_alarm(cleaned_message, copy_observed_devices)
    else:
        if open_requests["value_setalarmthr"] is not None:
            match = re.search(NUM_IS_INT_OR_FLOAT_MATCH, cleaned_message)
            device = open_requests["value_setalarmthr"]
            if match is None:
                user_message = (
                    f"Invalid Number format to set threshold of device "
                    f"{device} to. You will have to run /setalarmthr again "
                    f"to retry."
                )
                send_message(user_message)
                open_requests["value_setalarmthr"] = None
            else:
                com.to_energy_mon.put(
                    com.Request(
                        command="setalarmthr",
                        data={"device": device, "threshold": match.group()},
                    )
                )
                open_requests["value_setalarmthr"] = None


def handle_callback_input(callback: Callback) -> None:
    """
    Handle the message from type callback and call further actions.
    :param callback: Callback from user input.
    :return: None
    """
    if callback.action in ("setalarmref", "energydevice"):
        com.to_energy_mon.put(
            com.Request(
                command=callback.action,
                data={"device": callback.value["device"]},
            )
        )
    elif callback.action == "setalarmthr":
        device = callback.value["device"]
        open_requests["value_setalarmthr"] = device
        user_message = (
            f"Write the threshold for device {device} " f"as an float (e.g. 50.0)"
        )
        send_message(user_message)


def pull_messages() -> None:  # [too-many-branches]
    """
    This function handles the messages and schedule the next
    steps based on the input.
    """
    messages = get_updates()
    if len(messages) <= 0:
        return
    for message in messages:
        if isinstance(message, Message):
            handle_message_input(message)

        elif isinstance(message, Callback):
            handle_callback_input(message)

        if message.message_id > verified_bot_connection["last_received_message"]:
            verified_bot_connection["last_received_message"] = message.message_id


def handle_communication() -> None:
    """
    Check all the items in main to bot queue and handle the output to the user or further actions.
    :return: None
    """
    while not com.to_bot.empty():
        req = com.to_bot.get()
        match req.command:
            case "status" | "devices":
                send_message(req.data["output_text"])
            case "setalarmref" | "setalarmthr":
                send_inline_keyboard_for_set_alarm(req.command, req.data["device_list"])
            case "alarm_message":
                message = (
                    f"The energy consumption of {req.data['device_name']} is unusually high. "
                    f"Please check if the device works correctly."
                )
                send_message(message)


def send_message(message: str) -> None:
    """
    Function send a message from bot to the chat.
    :param message: Transmitted message which is to be written by the bot to the chat
    :return: None
    """
    try:
        if not verified_bot_connection["verified"]:
            return
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
        requests.get(url, timeout=TIMEOUT_RESPONSE_TIME).json()

    except requests.exceptions.ConnectTimeout as err:
        telegrambot_watcher.failure_processing(
            type(err).__name__,
            err,
            "- Connection to telegram api timed out during send message.",
        )


def check_exist_last_message(get_update_response: dict) -> int:
    """

    :param get_update_response: Data from api with all messages from last 24h
    :return: id if the last message
    """
    if len(get_update_response["result"]) < 1:
        return 0
    if "message" in get_update_response["result"][-1]:
        last_message_id = (
            get_update_response["result"][-1]["message"]["message_id"]
            if get_update_response["result"]
            else 0
        )
    else:
        last_message_id = (
            get_update_response["result"][-1]["callback_query"]["message"]["message_id"]
            if get_update_response["result"]
            else 0
        )
    return last_message_id


def check_and_verify_token() -> None:
    """
    Function checks Bot Token and verify connection to chat
    :return: None
    """
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
        token_check_response = requests.get(url, timeout=TIMEOUT_RESPONSE_TIME).json()
        if token_check_response["ok"]:
            verified_bot_connection["token"] = True
            verified_bot_connection["last_received_message"] = check_exist_last_message(
                token_check_response
            )
        else:
            raise ValueError("Telegram-Bot could not be started. Check Bot-Token.")
    except ValueError as err:
        verified_bot_connection["verified"] = False
        lh.write_log(lh.LoggingLevel.ERROR.value, err)
    except requests.exceptions.ConnectTimeout as err:
        telegrambot_watcher.failure_processing(
            type(err).__name__,
            err,
            "- Connection to telegram api timed out during verification.",
        )


def check_and_verify_chat_id() -> None:
    """
    Function checks all possible inputs for chat ID and verify.
    :return: None
    """
    if os.path.exists(CHAT_ID_FILE_PATH):
        with open(CHAT_ID_FILE_PATH, "r", encoding="utf-8") as datei:
            chat_id = datei.read()
        if chat_id:
            verified_bot_connection["chat_id_value"] = chat_id
            verified_bot_connection["chat_id"] = True

    if not verified_bot_connection["chat_id"]:
        if not CHAT_ID:
            message = (
                "It's currently not possible for the bot to write messages "
                "because the CHAT_ID is still missing. Use the start command in the chat "
                "or add the CHAT_ID to the env variables."
            )
            lh.write_log(lh.LoggingLevel.ERROR.value, message)
        else:
            verified_bot_connection["chat_id_value"] = CHAT_ID
            verified_bot_connection["chat_id"] = True


def check_and_verify_bot_config() -> None:
    """
    Checks and plausible the bot configuration with user inputs. If something is
    wrong default values are taken.
    :return: None
    """
    with open(CONFIGURATION_FILE_PATH, encoding="utf-8") as file:
        data = json.load(file)
    if "telegrambot" not in data:
        message = (
            "Configuration for Telegram-Bot is missing in config.json, the default values "
            "are now adopted"
        )
        lh.write_log(lh.LoggingLevel.ERROR.value, message)
        return
    if "update_time" not in data["telegrambot"]:
        message = (
            f"The update time for Telegram-Bot is missing in config.json. The default "
            f"value of {DEFAULT_BOT_UPDATE_TIME} is assumed."
        )
        lh.write_log(lh.LoggingLevel.ERROR.value, message)
        return
    try:
        update_time_value = int(data["telegrambot"]["update_time"])
        if update_time_value >= 2:
            verified_bot_connection["bot_update_time"] = update_time_value
            verified_bot_connection["bot_request_handle_time"] = update_time_value // 2
        else:
            message = (
                f"Too small value for Telegram-Bot update time. Default value "
                f"{DEFAULT_BOT_UPDATE_TIME}s is used."
            )
            lh.write_log(lh.LoggingLevel.ERROR.value, message)
    except (TypeError, ValueError) as _:
        message = (
            f"Not valid value for Telegram-Bot update time. Default value "
            f"{DEFAULT_BOT_UPDATE_TIME}s is used."
        )
        lh.write_log(lh.LoggingLevel.ERROR.value, message)

    if "inline_keys_columns" in data["telegrambot"]:
        value_inline_keys_columns = data["telegrambot"]["inline_keys_columns"]
        if isinstance(value_inline_keys_columns, int):
            verified_bot_connection["inline_keys_columns"] = value_inline_keys_columns


def check_and_verify_bot_connection() -> None:
    """
    Function controls the passed env variables and checks if a connection
    to the chat can be established
    :return:
    """

    check_and_verify_token()
    if not verified_bot_connection["verified"]:
        return
    check_and_verify_chat_id()


def get_updates() -> list:
    """
    This function fetches the last messages and filter which ones
    have already checked. In the last step, it is split into messages
    from the user or into callbacks from inline forms.
    :return: List with all not handled messages.
    """
    try:
        messages = []
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
        update = requests.get(url, timeout=TIMEOUT_RESPONSE_TIME).json()
        for result in update["result"]:
            if "message" in result:
                if (
                    result["message"]["message_id"]
                    > verified_bot_connection["last_received_message"]
                ):
                    messages.append(
                        Message(
                            chat_id=result["message"]["chat"]["id"],
                            message_id=result["message"]["message_id"],
                            text=result["message"]["text"],
                        )
                    )
            elif "callback_query" in result:
                if (
                    result["callback_query"]["message"]["message_id"]
                    > verified_bot_connection["last_received_message"]
                ):
                    messages.append(
                        Callback(
                            message_id=result["callback_query"]["message"][
                                "message_id"
                            ],
                            action=json.loads(result["callback_query"]["data"])[
                                "action"
                            ],
                            value=json.loads(result["callback_query"]["data"]),
                        )
                    )
        return messages
    except requests.exceptions.ConnectTimeout as err:
        telegrambot_watcher.failure_processing(
            type(err).__name__,
            err,
            "- Connection to telegram api timed out during update.",
        )
        return messages
    except requests.exceptions.ConnectionError as err:
        telegrambot_watcher.failure_processing(
            type(err).__name__,
            err,
            "- Connection to telegram api generates an error.",
        )
        return messages
    except KeyError as err:
        telegrambot_watcher.failure_processing(
            type(err).__name__,
            err,
            f"- Key Error during get_updates with error: {err}",
        )
        return messages
    except requests.exceptions.ReadTimeout as err:
        telegrambot_watcher.failure_processing(
            type(err).__name__,
            err,
            "- An error has occurred when reading via the telegram API.",
        )
        return messages


def set_commands() -> None:
    """
    Set all commands for the Telegram Bot so that the user has easier access
    to the commands.
    :return: None
    """
    url = f"https://api.telegram.org/bot{TOKEN}/setMyCommands"
    commands = [
        {"command": "/start", "description": "Initialization off the app"},
        {"command": "/status", "description": "Get current status of ISDL"},
        {"command": "/runningdevices", "description": "Get all running devices"},
        {"command": "/observeddevices", "description": "Get all observed devices"},
        {"command": "/setalarmthr", "description": "Set threshold for power alarm"},
        {
            "command": "/setalarmref",
            "description": "Set reference value of energy from last period",
        },
        {
            "command": "/energydevice",
            "description": "Get energy of device from last period",
        },
    ]

    payload = {"commands": commands}
    try:
        _ = requests.post(url, timeout=TIMEOUT_RESPONSE_TIME, json=payload)

    except requests.exceptions.ConnectTimeout as err:
        telegrambot_watcher.failure_processing(
            type(err).__name__,
            err,
            "- Connection to telegram api timed out during send commands.",
        )
    # if response.status_code == 200:
    # if response.status_code == 200:
    #     print("Commands set successfully.")
    # else:
    #     print("Error setting commands: ", response.text)


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
    # check_and_verify_bot_connection()
    # poll_messages()
    # send_message("geht doch")
    # get_updates()
    set_commands()


if __name__ == "__main__":
    main()
