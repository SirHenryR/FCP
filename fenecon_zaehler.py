#!/usr/bin/env python3
import requests
import json
from datetime import datetime

BASE_URL = "URL FEMS (z.B. 192.168.1.100:80)"
USERNAME = "x"
PASSWORD = "user"
TIMEOUT = 5  # Sekunden

# Welche Meter sind verbaut?
METERS = ["meter0", "meter1", "meter2", "meter3"]
CHANNELS = ["ActiveProductionEnergy", "ActiveConsumptionEnergy"]

# vorhandene Zähler benennen 
METER_LABELS = {
    "meter0": "Netzzähler",
    "meter1": "Erzeugungszähler",
    "meter2": "Notstromzähler",
    "meter3": "Wärmepumpenzähler",
}

# Pushover-Konfiguration (eigene Daten eintragen)
PUSHOVER_TOKEN = "DEIN_APP_TOKEN"
PUSHOVER_USER  = "DEIN_USER_KEY"
PUSHOVER_URL   = "https://api.pushover.net/1/messages.json"
PUSHOVER_DEV	 = "Empfänger-Geräte (mehrere mit Komma getrennt)"

def fetch_value(meter: str, channel: str) -> dict | None:
    url = f"{BASE_URL}/rest/channel/{meter}/{channel}"
    try:
        resp = requests.get(url, auth=(USERNAME, PASSWORD), timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f"Fehler beim Abruf von {meter}/{channel}: {e}")
        return None

def format_wh(value: int) -> str:
    return f"{value:,}".replace(",", ".")

def format_kwh(value: int) -> str:
    kwh = value / 1000.0
    return f"{kwh:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def send_pushover(message: str, title: str = "Energieübersicht") -> None:
    data = {
        "token": PUSHOVER_TOKEN,
        "user": PUSHOVER_USER,
        "title": 'Zählerstände',
        "device": PUSHOVER_DEV,
        "message": message,
    }
    resp = requests.post(PUSHOVER_URL, data=data, timeout=5)
    resp.raise_for_status()

def main():
    ts = datetime.now().isoformat(timespec="seconds")

    lines = [f"Zeitstempel: {ts}", ""]
    print(f"Zeitstempel: {ts}\n")

    for meter in METERS:
        label = METER_LABELS.get(meter, meter)
        header = f"{label} ({meter}):"
        print(header)
        lines.append(header)

        for channel in CHANNELS:
            data = fetch_value(meter, channel)
            if data is None:
                continue

            unit = data.get("unit", "")
            value = int(data.get("value", 0))

            wh_str = format_wh(value)
            kwh_str = format_kwh(value)

            line = f"  {channel}: {wh_str} {unit} ({kwh_str} kWh)"
            print(line)
            lines.append(line)

        print()
        lines.append("")

    # Nachricht für Pushover zusammenbauen
    message = "\n".join(lines)

    try:
        send_pushover(message)
        print("Pushover-Benachrichtigung gesendet.")
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Senden an Pushover: {e}")

if __name__ == "__main__":
    main()

