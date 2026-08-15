import requests
import random
from datetime import datetime

from src.utils import logger, config, get_train_name, convert_iso_string

stations = config["stations"]
blacklist = config["blacklist"]
user_agent = config["http"]["user_agent"]

headers = {
    "User-Agent": f"{user_agent}"
}

endpoint = "https://api.transitous.org"

def get_random_stop_id() -> str:
    assigned_station = random.choice(stations)
    req = f"{endpoint}/api/v1/geocode?text={assigned_station}"

    try:
        response = requests.get(req, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger(f"An error occured while searching for a connection: {e}", "fatal")
        return None

    if response.status_code == 404:
        logger(f"Error finding station '{assigned_station}'")

    for entry in data:
        if entry.get("type") != "STOP":
            continue
        return entry["id"]

def get_random_connection(stop_id: str) -> str:
    max_pages = 5
    cursor = None
    count = 20

    for _ in range(max_pages):
        params = f"stopId={stop_id}&n={count}"
        if cursor:
            params += f"&pageCursor={cursor}"

        req = f"{endpoint}/api/v1/stoptimes?{params}"

    try:
        response = requests.get(req, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(e)
        return None

    trip_ids = []
    stop_times = data.get("stopTimes", [])
    for entry in stop_times:
        trip_id = entry["tripId"]
        if entry["mode"] in blacklist:
            continue
        trip_ids.append(trip_id)

        if len(trip_ids) >= 5:
            break

        cursor = data.get("nextPageCursor")
        if not cursor:
            break

        if not trip_ids:
            logger("Couldn't find any connection", "fatal")
            return None
        
    trip_id = random.choice(trip_id)
    from_station = stop_times[0]["place"]["name"]
    return {
        "trip_id": random.choice(trip_ids), 
        "from_station": from_station
        }

def get_trip_details(trip_id: str, from_station: str) -> dict:
    req = f"{endpoint}/api/v2/trip?tripId={trip_id}"

    try:
        response = requests.get(req, headers=headers)
        response.raise_for_status
        data = response.json()
    except requests.RequestException as e:
        logger(f"An error occured while trying to get the route details: {e}", "fatal")
        return None

    legs = data["legs"][0]

    display_name = legs["displayName"]
    trip_from = legs["tripFrom"]["name"]
    goes_to = legs["tripTo"]["name"]
    start_time = legs["startTime"]
    end_time = legs["endTime"]
    mode = legs["mode"]

    departure = convert_iso_string(start_time)
    arrival = convert_iso_string(end_time)
    train_name = get_train_name(display_name, mode)

    trip_details = {
        "long_name": f"{train_name} nach {goes_to} von {from_station}",
        "short_name": display_name,
        "from": from_station,
        "to": goes_to,
        "agency": legs["agencyName"],
        "route_color": legs.get("routeColor"),
        "duration": legs["duration"],
        "departure": departure,
        "arrival": arrival,
        "mode": mode,
        "stops": {}
    }

    trip_details["stops"][trip_from] = departure
    for stop in legs["intermediateStops"]:
        arrival = convert_iso_string(stop["arrival"])
        trip_details["stops"][stop["name"]] = arrival
        if stop.get("name") == from_station:
            departure_time = stop["departure"]
            trip_details["departure"] = convert_iso_string(departure_time)
    trip_details["stops"][goes_to] = arrival

    return trip_details    

