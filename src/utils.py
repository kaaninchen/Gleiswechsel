import requests
import random
from config import config
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
        ]

        if not departures:
            continue

        dep = random.choice(departures)
        return [dep['train'], dep['destination'], dep['route'], dep['scheduledDeparture'], dep['via'], station]
    

def operator_infos(train):
    if not train:
        return OPERATORS["Fallback"]

    train_type = train.split()[0]

    return OPERATORS.get(train_type, OPERATORS["fallback"])

def format_via_list(via: list[str]):
    if not via:
        return ""
    if len(via) == 1:
        return via[0]
    return ", ".join(via[:-1]) + " und " + via[-1] 