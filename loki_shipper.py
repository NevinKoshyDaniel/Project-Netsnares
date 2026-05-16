import json
import requests
import logging
from datetime import datetime, timezone 

logging.basicConfig(level=logging.INFO, format='[*] %(message)s')

JSON_INPUT = "capture/forensic_timeline.json"
LOKI_URL = "http://localhost:3100/loki/api/v1/push"

def push_to_loki():
    logging.info(f"Reading forensic data from {JSON_INPUT}...")
    try:
        with open(JSON_INPUT, 'r') as f:
            timeline_data = json.load(f)
    except FileNotFoundError:
        logging.error("JSON file not found. Ensure analyzer.py ran successfully.")
        return

    logging.info("Formatting payload for Loki (with UTC correction)...")
    
    # Loki requires a specific payload structure
    payload = {"streams": []}

    for entry in timeline_data:
        try:
            dt = datetime.strptime(entry["time"], "%Y-%m-%d %H:%M:%S")
            dt = dt.replace(tzinfo=timezone.utc)
            
            # Convert to epoch nanoseconds using the timezone-aware object
            epoch_ns = str(int(dt.timestamp() * 1e9))
        except ValueError:
            continue # Skip malformed timestamps

        stream = {
            "stream": {
                "project": "netsnares",
                "service_name": "forensics_analyzer",
                "threat_level": entry["threat_assessment"]
            },
            "values": [
                [epoch_ns, json.dumps(entry)]
            ]
        }
        payload["streams"].append(stream)

    logging.info(f"Pushing {len(payload['streams'])} forensic records to Loki...")
    
    # POST to the Loki API
    headers = {'Content-type': 'application/json'}
    response = requests.post(LOKI_URL, json=payload, headers=headers)
    
    if response.status_code == 204:
        logging.info("SUCCESS: Data successfully ingested by Loki.")
    else:
        logging.error(f"FAILED: Loki returned status {response.status_code}")
        logging.error(response.text)

if __name__ == "__main__":
    push_to_loki()