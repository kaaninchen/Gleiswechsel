import json
import os
import importlib
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import src.data.operators as operators
from src.data.emojis import emoji_list

_operator_mtime = None

with open("config.json", "r") as file:
    config = json.load(file)

def logger(msg, log_type="info") -> str:
    status = log_type.upper()
    current_time = datetime.now().strftime('%X')
    print(f"{current_time}: {status}: {msg}")
    if status == "FATAL":
        os._exit(1)

def choose_connection() -> dict | None:
    from src.api import transitous
    station_id = transitous.get_random_stop_id()
    connection = transitous.get_random_connection(station_id)
    trip = transitous.get_trip_details(connection)

    return trip

def validate_connection(start_time: str, end_time: str) -> bool:
    now = datetime.now(timezone.utc)
    start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
    end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
    max_wait_time = config.get("max_wait_time", 6)
    
    if end_dt < now:
        logger(f"Verbindung liegt bereits in der Vergangenheit: {start_dt}", "error")
        return False

    if start_dt > now + timedelta(hours=max_wait_time):
        logger(f"Verbindung liegt zu weit in der Zukunft: {start_dt}", "error")
        return False
    
    return True

def convert_iso_string(isostring) -> str:
    timezone = config.get("timezone", "Europe/Berlin")
    dt = datetime.fromisoformat(isostring.replace('Z', '+00:00'))
    dt = dt.astimezone(ZoneInfo(timezone))

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

def _reload_operators_if_changed():
    global _operator_mtime

    path = operators.__file__
    current_mtime = os.path.getmtime(path)

    if _operator_mtime is None:
        _operator_mtime = current_mtime
        return

    if current_mtime != _operator_mtime:
        importlib.reload(operators)
        _operator_mtime = current_mtime
        logger("operators.py wurde automatisch neu geladen (Änderungen erkannt)")


def get_operator_metadata(agency: str, route_color: str) -> dict:
    _reload_operators_if_changed()

    op_data = operators.OPERATOR_ALIASES.get(agency) or operators.OPERATORS.get(agency) or operators.OPERATORS["fallback"]

    logo = op_data.get("logo", operators.OPERATORS["fallback"]["logo"])
    slogans = op_data.get("slogan")

    color = op_data.get("color")
    if color is None or color == 0xFFFFFF:
        if route_color is not None:
            try:
                color = int(route_color, 16)
                print(color)
            except ValueError:
                color = operators.OPERATORS["fallback"]["color"]
            else:
                logger(f"Managed to get color from API, edit src/data/operators.py if you don't like it")
        else:
            color = operators.OPERATORS["fallback"]["color"]
    return {
        "logo": logo,
        "color": color,
        "slogans": slogans
    }