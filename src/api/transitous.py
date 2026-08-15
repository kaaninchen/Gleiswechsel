import json
import requests
import random
from src.utils import logger
from ... import config

stations = config["stations"]
blacklist = config["blacklist"]
user_agent = config["http"]["user_agent"]

headers = {
    "User-Agent": f"{user_agent}"
}

endpoint = "https://api.transitous.org"

def get_stop_id(stop):
    req = f"{endpoint}/api/v1/geocode?text={stop}"

    try:
        response = requests.get(req, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger(f"An error occured while searching for a connection: {e}")
        return None

    if response.status_code == 404:
        logger(f"Error finding station '{stop}'")

    for entry in data:
        if entry.get("type") != "STOP":
            continue
        return entry["id"]

def get_random_connection(stop_id):
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
            print("Couldn't find any connection")
            return None
        
    return random.choice(trip_ids)

def get_trip_details(trip_id):
    req = f"{endpoint}/api/v2/trip?tripId={trip_id}"

    try:
        response = requests.get(req, headers=headers)
        response.raise_for_status
        data = response.json()
    except requests.RequestException as e:
        print("e")
        return None

    legs = data["legs"][0]

    trip_from = legs["tripFrom"]["name"]
    trip_to = legs["tripTo"]["name"]
    start_time = legs["startTime"]
    end_time = legs["endTime"]

    trip_details = {
        "name": legs["displayName"],
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

assigned_station = random.choice(stations)
print(assigned_station)

stop_id = get_stop_id(assigned_station)
trip_id = get_random_connection(stop_id)
print(json.dumps(get_trip_details(trip_id), indent=2, ensure_ascii=False))

