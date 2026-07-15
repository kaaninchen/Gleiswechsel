import requests
import random
from config import config

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
        return [dep['train'], dep['destination'], station]
