import json
import requests
import random

from src.utils import logger, config

stations = config["stations"]
blacklist = config["blacklist"]
user_agent = config["http"]["user_agent"]

headers = {
    "User-Agent": f"{user_agent}"
}

endpoint = "https://api.transitous.org"

def get_random_stop_id() -> str:
    stop = random.choice(stations)
    req = f"{endpoint}/api/v1/geocode?text={stop}"

    try:
        response = requests.get(req, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger(f"An error occured while searching for a connection: {e}", "fatal")
        return None

    if response.status_code == 404:
        logger(f"Error finding station '{stop}'")

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
    for entry in data.get("stopTimes", []):
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
        
    return random.choice(trip_ids)

def get_trip_details(trip_id: str) -> dict:
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
    trip_to = legs["tripTo"]["name"]
    start_time = legs["startTime"]
    end_time = legs["endTime"]

    trip_details = {
        "long_name": f"{display_name} nach {trip_to} von {trip_from}",
        "short_name": display_name,
        "from": trip_from,
        "to": trip_to,
        "agency": legs["agencyName"],
        "route_color": legs.get("routeColor"),
        "duration": legs["duration"],
        "start_time": start_time,
        "end_time": end_time,
        "mode": legs["mode"],
        "stops": {}
    }

    trip_details["stops"][trip_from] = start_time
    for stop in legs["intermediateStops"]:
        trip_details["stops"][stop["name"]] = stop["arrival"]
    trip_details["stops"][trip_to] = end_time

    return trip_details    

