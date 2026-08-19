import os
import importlib
from pathlib import Path
from datetime import datetime, timedelta, timezone
import staticmaps
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
    if max_wait_time:
        if start_dt > now + timedelta(hours=max_wait_time):
            logger(f"Connection is way too far in the future: {start_dt} (max_wait_time: {max_wait_time}h), retrying...", "error")
            return False

    departure_time_iso_dt = datetime.fromisoformat(departure_time_iso.replace("Z", "+00:00"))
    trip_duration = (end_dt - departure_time_iso_dt).total_seconds()
    trip_duration_minutes = str(timedelta(seconds=trip_duration))

    min_duration = config.connections.min_duration
    min_duration_seconds = min_duration * 60
    if trip_duration < min_duration_seconds:
        logger(f"Connection is with {trip_duration_minutes} minutes too short (configured to {min_duration} minutes or more), retrying...", "error")
        return False

    max_duration = config.connections.max_duration
    if max_duration:
        max_duration_seconds = max_duration * 60
        if max_duration_seconds < trip_duration:
            logger(f"Connection is with {trip_duration_minutes} too long (configured to {max_duration} minutes at most), retrying...", "error")
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

def get_sound_path(station: str) -> str | None:
    announcement_dir = Path("src/data/announcements")

    for file in announcement_dir.iterdir():
        if file.is_file():
            if station.lower() in file.stem.lower():
                sound_file = file.resolve()
                return sound_file

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
            line = f"• __{name}__ ({stop_arrival.strftime("%H:%M")})"
        else:
            stop_arrival = info["arrival"]
            line = f"• {name} ({stop_arrival.strftime("%H:%M")})"

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

def generate_static_map(stops: dict, mode: str, operator: str, route_color: str):
    logger("Generating a new route map..")
    operator_metadata = get_operator_metadata(operator, route_color, mode)
    operator_color = operator_metadata["color"]
    if operator_color == 0xFFFFFF:
        stop_color = staticmaps.Color(105, 105, 105, 255)
    else:
        stop_color = staticmaps.parse_color(f"#{operator_color:06x}")

    white = staticmaps.Color(255, 255, 255, 255)
    
    context = staticmaps.Context()

    context.set_tile_provider(
        staticmaps.TileProvider(
            "carto-voyager",
            url_pattern=(
                "https://$s.basemaps.cartocdn.com/"
                "rastertiles/voyager/$z/$x/$y.png"
            ),
            shards=["a", "b", "c", "d"],
            attribution="",
        )
        # It is against the law (and against your morals...) to not give
        # OSM and carto credits for their great work
        # I only removed the attribution text because I really dislike the
        # ugly white box that py-staticmaps adds. Credits are still visible in the
        # embeds footer
    )

    stop_coords = [
        staticmaps.create_latlng(
            stop["lat"],
            stop["lon"],
        )
        for stop in stops.values()
    ]

    context.add_object(
        staticmaps.Line(
            stop_coords,
            color=white,
            width=20,
        )
    )

    context.add_object(
        staticmaps.Line(
            stop_coords,
            color=stop_color,
            width=8,
        )
    )

    last_index = len(stop_coords) - 1
    for i, point in enumerate(stop_coords):
        
        if i == 0 or i == last_index:
            context.add_object(
                staticmaps.Circle(
                    point,
                    radius_km=0.1,
                    fill_color=white,
                    color=stop_color,
                    width=12
                )
            )
            if i == last_index:
                context.add_object(
                    staticmaps.Marker(
                        point,
                        color=stop_color,
                        size=12
                    )
                )
        elif mode not in ["TRAM", "BUS", "SUBWAY", "SUBURBAN", "METRO"]: # wayyy too many stops...
            context.add_object(
                staticmaps.Circle(
                    center=point,
                    fill_color=white,
                    radius_km=0.1,
                    color=stop_color,
                    width=10,
                )
            )

    lats = [c.lat().degrees for c in stop_coords]
    lons = [c.lng().degrees for c in stop_coords]
    lat_span = max(lats) - min(lats)
    lon_span = max(lons) - min(lons)

    MIN_SPAN = 0.01 

    if lat_span < MIN_SPAN or lon_span < MIN_SPAN:
        center_lat = (max(lats) + min(lats)) / 2
        center_lon = (max(lons) + min(lons)) / 2
        pad = MIN_SPAN / 2

        context.add_object(
            staticmaps.Circle(
                staticmaps.create_latlng(center_lat + pad, center_lon + pad),
                radius_km=0.01,
                fill_color=staticmaps.TRANSPARENT,
                color=staticmaps.TRANSPARENT,
                width=0,
            )
        )
        context.add_object(
            staticmaps.Circle(
                staticmaps.create_latlng(center_lat - pad, center_lon - pad),
                radius_km=0.01,
                fill_color=staticmaps.TRANSPARENT,
                color=staticmaps.TRANSPARENT,
                width=0,
            )
        )

    try:
        image = context.render_cairo(400, 300)
        image.write_to_png("src/data/assets/current_map.png")
    except RuntimeError:
        logger(f"You don't have cairo installed! Because of that I can only give you a low-res png of the route...")
        image = context.render_pillow(400, 300)
        image.save("src/data/assets/current_map.png")
    logger("Map generated!")
