"""
THE PROOF: replay a real heatwave and compare CoolHead with "normal" behaviour.

Run:   python backtest.py
Offline test with made-up data:   python backtest.py --demo
Real weather + normal household tariff:   python backtest.py --tou

Makes:  outputs/backtest_chart.png  and prints the scorecard table.
"""

import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from coolhead.model import (ROOM_PRESETS, FIXES, simulate, plan_reactive, plan_thermostat,
                            plan_coolhead, scorecard, carer_message,
                            tou_price, TARIFF_NAME)

# ---- Settings you can change ------------------------------------------------
PLACE = "Penrith"
START, END = "2020-01-03", "2020-01-05"   # Penrith ~48.9°C on 4 Jan 2020 (check in the data!)
ROOM = sys.argv[sys.argv.index("--room") + 1] if "--room" in sys.argv else "Fibro / weatherboard"
BAND_MAX = 27.0      # the person's "brain-safe" upper limit (user-adjustable)
# -----------------------------------------------------------------------------


def load_real():
    from coolhead.data import find_place, history, aemo_prices
    lat, lon, label = find_place(PLACE)
    w = history(lat, lon, START, END)
    if "--tou" in sys.argv:   # real weather, normal household time-of-use tariff
        w["price_c"] = [tou_price(t) for t in w["time"]]
        return w, label, TARIFF_NAME
    try:
        y, m = int(START[:4]), int(START[5:7])
        p = aemo_prices(y, m)
        w = w.merge(p, on="time", how="left")
        w["price_c"] = w["price_c"].ffill().bfill()
        source = "AEMO NSW wholesale + 25c network/retail"
    except Exception as e:
        print("Couldn't get AEMO prices, using the time-of-use tariff instead:", e)
        w["price_c"] = [tou_price(t) for t in w["time"]]
        source = TARIFF_NAME
    return w, label, source


def load_demo():
    """Made-up 3-day heatwave so you can test without internet."""
    times = pd.date_range("2020-01-03", periods=72, freq="h")
    peaks = [38, 47, 33]
    rows = []
    for t in times:
        day, h = (t - times[0]).days, t.hour
        temp = 24 + (peaks[day] - 24) * max(0, math.sin(math.pi * (h - 6) / 18)) if 6 <= h <= 23 else 24
        sun = max(0, 1000 * math.sin(math.pi * (h - 6) / 14)) if 6 <= h <= 20 else 0
        rows.append({"time": t, "outdoor": temp, "sun": sun, "price_c": tou_price(t)})
    return pd.DataFrame(rows), "Demo town (made-up data)", TARIFF_NAME


