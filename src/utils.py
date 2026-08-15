import json
import os
from datetime import datetime

with open("config.json", "r") as file:
    config = json.load(file)

def logger(msg, log_type="info") -> str:
    status = log_type.upper()
    current_time = datetime.now().strftime('%X')
    print(f"{current_time}: {status}: {msg}")
    if status == "FATAL":
        os._exit(1)