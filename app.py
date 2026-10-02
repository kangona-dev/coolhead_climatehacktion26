"""
CoolHead web app.   Run:  streamlit run app.py
"""

import pandas as pd
import streamlit as st

from coolhead.model import (ROOM_PRESETS, FIXES, simulate, plan_thermostat,
                            plan_coolhead, scorecard, carer_message,
                            example_tou_price)
from coolhead import data

st.set_page_config(page_title="CoolHead", page_icon="🧠", layout="centered")

st.title("🧠 CoolHead")
st.write("Every heat app tells you the temperature. **CoolHead simulates your room** "
         "and plans cooling around your **brain-safe range**, at the cheapest, cleanest hour.")
st.caption("COP31 priority: **Resilient Cities & Buildings** (supporting: Electrification). "
           "Not medical advice – set your safe range with your GP or pharmacist.")

# Profiles are STARTING POINTS the user adjusts. Do not present them as medical thresholds.
PROFILES = {
    "Older adult": 26,
    "Person living with dementia": 26,
    "Takes heat-sensitive medication": 26,
    "Teen / young adult": 28,
    "Custom": 27,
}

with st.sidebar:
    st.header("1. Who and where")
    name = st.text_input("Who are you caring for?", "Dad")
    place = st.text_input("Suburb", "Penrith")
    profile = st.selectbox("Profile", list(PROFILES))
    band_max = st.slider("Brain-safe upper limit (°C)", 22, 32, PROFILES[profile])
    st.caption("[NSW Health: beat the heat](https://www.health.nsw.gov.au/environment/beattheheat)")
    st.header("2. Their room")
    room_name = st.selectbox("Room type", list(ROOM_PRESETS), index=list(ROOM_PRESETS).index("Top-floor apartment"))
    st.header("3. Electricity")
    price_mode = st.radio("What to show", ["Replay a real heatwave (Jan 2020)", "Live: next 48 hours"])

room = ROOM_PRESETS[room_name]

# ---- Get weather + prices --------------------------------------------------
try:
    lat, lon, label = data.find_place(place)
    if price_mode.startswith("Replay"):
        w = data.history(lat, lon, "2020-01-03", "2020-01-05")
        try:
            w = w.merge(data.aemo_prices(2020, 1), on="time", how="left")
            w["price_c"] = w["price_c"].ffill().bfill()
            price_note = "real NSW electricity prices from that week"
        except Exception:
            w["price_c"] = [example_tou_price(t.hour) for t in w["time"]]
            price_note = "an example time-of-use tariff"
        st.info(f"Replaying the 3–5 January 2020 heatwave in {label} "
                f"(hottest: {w['outdoor'].max():.0f}°C), with {price_note}.")
    else:
        w = data.forecast(lat, lon, days=2)
        w["price_c"] = [example_tou_price(t.hour) for t in w["time"]]
        st.info(f"Next 48 hours in {label} (hottest: {w['outdoor'].max():.0f}°C), "
                "with an example time-of-use tariff.")
except Exception as e:
    st.error(f"Couldn't get weather data ({e}). Check the suburb name or your internet.")
    st.stop()

out, sun, prices = list(w["outdoor"]), list(w["sun"]), list(w["price_c"])
hours = [t.hour for t in w["time"]]

usual = plan_thermostat(room, out, sun, band_max)
plan = plan_coolhead(room, out, sun, prices, band_max)
t_none = simulate(room, out, sun, [False] * len(out))
t_usual = simulate(room, out, sun, usual)
t_plan = simulate(room, out, sun, plan)

# ---- Carer text -------------------------------------------------------------
st.subheader("📱 Today's message")
st.success(carer_message(name, room_name, t_none, plan, prices, hours, band_max))

# ---- Chart -------------------------------------------------------------------
st.subheader("🌡️ How hot the room gets")
# columns kept in alphabetical order so each line gets the right colour
chart = pd.DataFrame({"Outdoor": out, "Room – CoolHead": t_plan,
                      "Room – no cooling": t_none, "Room – usual thermostat": t_usual},
                     index=w["time"])
st.line_chart(chart, color=["#9e9e9e", "#1f77b4", "#d62728", "#9467bd"])

# ---- Two sets of vital signs -------------------------------------------------
left, right = st.columns(2)
with left:
    st.markdown("**🧠 Person**")
    drop = max(t_none) - max(t_plan)
    st.metric("Hottest room temp (CoolHead)", f"{max(t_plan):.1f}°C",
              delta=f"-{drop:.1f}°C vs no cooling" if drop >= 0.1 else None, delta_color="inverse")
    st.metric("Hottest room temp (no cooling)", f"{max(t_none):.1f}°C")
with right:
    st.markdown("**⚡ Grid**")
    st.metric("Cheapest hour", f"{min(prices):.0f}c/kWh")
    st.metric("Most expensive hour", f"{max(prices):.0f}c/kWh")

# ---- COP31 scorecard -----------------------------------------------------------
st.subheader("🌏 COP31 scorecard")
s_usual = scorecard(room, t_usual, usual, prices, hours, band_max)
s_plan = scorecard(room, t_plan, plan, prices, hours, band_max)
FORMATS = {"Hours too hot": "{:.0f}", "Hottest indoor °C": "{:.1f}°C", "Cooling cost $": "${:.2f}",
           "Cooling kWh": "{:.1f}", "Evening-peak kWh": "{:.1f}", "Solar-hours share %": "{:.0f}%"}
st.table(pd.DataFrame({"Usual thermostat": {k: FORMATS[k].format(v) for k, v in s_usual.items()},
                       "CoolHead": {k: FORMATS[k].format(v) for k, v in s_plan.items()}}))
if s_usual["Cooling kWh"] == 0:
    st.write("No cooling needed in this period. Try **Replay a real heatwave** or a hotter room type.")
else:
    saved_cost = s_usual["Cooling cost $"] - s_plan["Cooling cost $"]
    saved_peak = s_usual["Evening-peak kWh"] - s_plan["Evening-peak kWh"]
    st.write(f"Same safety, **${saved_cost:.2f} cheaper** and **{saved_peak:.1f} kWh less** in the evening peak. "
             f"Across **10,000** NSW homes that's about **{saved_peak * 10000 / 1000:,.0f} MWh** off the evening peak.")

# ---- Cool Room Fixes -----------------------------------------------------------
st.subheader("🔧 Cool Room Fixes – test before you spend")
rows = []
for fix_name, apply_fix in FIXES.items():
    r2 = apply_fix(room)
    p2 = plan_coolhead(r2, out, sun, prices, band_max)
    s2 = scorecard(r2, simulate(r2, out, sun, p2), p2, prices, hours, band_max)
    cut = 100 * (s_plan["Cooling kWh"] - s2["Cooling kWh"]) / s_plan["Cooling kWh"] if s_plan["Cooling kWh"] else 0
    rows.append({"Fix": fix_name, "Cooling energy saved": f"{cut:.0f}%",
                 "Cost for this period": f"${s2['Cooling cost $']:.2f}"})
st.table(pd.DataFrame(rows))

st.caption("Room temperatures are estimates from a simple room simulation, not a sensor. "
           "Weather: Open-Meteo. Prices: example tariff or AEMO NSW wholesale + 25c/kWh.")
