import requests
import random
import os
import importlib
from datetime import datetime
from src.config import config
import src.data.operators as operators_module

_operators_mtime = None

def _reload_operators_if_changed():
    global _operators_mtime

    path = operators_module.__file__
    current_mtime = os.path.getmtime(path)

    if _operators_mtime is None:
        _operators_mtime = current_mtime
        return
    
    if current_mtime != _operators_mtime:
        importlib.reload(operators_module)
        _operators_mtime = current_mtime
        logger("operators.py wurde automatisch neu geladen (Änderungen erkannt)")

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
            and not d.get("train", "").startswith(tuple(config["blacklist"]))
        ]

        if not departures:
            continue

        if config['random']:
            dep = random.choice(departures)
        else:
            dep = departures[0]

        return {
            "train": dep['train'], 
            "destination": dep['destination'], 
            "route": dep['route'], 
            "departure": dep['scheduledDeparture'], 
            "via": dep['via'], 
            "station": station,
            "train_number": dep['trainNumber']
        }

def get_train_info(station, train_ID, train_type):
    url = f"https://dbf.finalrewind.org/z/{train_type}%20{train_ID}/{station}.json"
    logger(f"Fetche {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger(f"ReqestException Fehler: {e}")
        return None

    dep = data.get("departure", [])
    if not dep:
        logger("Kein departure Feld gefunden")
        return None
    
    route_post = dep.get("route_post_diff")
    if not route_post:
        logger("Kein route_post_diff Feld gefunden")
        return None
    
    arrival_iso = route_post[-1].get("sched_arr")
    if not arrival_iso:
        logger("Keine Ankunftszeit gefunden")
        return None
    
    return {
        "arrival": arrival_iso,
        "operators": dep.get("operators"),
    }

def format_via_list(via: list[str]):
    if not via:
        return ""
    if len(via) == 1:
        return via[0]
    return ", ".join(via[:-1]) + " und " + via[-1] 

def resolve_operator(operators):
    if not operators:
        return None
    for op in operators:
        if op in operators_module.OPERATOR_ALIASES or op in operators_module.OPERATORS:
            return op
        
    return operators[0]

def operator_metadata(operator):
    _reload_operators_if_changed()

    if not operator:
        return operators_module.OPERATORS["fallback"]

    if operator in operators_module.OPERATOR_ALIASES:
        return operators_module.OPERATOR_ALIASES[operator]

    return operators_module.OPERATORS.get(operator, operators_module.OPERATORS["fallback"])

def logger(msg, log_type="info"):
    current_time = datetime.now().strftime('%X')
    print(f"{current_time}: {log_type.upper()}: {msg}")
    if log_type.lower() == "fatal":
        os._exit(1)