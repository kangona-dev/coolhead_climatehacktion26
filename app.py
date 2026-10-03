"""
CoolHead web app.   Run:  py -m streamlit run app.py
"""

import re

import pandas as pd
import streamlit as st

from coolhead.model import (ROOM_PRESETS, FIXES, simulate, plan_thermostat,
                            plan_coolhead, scorecard, carer_message,
                            tou_price, TARIFF_NAME, cooling_blocks)
from coolhead.charts import room_chart
from coolhead import data, ui

st.set_page_config(page_title="CoolHead", page_icon="🧠", layout="centered")


def show(html):
    """Render our own HTML. Newlines are collapsed so Markdown can't mangle it."""
    st.markdown(re.sub(r"\s*\n\s*", " ", html), unsafe_allow_html=True)


show(ui.CSS)

# Profiles are STARTING POINTS the user adjusts. Do not present them as medical thresholds.
PROFILES = {
    "Older adult": 26,
    "Person living with dementia": 26,
    "Takes heat-sensitive medication": 26,
    "Teen / young adult": 28,
    "Custom": 27,
}

with st.sidebar:
    st.header("Who and where")
    name = st.text_input("Who are you caring for?", "Dad")
    place = st.text_input("Suburb", "Penrith")
    profile = st.selectbox("Profile", list(PROFILES))
    band_max = st.slider("Brain-safe upper limit (°C)", 22, 32, PROFILES[profile])
    st.caption("Set this with their GP or pharmacist. "
               "[NSW Health: beat the heat](https://www.health.nsw.gov.au/environment/beattheheat)")
    st.header("Their room")
    room_name = st.selectbox("Room type", list(ROOM_PRESETS),
                             index=list(ROOM_PRESETS).index("Top-floor apartment"))
    st.header("Weather")
    price_mode = st.radio("Show", ["Replay a real heatwave (Jan 2020)", "Live: next 48 hours"])

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
            w["price_c"] = [tou_price(t) for t in w["time"]]
            price_note = TARIFF_NAME
        period = "during the real 3–5 January 2020 heatwave"
    else:
        w = data.forecast(lat, lon, days=2)
        w["price_c"] = [tou_price(t) for t in w["time"]]
        price_note = TARIFF_NAME
        period = "over the next 48 hours"
except Exception as e:
    st.error(f"Couldn't find weather for “{place}”. Check the suburb spelling, then try again. ({e})")
    st.stop()

times = list(w["time"])
out, sun, prices = list(w["outdoor"]), list(w["sun"]), list(w["price_c"])
hours = [t.hour for t in times]

no_ac = [False] * len(out)
usual = plan_thermostat(room, out, sun, band_max)
plan = plan_coolhead(room, out, sun, prices, band_max)
t_none = simulate(room, out, sun, no_ac)
t_usual = simulate(room, out, sun, usual)
t_plan = simulate(room, out, sun, plan)
s_none = scorecard(room, t_none, no_ac, prices, hours, band_max)
s_usual = scorecard(room, t_usual, usual, prices, hours, band_max)
s_plan = scorecard(room, t_plan, plan, prices, hours, band_max)

# ---- Hero: the thermal scale + outcomes -------------------------------------
show(ui.hero(max(out), max(t_none), max(t_plan), band_max, label, period, room_name)
     + ui.outcome_row(s_none, s_usual, s_plan))
st.caption(f"{room_name}, compared with a normal thermostat set to the same limit. Prices: {price_note}. "
           "COP31 priority: Resilient Cities & Buildings (supporting: Electrification). Not medical advice.")

# ---- The text a carer receives ----------------------------------------------
st.header("Today's message")
show(ui.text_message(carer_message(name, room_name, t_none, plan, prices, hours, band_max, times=times), name))

# ---- The plan ------------------------------------------------------------------
st.header("When to run the air-con")
if not any(plan):
    st.write("No cooling needed. The room stays under the safe limit the whole time.")
