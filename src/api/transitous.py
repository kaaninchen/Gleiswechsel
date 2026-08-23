import requests
import random
import json
from datetime import datetime, timezone

from src.utils import logger, get_train_name, validate_connection, parse_iso
from src.config import config
from src.lang.locales import lang


station_names = config.connections.stations
station_IDs = config.connections.IDs
blacklist = config.connections.blacklist
user_agent = config.http.user_agent

headers = {
    "User-Agent": f"{user_agent}"
}

endpoint = "https://api.transitous.org"

def check_stations():
    logger(f"Testing {len(station_names)} stations...")
    all_stations_output = {}
    minimal_overview = {}

    for station in station_names:
        req = f"{endpoint}/api/v1/geocode"

        try:
            response = requests.get(req, params={"text": station}, headers=headers)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            logger(f"An error occured while checking for station {station}: {e}")
            continue

        stops_dict = {}
        aliases_list = []
        exact_match = False

        for entry in data:
            if entry.get("type") != "STOP":
                continue

            station_id = entry.get("id") 
            stop_name = entry.get("name")
            coords = f"{entry.get("lat")}, {entry.get("lon")}"
            modes = entry.get("modes")

            stop_details = {
                "tz": entry.get("tz"),
                "country": entry.get("country"),
                "coords": coords,
                "id": station_id,
                "modes": modes,
            }

            if stop_name:
                stops_dict[stop_name] = stop_details
                aliases_list.append(stop_name)

            if stop_name == station:
                if not exact_match:
                    exact_match = True

        if not stops_dict:
            logger("Failed to grab ID from 'search_name'", "error")
            continue

        all_stations_output[station] = {
            "exact_match": exact_match,
            "associated": stops_dict
        }

        minimal_overview[station] = {
            "exact_match": exact_match,
            "names": aliases_list
        }

    logger(json.dumps(minimal_overview, indent=4, ensure_ascii=False))


    print(f"\nIf you want, I can save a more detailed version directly as a json file to disk.")
    print("The json would provide informations like coords, country and transport modes that are from every specific associated station.")
    prompt = input("This would help you to identify the associated stations more accurately (y/n): ")
    if prompt == "y" or prompt == "yes":
        with open('stations.json', 'w') as f:
            json.dump(all_stations_output, f, indent=4, ensure_ascii=False)
            logger("stations.json generated")
    else:
        logger("okay :(")


def get_random_stop_id() -> str | None:
    stations = {}

    if len(station_names) > 0:
        for entry in station_names:
            if entry != "":
                stations[entry] = "name"

    if len(station_IDs) > 0:
        for entry in station_IDs:
            if entry != "":
                stations[entry] = "ID"

    if not stations:
        logger("Both stations and IDs are empty...", "FATAL")

    assigned_station = random.choice(list(stations.keys()))

    if stations[assigned_station] == "ID":
        return assigned_station
    
    req = f"{endpoint}/api/v1/geocode"

    try:
        response = requests.get(req, params={"text": assigned_station}, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger(f"An error occured while searching for a connection: {e}", "error")
        return None

    stop_ids = {}
    for entry in data:
        if entry.get("type") != "STOP":
            continue

        stop_name = entry.get("name")
        stop_id = entry.get("id", None)
        stop_ids[stop_id] = stop_name
            
        if stop_name == assigned_station:
            stop_ids.clear()
            stop_ids[stop_id] = stop_name
            break

    if stop_ids is None:
        logger(f"Failed to grab ID from '{assigned_station}'", "error")
        return None

    stop_ids_list = list(stop_ids.keys())
    chosen_stop_id = random.choice(stop_ids_list)
    if len(stop_ids_list) > 1:
        logger(f"No station associated as '{assigned_station}', choosing random from similar named stations")
        logger(f"Run `python run main.py stations` to get exact station names")
        logger(f"Selected station: {stop_ids[chosen_stop_id]}")

    return chosen_stop_id

def get_random_connection(stop_id: str) -> str | None:
    if stop_id is None:
        return None
    
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    params = {"stopId": stop_id, "n": 50, "time": now}

    try:
        response = requests.get(f"{endpoint}/api/v5/stoptimes", params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger(e, "Error")
        return None

    candidates = []
    for entry in data.get("stopTimes", []):
        if entry["mode"] in blacklist:
            continue
        candidates.append(entry)
        
    if not candidates:
        logger("Couldn't find any connections", "error")
        return None
    
    if config.connections.priority:
        best_priority = None
        for entry in candidates:
            priority = config.connections.priority.get(entry["mode"], 99)
            if best_priority is None or priority < best_priority:
                best_priority = priority

        best_candidates = []
        for entry in candidates:
            priority = config.connections.priority.get(entry["mode"], 99)
            if priority == best_priority:
                best_candidates.append(entry)

        chosen = random.choice(best_candidates)
    else:
        chosen = random.choice(candidates)

    return {
        "trip_id": chosen["tripId"], 
        "from_station": chosen.get("place", {}).get("name"),
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

    if goes_to == train_from:
        logger(f"Bot doesn't know what to do with round trips, I'll have to implement this some day", "error")
        return None # TODO actually handel this 

    all_stop_names = [train_from] + [stop["name"] for stop in legs["intermediateStops"]] + [goes_to]
    if len(all_stop_names) != len(set(all_stop_names)):
        logger("Route reuses station names! Skipping, to be safe...", "error")
        return None # TODO this too

    arrival_dt = parse_iso(end_time)
    departure_dt = parse_iso(start_time)

    train_name = get_train_name(display_name, mode) # used by lang
    if len(lang.channel.long_name.train_from()) >= 100:
        channel_name = lang.channel.short_name
    else:
        if train_from == from_station:
            channel_name = lang.channel.long_name.train_from()
        else:
            channel_name = lang.channel.long_name.train_via()

    trip_details = {
        "channel_name": channel_name,
        "station": from_station,
        "from": train_from,
        "to": goes_to,
        "agency": legs["agencyName"],
        "route_color": legs.get("routeColor"),
        "departure": departure_dt.strftime("%H:%M"),
        "departure_dt": departure_dt,
        "arrival": arrival_dt.strftime("%H:%M"),
        "arrival_dt": arrival_dt,
        "mode": mode,
        "stops": {}
    }  

    train_from_importance = legs["from"]["importance"]
    trip_details["stops"][train_from] = {
        "arrival": departure_dt,
        "importance": train_from_importance,
        "lat": legs["from"]["lat"],
        "lon": legs["from"]["lon"]
    }
    
    departure_time_iso = start_time
    
    for stop in legs["intermediateStops"]:
        stop_arrival_dt = parse_iso(stop["arrival"])
        stop_importance = stop["importance"]
        stop_details = {
            "arrival": stop_arrival_dt,
            "importance": stop_importance,
            "lat": stop["lat"],
            "lon": stop["lon"]
        }
        trip_details["stops"][stop["name"]] = stop_details 

        if stop.get("name") == from_station:
            departure_time_iso = stop["departure"]
            trip_details["departure"] = parse_iso(departure_time_iso).strftime("%H:%M")

    train_to_importance = legs["to"]["importance"]
    trip_details["stops"][goes_to] = {
        "arrival": arrival_dt,
        "importance": train_to_importance,
        "lat": legs["to"]["lat"],
        "lon": legs["to"]["lon"]
    }

    valid = validate_connection(start_time, end_time, departure_time_iso)
    if not valid:
        return None
    
    return trip_details    

