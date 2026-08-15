import json
import os
from datetime import datetime, timedelta

import src.data.operators as operators
from src.data.emojis import emoji_list


with open("config.json", "r") as file:
    config = json.load(file)

def logger(msg, log_type="info") -> str:
    status = log_type.upper()
    current_time = datetime.now().strftime('%X')
    print(f"{current_time}: {status}: {msg}")
    if status == "FATAL":
        os._exit(1)

def convert_iso_string(isostring) -> str:
    dt = datetime.fromisoformat(isostring.replace('Z', '+00:00'))
    if dt.second >= 30:
        dt += timedelta(minutes=1)

    return dt.strftime('%H:%M')

def channel_formatting(mode: str) -> str:
    formatting = config.get("formatting", "")

    if config.get("emojis", True):
        emoji = emoji_list.get(mode)
        if emoji is None:
            emoji = emoji_list.get("Fallback")

    return f"{emoji}{formatting}"

def get_train_name(train_name: str, mode: str) -> str:
    if train_name.isdigit():
        train = f"{mode.capitalize()} {train_name}"
    elif "(" in train_name:
        train = train_name.split(" (")[0]
    else:
        train = train_name

    return train

def get_operator_metadata(agency: str, route_color: str) -> dict:
    op_data = operators.OPERATOR_ALIASES.get(agency) or operators.OPERATORS.get(agency) or operators.OPERATORS["fallback"]

    logo = op_data.get("logo", operators.OPERATORS["fallback"]["logo"])
    slogans = op_data.get("slogans")

    color = op_data.get("color")
    if color is None:
        if route_color is not None:
            try:
                color = int(f"0x{route_color.upper()}")
            except ValueError:
                color = operators.OPERATORS["fallback"]["color"]
        else:
            color = operators.OPERATORS["fallback"]["colors"]

    return {
        "logo": logo,
        "color": color,
        "slogans": slogans
    }