else:
    show(ui.plan_strip(times, plan, prices))
    if max(prices) >= 100:
        st.caption(f"The most expensive hour hit ${max(prices) / 100:.2f}/kWh. Wholesale prices spike when "
                   "the grid is stressed on hot evenings, so CoolHead cools earlier where it safely can.")
    with st.expander("Exact times"):
        st.table(pd.DataFrame([{
            "Day": b["day"], "Cool from": b["start"], "Until": b["end"],
            "Air-con on for": f"{b['hours']} h", "Average price": f"{b['avg_price']:.0f}c/kWh",
            "Timing": "includes 4–9pm peak" if b["in_peak"] else "before the peak",
        } for b in cooling_blocks(times, plan, prices)]))

# ---- Chart -------------------------------------------------------------------
st.header("How hot the room gets")
st.pyplot(room_chart(times, {
    "Outdoor": out, "Room – no cooling": t_none,
    "Room – usual thermostat": t_usual, "Room – CoolHead": t_plan}, band_max))

# ---- Cool Room Fixes -----------------------------------------------------------
st.header("Test cheap upgrades before you buy")
fix_rows = []
for fix_name, apply_fix in FIXES.items():
    r2 = apply_fix(room)
    p2 = plan_coolhead(r2, out, sun, prices, band_max)
    s2 = scorecard(r2, simulate(r2, out, sun, p2), p2, prices, hours, band_max)
    cut = 100 * (s_plan["Cooling kWh"] - s2["Cooling kWh"]) / s_plan["Cooling kWh"] if s_plan["Cooling kWh"] else 0
    fix_rows.append((fix_name, cut, s2["Cooling cost $"]))
if s_plan["Cooling kWh"]:
    show(ui.fixes_bars(fix_rows))
else:
    st.write("No cooling was needed, so there's nothing to save here. Try the heatwave replay.")

# ---- Details for judges --------------------------------------------------------
with st.expander("How CoolHead works"):
    st.markdown(
        "1. **Mini room simulation.** From the weather and the type of home, CoolHead estimates how hot "
        "the room gets, hour by hour. No sensor needed.\n"
        "2. **Brain-safe limit.** The carer sets the upper limit with the person's GP. Heat affects sleep, "
        "mood and thinking, especially for older people and people living with dementia.\n"
        "3. **Cooling plan.** CoolHead finds when the room would get too hot and cools it beforehand at "
        "cheaper hours, instead of running flat out in the 4–9pm peak.\n"
        "4. **Upgrades.** It re-runs the simulation with blinds, draught sealing or insulation to show "
        "how much cooling energy each one saves.")

with st.expander("Full comparison"):
    FORMATS = {"Hours too hot": "{:.0f}", "Hottest indoor °C": "{:.1f}°C", "Cooling cost $": "${:.2f}",
               "Cooling kWh": "{:.1f}", "Evening-peak kWh": "{:.1f}", "Solar-hours share %": "{:.0f}%"}
    st.table(pd.DataFrame({
        "No cooling": {k: FORMATS[k].format(v) for k, v in s_none.items()},
        "Normal thermostat": {k: FORMATS[k].format(v) for k, v in s_usual.items()},
        "CoolHead": {k: FORMATS[k].format(v) for k, v in s_plan.items()}}))
    saved_kwh = s_usual["Cooling kWh"] - s_plan["Cooling kWh"]
    if saved_kwh >= 0.5:
        st.write(f"Across 10,000 NSW homes like this, that's about **{saved_kwh * 10:,.0f} MWh** "
                 "of cooling energy saved over these days.")

st.caption("Room temperatures are estimates from a simple room simulation, not sensor readings. "
           "Weather: Open-Meteo. Prices: AEMO NSW wholesale + 25c/kWh (heatwave replay), or "
           f"{TARIFF_NAME}: 46.6c peak 4–8pm weekdays, 12.3c solar soak 10am–2pm, 35.7c other times.")
