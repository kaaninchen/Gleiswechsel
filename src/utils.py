import os
import importlib
import random
from pathlib import Path
from datetime import datetime, timedelta, timezone
from src.config import config
from zoneinfo import ZoneInfo

import src.data.operators as operators
from src.data.emojis import emoji_list

_operator_mtime = None
LOCAL_TZ = ZoneInfo(config.connections.timezone)

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

def validate_connection(start_time: str, end_time: str, departure_time_iso: str) -> bool:
    now = datetime.now(timezone.utc)
    start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))

    end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
    if end_dt < now:
        logger(f"Connection is from the past: {start_dt}", "error")
        return False

    max_wait_time = config.connections.max_wait_time
    if start_dt > now + timedelta(hours=max_wait_time):
        logger(f"Connection is way too far in the future: {start_dt} (max_wait_time: {max_wait_time}h)", "error")
        return False

    departure_time_iso_dt = datetime.fromisoformat(departure_time_iso.replace("Z", "+00:00"))
    trip_duration = (end_dt - departure_time_iso_dt).total_seconds()
    trip_duration_minutes = str(timedelta(seconds=trip_duration))

    min_duration = config.connections.min_duration
    min_duration_seconds = min_duration * 60
    if trip_duration < min_duration_seconds:
        logger(f"Connection is with {trip_duration_minutes} minutes too short (configured to {min_duration} minutes or more)", "error")
        return False

    max_duration = config.connections.max_duration
    if max_duration:
        max_duration_seconds = max_duration * 60
        if max_duration_seconds < trip_duration:
            logger(f"Connection is with {trip_duration_minutes} too long (configured to {max_duration} minutes at most)", "error")
            return False
        
    return True

def parse_iso(iso_str: str) -> datetime:
    dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    return dt.astimezone(LOCAL_TZ)

def channel_formatting(mode: str) -> str:
    formatting = config.discord.formatting
    emoji = ""

    if config.discord.emojis:
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

def get_operator_metadata(agency: str, route_color: str, mode: str) -> dict:
    _reload_operators_if_changed()

    op_data = operators.OPERATOR_ALIASES.get(agency) or operators.OPERATORS.get(agency) or operators.OPERATORS["fallback"]

    logo = op_data.get("logo", operators.OPERATORS["fallback"]["logo"])
    slogans = op_data.get("slogan")

    color = op_data.get("color")
    if color is None or color == operators.OPERATORS["fallback"]["color"]:
        if route_color is not None:
            try:
                color = int(route_color, 16)
            except ValueError:
                color = operators.OPERATORS["fallback"]["color"]
        else:
            color = operators.OPERATORS["fallback"]["color"]
    return {
        "logo": logo,
        "color": color,
        "slogans": slogans
    }

def get_sound_path(destination, type_announcement: str) -> str | None:
    if type_announcement == "end_stations":
        voice_stations = config.announcements.voice[0].end_stations
    elif type_announcement == "stops":
        voice_stations = config.announcements.voice[0].stops
    
    if destination in voice_stations:
        announcement_for = destination
    else:
        general_sound_enabled = voice_stations.get("general", "")
        if not general_sound_enabled:
            return None
        announcement_for = "general"
        
    if voice_stations.values() == list:
        sound_file = random.choice(voice_stations.get(announcement_for))
    else:
        sound_file = voice_stations.get(announcement_for)

    sound_path = f"src/data/announcements/{sound_file}"
    if Path(sound_path).is_file() is False:
        logger(f"Couldn't find {sound_path}", "error")
        return None

    return sound_path

def get_next_station(stops: dict, train_from: str) -> dict | None:
    now = datetime.now(LOCAL_TZ)
    for name, info in stops.items():
        arrival_dt = info["arrival"]
        if arrival_dt >= now:
            if name == train_from:
                return None
            else:
                return {
                    "name": name,
                    "arrival": arrival_dt
                 }

    return None

def format_via_list(stops: dict, via_and: str) -> str:
     if len(stops) > 2:
            stations = list(stops.keys())
            trip_from = stations[0]
            trip_to = stations[-1]

            important_stops = sort_stations_by_importance(stops)[:3]
            if trip_from in important_stops:
                important_stops.remove(trip_from)
            if trip_to in important_stops:
                important_stops.remove(trip_to)

            if len(important_stops) > 1:
                via = f"{', '.join(important_stops[:-1])} {via_and} {important_stops[-1]}"
            else:
                via = important_stops[0]
            return via
     return None

def sort_stations_by_importance(stops: dict) -> list:
    sorted_stations_dict = dict(
    sorted(
        [(name, info["importance"]) for name, info in stops.items()],
        key=lambda x: x[1],
        reverse=True)
    )

    sorted_stations = list(sorted_stations_dict.keys())
    return sorted_stations

def format_stop_list(stops: dict, next_stop: str | None) -> list[tuple[str, str]]:
    fields = []
    field_lines, field_length, part = [], 0, 1

    for name, info in stops.items():
        if name == next_stop:
            stop_arrival = info["arrival"]
            line = f"• __{name}__ ({stop_arrival.strftime("%H:%M")} Uhr)"
        else:
            stop_arrival = info["arrival"]
            line = f"• {name} ({stop_arrival.strftime("%H:%M")} Uhr)"

        if field_length + len(line) + 1 > 1024:
            route_page_name = "Route" if part == 1 else "Route (Fortsetzung)"
            fields.append((route_page_name, "\n".join(field_lines)))
            field_lines, field_length, part = [], 0, part + 1

        field_lines.append(line)
        field_length += len(line) + 1

    if field_lines:
        route_page_name = "Route" if part == 1 else "Route (Fortsetzung)"
        fields.append((route_page_name, "\n".join(field_lines)))

    return fields
