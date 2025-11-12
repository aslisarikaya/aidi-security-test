#!/usr/bin/env python3
"""
Einfacher Flask-Webserver, der den aktuellen Bitcoin-Kurs von CoinGecko abfragt.

Funktion:
---------
- Bei jedem HTTP-Aufruf (GET /) liefert der Server einen JSON-Response mit dem aktuellen Preis.
- Der Preis wird lokal in einer Cache-Datei gespeichert.
- Nur wenn der Cache älter als 60 Sekunden ist, wird ein neuer Wert von der API geholt.
- Wenn die API nicht erreichbar ist, wird der zuletzt gespeicherte Preis aus dem Cache zurückgegeben.

Deployment:
-----------
Dieses Script ist so geschrieben, dass es sowohl direkt auf einer VM (über Cloud-init)
als auch in einem Container (Docker) laufen kann.
"""

from flask import Flask, jsonify
import requests
import time
import json
import os
# Flask-App initialisieren
app = Flask(__name__)

# Konfiguration
CACHE_FILE = "/opt/price-server/price_cache.json"
API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
CACHE_TTL = 60  # Sekunden

def get_price():
    """
    Liefert den Bitcoin-Kurs, entweder aus dem Cache oder frisch von der API.

    Ablauf:
    1. Prüfen, ob Cache-Datei existiert und jünger als CACHE_TTL ist.
       -> Falls ja, Rückgabe des gespeicherten Werts.
    2. Andernfalls neuen Kurs von der API abrufen.
       -> Bei Erfolg: Cache-Datei aktualisieren und neuen Wert zurückgeben.
       -> Bei Fehler: Falls Cache vorhanden, alten Wert zurückgeben.
    """
    # Prüfen, ob Cache existiert und aktuell ist
    if os.path.exists(CACHE_FILE):
        age = time.time() - os.path.getmtime(CACHE_FILE)
        if age < CACHE_TTL:
            with open(CACHE_FILE) as f:
                return json.load(f)

    # Cache zu alt → API abrufen
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Cache aktualisieren
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, "w") as f:
            json.dump(data, f)

        return data
    except Exception as e:
        # Fallback: Cache zurückgeben, falls vorhanden
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE) as f:
                return json.load(f)
        return {"error": f"API request failed: {e}"}

@app.route("/")
def index():
    """HTTP-Handler: Gibt den aktuellen Preis als JSON aus."""
    return jsonify(get_price())

if __name__ == "__main__":
    # Server starten – hört auf allen Interfaces, Port 80
    app.run(host="0.0.0.0", port=80)
