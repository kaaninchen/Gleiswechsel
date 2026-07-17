import requests
import random
from datetime import datetime
from src.config import config
from src.data.operators import OPERATORS

def random_connection():
    while True:
        station = random.choice(config["stations"])
        url = f"https://dbf.finalrewind.org/{station}.json"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException:
            continue
        
        departures = [
            d for d in data.get("departures", [])
            if d.get("scheduledDeparture") and d.get("destination") != station
            and not d.get("train", "").startswith("S ")
        ]

        if not departures:
            continue

        dep = random.choice(departures)
        return {
            "train": dep['train'], 
            "destination": dep['destination'], 
            "route": dep['route'], 
            "departure": dep['scheduledDeparture'], 
            "via": dep['via'], 
            "station": station,
            "train_number": dep['trainNumber']
        }

def format_via_list(via: list[str]):
    if not via:
        return ""
    if len(via) == 1:
        return via[0]
    return ", ".join(via[:-1]) + " und " + via[-1] 

def get_train_info(station, train_ID, train_type):
    url = f"https://dbf.finalrewind.org/z/{train_type}%20{train_ID}/{station}.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        return None

    dep = data.get("departure", [])
    arrival_iso = dep["route_post_diff"][-1]["sched_arr"]
    print(dep["operators"])
    return {
        "arrival": arrival_iso,
        "operators": dep["operators"]
    }

def operator_metadata(operator):
    if not operator:
        return OPERATORS["fallback"]

    return OPERATORS.get(operator, OPERATORS["fallback"])

def logger(msg):
    current_time = datetime.now().strftime('%X')
    print(f"{current_time}: {msg}")