def main():
    w, label, price_source = load_demo() if "--demo" in sys.argv else load_real()
    room = ROOM_PRESETS[ROOM]
    out, sun, prices = list(w["outdoor"]), list(w["sun"]), list(w["price_c"])
    hours = [t.hour for t in w["time"]]

    no_ac = [False] * len(out)
    plans = {
        "No air-con": no_ac,
        "Usual: switch on when hot": plan_reactive(room, out, sun, BAND_MAX),
        "Usual: thermostat at limit": plan_thermostat(room, out, sun, BAND_MAX),
        "CoolHead plan": plan_coolhead(room, out, sun, prices, BAND_MAX),
    }
    temps = {k: simulate(room, out, sun, v) for k, v in plans.items()}

    print(f"\nPlace: {label} | {START} to {END} | Room: {ROOM} | Safe band max: {BAND_MAX}°C")
    print(f"Hottest outdoor: {max(out):.1f}°C | Prices: {price_source}\n")
    if max(out) < 35:
        print("⚠️  WARNING: this doesn't look like a heatwave. Check the place name and dates above.\n")
    table = pd.DataFrame({k: scorecard(room, temps[k], plans[k], prices, hours, BAND_MAX)
                          for k in plans}).T
    print(table.to_string(), "\n")

    # Cool Room Fixes: how much does each upgrade cut cooling energy?
    base_kwh = table.loc["CoolHead plan", "Cooling kWh"]
    print("Cool Room Fixes (with the CoolHead plan):")
    for fix_name, apply_fix in FIXES.items():
        r2 = apply_fix(room)
        p2 = plan_coolhead(r2, out, sun, prices, BAND_MAX)
        s2 = scorecard(r2, simulate(r2, out, sun, p2), p2, prices, hours, BAND_MAX)
        cut = 100 * (base_kwh - s2["Cooling kWh"]) / base_kwh if base_kwh else 0
        print(f"  {fix_name:38s} cooling energy -{cut:.0f}%   hours too hot: {s2['Hours too hot']}")

    # Step 8 done for you: the headline numbers for the pitch
    u, c = table.loc["Usual: thermostat at limit"], table.loc["CoolHead plan"]
    def pct(a, b):
        return f"{100 * (a - b) / a:.0f}%" if a else "n/a"
    print("\n========== PITCH NUMBERS (CoolHead vs a normal thermostat) ==========")
    print(f"  Both keep the room safe:  hours too hot {u['Hours too hot']:.0f} (thermostat) vs {c['Hours too hot']:.0f} (CoolHead)")
    print(f"  Cooling cost:      ${u['Cooling cost $']:.2f} -> ${c['Cooling cost $']:.2f}   "
          f"saved ${u['Cooling cost $'] - c['Cooling cost $']:.2f} ({pct(u['Cooling cost $'], c['Cooling cost $'])})")
    print(f"  Evening-peak kWh:  {u['Evening-peak kWh']:.1f} -> {c['Evening-peak kWh']:.1f}   "
          f"cut {u['Evening-peak kWh'] - c['Evening-peak kWh']:.1f} kWh ({pct(u['Evening-peak kWh'], c['Evening-peak kWh'])})")
    print(f"  Solar-hours share: {u['Solar-hours share %']:.0f}% -> {c['Solar-hours share %']:.0f}%   "
          f"(+{c['Solar-hours share %'] - u['Solar-hours share %']:.0f} points)")
    spike = 100  # c/kWh: anything above $1/kWh counts as a price spike
    def spike_hours(plan):
        return sum(1 for on, p in zip(plan, prices) if on and p > spike)
    if max(prices) > spike:
        print(f"  Price-spike hours cooled (>$1/kWh): {spike_hours(plans['Usual: thermostat at limit'])} (thermostat) "
              f"vs {spike_hours(plans['CoolHead plan'])} (CoolHead)   most expensive hour: ${max(prices) / 100:.2f}/kWh")
    peak_mwh = (u['Evening-peak kWh'] - c['Evening-peak kWh']) * 10000 / 1000
    print(f"  Scaled up: 10,000 homes like this = {peak_mwh:,.0f} MWh off the evening peak over these {len(out) // 24} days")
    print("  Cool Room Fixes savings: see the list just above")
    print("=====================================================================")

    print("\nSample carer text:")
    print(" ", carer_message("Dad", ROOM, temps["No air-con"], plans["CoolHead plan"],
                             prices, hours, BAND_MAX))

    # Chart
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
    os.makedirs(out_dir, exist_ok=True)
    slug = "demo" if "--demo" in sys.argv else ROOM.split()[0].lower()   # e.g. "fibro"
    if "--tou" in sys.argv:
        slug += "_tou"
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7), sharex=True,
                                   gridspec_kw={"height_ratios": [3, 1]})
    ax1.plot(w["time"], out, color="#bbbbbb", label="Outdoor")
    colours = {"No air-con": "#d62728", "Usual: switch on when hot": "#ff7f0e",
               "Usual: thermostat at limit": "#9467bd", "CoolHead plan": "#1f77b4"}
    for k, t in temps.items():
        if k == "Usual: switch on when hot":
            continue   # keep the chart simple: 3 lines only
        ax1.plot(w["time"], t, label=f"Indoor – {k}", color=colours[k], lw=2)
    ax1.axhspan(0, BAND_MAX, color="#2ca02c", alpha=0.07, label="Brain-safe band")
    ax1.set_ylim(min(out) - 2, max(max(out), max(temps["No air-con"])) + 2)
    ax1.set_ylabel("°C")
    ax1.set_title(f"CoolHead heatwave replay – {label}")
    ax1.legend(loc="upper left", fontsize=8)
    ax2.bar(w["time"], prices, width=0.04, color="#999999")
    on = [p if c else 0 for p, c in zip(prices, plans["CoolHead plan"])]
    ax2.bar(w["time"], on, width=0.04, color="#1f77b4", label="CoolHead cools here")
    ax2.set_ylabel("c/kWh")
    ax2.legend(fontsize=8)
    fig.tight_layout()
    chart_path = os.path.join(out_dir, f"chart_{slug}.png")
    csv_path = os.path.join(out_dir, f"scorecard_{slug}.csv")
    try:
        fig.savefig(chart_path, dpi=150)
        table.to_csv(csv_path)
        print(f"\nSaved {chart_path}\n  and {csv_path}")
    except OSError as e:
        print(f"\nCouldn't save the chart ({e}). If the picture is open in another app, close it and run again.")


if __name__ == "__main__":
    main()
