import requests
import random
import json
from datetime import datetime, timezone

from src.utils import logger, config, get_train_name, convert_iso_string, validate_connection

stations = config["stations"]
blacklist = config["blacklist"]
user_agent = config["http"]["user_agent"]

headers = {
    "User-Agent": f"{user_agent}"
}

endpoint = "https://api.transitous.org"

def get_random_stop_id() -> str | None:
    assigned_station = random.choice(stations)
    req = f"{endpoint}/api/v1/geocode"

    try:
        response = requests.get(req, params={"text": assigned_station}, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger(f"An error occured while searching for a connection: {e}", "error")
        return None

    if response.status_code == 404:
        logger(f"Error finding station '{assigned_station}'", "error")
        return None

    id = None
    for entry in data:
        if entry.get("type") != "STOP":
            continue
        id = entry.get("id", None)
        break

    if id is None:
        logger(f"Failed to grab ID from '{assigned_station}'", "error")
        return None

    return id

def get_random_connection(stop_id: str) -> str | None:
    if stop_id is None:
        return None
    
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cursor = None
    max_pages = 5
    min_results = 5
    trip_ids = []
    all_stop_times = []

    for _ in range(max_pages):
        params = {
            "stopId": stop_id,
            "n": 20,
            "time": now,
        }
        if cursor:
            params["pageCursor"] = cursor

        try:
            response = requests.get(f"{endpoint}/api/v5/stoptimes", params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            logger(e, "Error")
            break
        
        stop_times = data.get("stopTimes", [])
        all_stop_times.extend(stop_times)

        for entry in stop_times:
            trip_id = entry["tripId"]
            if entry["mode"] in blacklist:
                continue
            else:
                trip_ids.append(entry["tripId"])

        if len(trip_ids) >= min_results:
            break
        
        cursor = data.get("nextPageCursor")
        if not cursor:
            break

    if not trip_ids:
            logger("Couldn't find any connection", "error")
            return None

    trip_id = random.choice(trip_ids)

    from_station = None
    for entry in all_stop_times:
        if entry.get("tripId") == trip_id:
            from_station = entry.get("place", {}).get("name")
            break

    logger(f"Station: {from_station}")
    return {
        "trip_id": trip_id, 
        "from_station": from_station
    }

def get_trip_details(random_connection: dict | None) -> dict | None:
    if random_connection is None:
        return None
    
    req = f"{endpoint}/api/v2/trip"

    try:
        response = requests.get(req, params={"tripId": random_connection["trip_id"]}, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger(f"An error occured while trying to get the route details: {e}", "error")
        return None

    legs = data["legs"][0]
    end_time = legs["endTime"]
    from_station = random_connection["from_station"]
    display_name = legs["displayName"]
    train_from = legs["from"]["name"]
    goes_to = legs["to"]["name"]
    start_time = legs["startTime"]
    mode = legs["mode"]

    is_valid = validate_connection(start_time, end_time)
    if not is_valid:
        return None

    arrival = convert_iso_string(end_time)
    departure = convert_iso_string(start_time)

    train_name = get_train_name(display_name, mode)
    if train_from == from_station:
        long_name = f"{train_name} nach {goes_to} von {train_from}"
    else:
        long_name = f"{train_name} nach {goes_to} über {from_station}"
        
    trip_details = {
        "long_name": long_name,
        "short_name": display_name,
        "station": from_station,
        "from": train_from,
        "to": goes_to,
        "agency": legs["agencyName"],
        "route_color": legs.get("routeColor"),
        "duration": legs["duration"],
        "departure": departure,
        "arrival": arrival,
        "mode": mode,
        "stops": {}
    }

    trip_details["stops"][train_from] = departure

    for stop in legs["intermediateStops"]:
        stop_arrival = convert_iso_string(stop["arrival"])
        trip_details["stops"][stop["name"]] = stop_arrival
        if stop.get("name") == from_station:
            departure_time = stop["departure"]
            trip_details["departure"] = convert_iso_string(departure_time)
    trip_details["stops"][goes_to] = arrival

    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    logger(json.dumps(trip_details, indent=4, ensure_ascii=False))
    return trip_details    

