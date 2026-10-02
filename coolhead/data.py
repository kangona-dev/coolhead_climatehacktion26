"""
Getting real data (needs internet). Everything downloaded is saved in the
data/ folder, so the demo still works if a website goes down.

Sources (all free, no login):
- Open-Meteo forecast + historical weather   https://open-meteo.com
- Open-Meteo place search (suburb -> lat/lon)
- AEMO NSW electricity prices               https://aemo.com.au
"""

import io
import json
import os

import pandas as pd
import requests

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)
TZ = "Australia/Sydney"


def _cached_json(name, url, params):
    path = os.path.join(DATA_DIR, name)
    try:
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        with open(path, "w") as f:
            json.dump(data, f)
        return data
    except Exception:
        if os.path.exists(path):          # offline? use the saved copy
            with open(path) as f:
                return json.load(f)
        raise


def find_place(name):
    """'Penrith' -> (latitude, longitude, nice name). Australian places only."""
    data = _cached_json(f"place_au_{name.lower().replace(' ', '_')}.json",
                        "https://geocoding-api.open-meteo.com/v1/search",
                        {"name": name, "count": 20, "countryCode": "AU"})
    places = [p for p in data.get("results", []) if p.get("country_code") == "AU"]
    if not places:
        raise ValueError(f"Couldn't find an Australian place called '{name}'")
    # prefer NSW if there are several with the same name
    p = next((p for p in places if p.get("admin1") == "New South Wales"), places[0])
    return p["latitude"], p["longitude"], f"{p['name']}, {p.get('admin1', '')}"


def _weather_frame(data):
    h = data["hourly"]
    df = pd.DataFrame({"time": pd.to_datetime(h["time"]),
                       "outdoor": h["temperature_2m"],
                       "sun": h["shortwave_radiation"]})
    df["sun"] = df["sun"].fillna(0)
    df["outdoor"] = df["outdoor"].interpolate()
    return df


def forecast(lat, lon, days=2):
    data = _cached_json(f"forecast_{lat:.2f}_{lon:.2f}.json",
                        "https://api.open-meteo.com/v1/forecast",
                        {"latitude": lat, "longitude": lon, "timezone": TZ,
                         "hourly": "temperature_2m,shortwave_radiation",
                         "forecast_days": days})
    return _weather_frame(data)


def history(lat, lon, start, end):
    """start/end like '2020-01-03'"""
    data = _cached_json(f"history_{lat:.2f}_{lon:.2f}_{start}_{end}.json",
                        "https://archive-api.open-meteo.com/v1/archive",
                        {"latitude": lat, "longitude": lon, "timezone": TZ,
                         "start_date": start, "end_date": end,
                         "hourly": "temperature_2m,shortwave_radiation"})
    return _weather_frame(data)


def aemo_prices(year, month, network_c_per_kwh=25.0):
    """Hourly NSW prices in cents/kWh for one month.
    AEMO gives wholesale $/MWh. $/MWh / 10 = c/kWh. We add a flat amount for
    network + retail charges so it looks like a wholesale-linked household bill.
    (Say this clearly in the pitch: it's an approximation.)"""
    name = f"PRICE_AND_DEMAND_{year}{month:02d}_NSW1.csv"
    path = os.path.join(DATA_DIR, name)
    if not os.path.exists(path):
        url = f"https://aemo.com.au/aemo/data/nem/priceanddemand/{name}"
        r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
    df = pd.read_csv(path)
    # AEMO uses market time (AEST, no daylight saving). Convert to Sydney clock time
    # so it lines up with the weather data.
    df["time"] = (pd.to_datetime(df["SETTLEMENTDATE"])
                  .dt.tz_localize("Etc/GMT-10").dt.tz_convert(TZ).dt.tz_localize(None))
    # AEMO timestamps mark the END of each interval -> shift back to the start
    df["hour"] = (df["time"] - pd.Timedelta(minutes=1)).dt.floor("h")
    hourly = df.groupby("hour")["RRP"].mean().reset_index()
    hourly["price_c"] = hourly["RRP"] / 10 + network_c_per_kwh
    return hourly.rename(columns={"hour": "time"})[["time", "price_c"]]
