"""
CoolHead web app.   Run:  streamlit run app.py
"""

import pandas as pd
import streamlit as st

from coolhead.model import (ROOM_PRESETS, FIXES, simulate, plan_thermostat,
                            plan_coolhead, scorecard, carer_message,
                            example_tou_price, cooling_blocks)
from coolhead.charts import room_chart
from coolhead import data

st.set_page_config(page_title="CoolHead", page_icon="🧠", layout="centered")

st.title("🧠 CoolHead")
st.write("Every heat app tells you the temperature. **CoolHead simulates your room** "
         "and plans cooling around your **brain-safe range**, at the cheapest hours, before the evening peak.")
st.caption("COP31 priority: **Resilient Cities & Buildings** (supporting: Electrification). "
           "Not medical advice – set your safe range with your GP or pharmacist.")

with st.expander("ℹ️ How CoolHead works (30-second version)"):
    st.markdown(
        "1. **Mini room simulation.** No sensor needed: from the weather forecast and the type of home, "
        "CoolHead estimates how hot the room will get, hour by hour.\n"
        "2. **Brain-safe band.** You set the upper temperature limit with your GP's advice. Heat affects "
        "sleep, mood and thinking, especially for older people and people with dementia.\n"
        "3. **Smart cooling plan.** CoolHead finds when the room would get too hot and pre-cools it "
        "at the cheapest hours beforehand, instead of running the air-con flat out in the 4–9pm peak.\n"
        "4. **Cool Room Fixes.** It tests cheap upgrades (blinds, draught sealing, insulation) so you can "
        "see how much cooling energy each saves before you spend money.")

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
st.success(carer_message(name, room_name, t_none, plan, prices, hours, band_max, times=list(w["time"])))

# ---- The plan itself -----------------------------------------------------------
st.subheader("🗓️ Cooling plan")
blocks = cooling_blocks(list(w["time"]), plan, prices)
if not blocks:
    st.write("No cooling needed – the room stays inside the safe band.")
else:
    st.table(pd.DataFrame([{
        "Day": b["day"],
        "Cool from": b["start"],
        "Until": b["end"],
        "Air-con on for": f"{b['hours']} h",
        "Power price": f"{b['avg_price']:.0f}c/kWh",
        "When": "⚠️ evening peak" if b["in_peak"] else "✅ before the peak",
    } for b in blocks]))
    st.caption("Set the air-con to these times (or let a smart plug do it). "
               "CoolHead runs it before the room gets too hot, not after.")

# ---- Chart -------------------------------------------------------------------
st.subheader("🌡️ How hot the room gets")
st.pyplot(room_chart(list(w["time"]), {
    "Outdoor": out, "Room – no cooling": t_none,
    "Room – usual thermostat": t_usual, "Room – CoolHead": t_plan}, band_max))

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
    def price_text(c):
        return f"${c / 100:.2f}/kWh" if c >= 100 else f"{c:.0f}c/kWh"
    st.metric("Cheapest hour", price_text(min(prices)))
    st.metric("Most expensive hour", price_text(max(prices)))
    if max(prices) >= 100:
        st.caption("⚡ That's a price spike – wholesale prices jump when the grid is under stress "
                   "on hot evenings. CoolHead plans around them.")

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
    saved_kwh = s_usual["Cooling kWh"] - s_plan["Cooling kWh"]
    saved_peak = s_usual["Evening-peak kWh"] - s_plan["Evening-peak kWh"]
    wins = []
    if saved_cost >= 0.5:
        wins.append(f"**${saved_cost:.2f} cheaper** ({100 * saved_cost / s_usual['Cooling cost $']:.0f}%)")
    if saved_kwh >= 0.5:
        wins.append(f"**{saved_kwh:.1f} kWh less energy** ({100 * saved_kwh / s_usual['Cooling kWh']:.0f}%)")
    if saved_peak >= 0.5:
        wins.append(f"**{saved_peak:.1f} kWh less in the 4–9pm peak**")
    if wins:
        st.write("Same safety as a normal thermostat, but " + ", ".join(wins) + ".")
        if saved_kwh >= 0.5:
            st.write(f"Across **10,000** NSW homes like this, that's about "
                     f"**{saved_kwh * 10000 / 1000:,.0f} MWh** of cooling energy saved over these days.")
    else:
        st.write("Here a normal thermostat does about as well – try a different room type or safe limit.")

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
