"""
CoolHead core logic. Plain Python, no internet needed.

Three ideas:
1. ROOM MODEL  - a mini simulation of how hot one room gets, hour by hour,
                 from the outdoor temperature and sunshine (no sensor needed).
2. PLANNER     - decides which hours to run the air-con so the room stays inside
                 the person's safe band, using the CHEAPEST hours possible
                 (this is "pre-cooling").
3. SCORECARD   - the numbers judges care about (cost, peak-time energy, hours
                 too hot) so we can compare CoolHead against "normal" behaviour.
"""

from dataclasses import dataclass, replace

# ---------------------------------------------------------------------------
# 1. ROOM MODEL
# ---------------------------------------------------------------------------

@dataclass
class Room:
    name: str
    lag_hours: float      # how slowly the room follows the outside temp (bigger = slower)
    sun_gain: float       # °C added per hour in full sun (1000 W/m² of sunshine)
    ac_cooling: float = 8.0   # °C per hour the air-con can remove (one room, split system)
    ac_power_kw: float = 1.5  # electricity the air-con uses per hour it runs
    ac_floor: float = 22.0    # air-con never cools below this


# Starting presets. These are ESTIMATES - say so in the pitch.
# If you ever get a sensor, calibrate these numbers against real readings.
ROOM_PRESETS = {
    "Brick house":         Room("Brick house",         lag_hours=8.0, sun_gain=0.6),
    "Fibro / weatherboard": Room("Fibro / weatherboard", lag_hours=3.0, sun_gain=1.2),
    "Top-floor apartment":  Room("Top-floor apartment",  lag_hours=4.0, sun_gain=1.5),
}

# "Cool Room Fixes": cheap upgrades, modelled as changes to the room.
FIXES = {
    "External blinds / shade cloth": lambda r: replace(r, sun_gain=r.sun_gain * 0.5),
    "Seal draughts (door snakes, gaps)": lambda r: replace(r, lag_hours=r.lag_hours * 1.25),
    "Ceiling insulation": lambda r: replace(r, lag_hours=r.lag_hours * 1.3, sun_gain=r.sun_gain * 0.7),
}


def simulate(room, outdoor, sun, ac_on, start_temp=None):
    """Return a list of indoor temperatures, one per hour.

    outdoor: list of outdoor °C per hour
    sun:     list of sunshine W/m² per hour (0 at night)
    ac_on:   list of True/False per hour
    """
    t_in = outdoor[0] + 1.0 if start_temp is None else start_temp
    temps = []
    for t_out, s, on in zip(outdoor, sun, ac_on):
        temps.append(t_in)
        # drift towards outdoor temperature, plus sun heating
        t_in = t_in + (t_out - t_in) / room.lag_hours + room.sun_gain * s / 1000
        if on:
            t_in = max(room.ac_floor, t_in - room.ac_cooling)
    return temps


# ---------------------------------------------------------------------------
# 2. PLANNERS
# ---------------------------------------------------------------------------

def plan_reactive(room, outdoor, sun, band_max):
    """What most people do: turn the air-con on once it already feels hot,
    turn it off once it's 1°C below the limit."""
    ac_on, t_in, on = [], outdoor[0] + 1.0, False
    for t_out, s in zip(outdoor, sun):
        if t_in > band_max:
            on = True
        elif t_in < band_max - 1:
            on = False
        ac_on.append(on)
        t_in = t_in + (t_out - t_in) / room.lag_hours + room.sun_gain * s / 1000
        if on:
            t_in = max(room.ac_floor, t_in - room.ac_cooling)
    return ac_on


def plan_thermostat(room, outdoor, sun, band_max):
    """A normal thermostat set to the safe limit: it runs whenever the room
    would otherwise go over. Keeps the person safe, but ignores price -
    so it ends up running hard during the expensive evening peak."""
    ac_on, t_in = [], outdoor[0] + 1.0
    for t_out, s in zip(outdoor, sun):
        drift = t_in + (t_out - t_in) / room.lag_hours + room.sun_gain * s / 1000
        on = drift > band_max
        ac_on.append(on)
        t_in = max(room.ac_floor, drift - room.ac_cooling) if on else drift
    return ac_on


def plan_coolhead(room, outdoor, sun, prices, band_max, look_back=6):
    """CoolHead's planner (greedy, easy to explain):
    1. Simulate the day with no air-con.
    2. Find the FIRST hour the room goes above the safe band.
    3. Of the hours just before it (up to `look_back` hours), switch on the
       BEST-VALUE one: cheap power, but not so early the coolness leaks away.
    4. Repeat until the room stays safe all day (or nothing more can be done).
    Because cheap hours are usually earlier (solar hours), this naturally
    pre-cools the room before the expensive evening peak."""
    n = len(outdoor)
    ac_on = [False] * n
    for _ in range(n * 2):
        temps = simulate(room, outdoor, sun, ac_on)
        too_hot = [h for h in range(n) if temps[h] > band_max + TOLERANCE]
        if not too_hot:
            break
        first = too_hot[0]
        candidates = [h for h in range(max(0, first - look_back), first) if not ac_on[h]]
        if not candidates:
            # can't fix this hour; mark it and move on to the next problem
            candidates = [h for h in range(first, n) if not ac_on[h]][:1]
            if not candidates:
                break
        # "best value" hour = cheapest price per degree of cooling that still
        # remains by the problem hour (cooling too early leaks away)
        keep = 1 - 1 / room.lag_hours
        best = min(candidates, key=lambda h: prices[h] / keep ** (first - 1 - h))
        ac_on[best] = True
    return _tidy(room, outdoor, sun, prices, band_max, ac_on, look_back)


def _hours_too_hot(room, outdoor, sun, band_max, ac_on):
    return sum(1 for t in simulate(room, outdoor, sun, ac_on) if t > band_max + TOLERANCE)


def _tidy(room, outdoor, sun, prices, band_max, ac_on, look_back):
    """Clean-up pass:
    a) MOVE: for each cooling hour, most expensive first, try moving it to a
       cheaper hour up to `look_back` hours earlier (pre-cooling).
    b) TRIM: then switch off any hour that isn't actually needed.
    A change is only kept if the room is no less safe than before."""
    ac_on = list(ac_on)
    target = _hours_too_hot(room, outdoor, sun, band_max, ac_on)
    for h in sorted([h for h, on in enumerate(ac_on) if on], key=lambda h: -prices[h]):
        for e in sorted(range(max(0, h - look_back), h), key=lambda e: prices[e]):
            if ac_on[e] or prices[e] >= prices[h]:
                continue
            trial = list(ac_on)
            trial[h], trial[e] = False, True
            if _hours_too_hot(room, outdoor, sun, band_max, trial) <= target:
                ac_on = trial
                break
    for h in sorted([h for h, on in enumerate(ac_on) if on], key=lambda h: -prices[h]):
        trial = list(ac_on)
        trial[h] = False
        if _hours_too_hot(room, outdoor, sun, band_max, trial) <= target:
            ac_on = trial
    return ac_on


# ---------------------------------------------------------------------------
# 3. SCORECARD
# ---------------------------------------------------------------------------

TOLERANCE = 0.5            # °C over the limit before an hour counts as 'too hot'
PEAK_HOURS = range(16, 21)    # 4pm-9pm evening peak
SOLAR_HOURS = range(10, 15)   # 10am-3pm solar soak


def scorecard(room, temps, ac_on, prices, hours_of_day, band_max):
    """prices in cents per kWh. hours_of_day: clock hour (0-23) for each step."""
    kwh = [room.ac_power_kw if on else 0.0 for on in ac_on]
    total = sum(kwh)
    peak = sum(k for k, h in zip(kwh, hours_of_day) if h in PEAK_HOURS)
    solar = sum(k for k, h in zip(kwh, hours_of_day) if h in SOLAR_HOURS)
    return {
        "Hours too hot": sum(1 for t in temps if t > band_max + TOLERANCE),
        "Hottest indoor °C": round(max(temps), 1),
        "Cooling cost $": round(sum(k * p for k, p in zip(kwh, prices)) / 100, 2),
        "Cooling kWh": round(total, 1),
        "Evening-peak kWh": round(peak, 1),
        "Solar-hours share %": round(100 * solar / total) if total else 0,
    }


def carer_message(name, room_name, temps_no_ac, ac_on, prices, hours_of_day, band_max):
    """Plain-language text a carer could receive."""
    breach = next((i for i, t in enumerate(temps_no_ac) if t > band_max), None)
    if breach is None:
        return f"Good news: {name}'s {room_name.lower()} should stay under {band_max}°C today. No action needed."
    first_on = next((i for i, on in enumerate(ac_on) if on), None)
    msg = (f"Heads up: {name}'s room will pass {band_max}°C at around "
           f"{_clock(hours_of_day[breach])} if nothing changes.")
    if first_on is not None:
        msg += (f" Start cooling at {_clock(hours_of_day[first_on])} while power is "
                f"{prices[first_on]:.0f}c/kWh, so it's already cool before the evening peak.")
    msg += " Keep water nearby and check in on them."
    return msg


def _clock(h):
    h = int(h) % 24
    return f"{h % 12 or 12}{'am' if h < 12 else 'pm'}"


def cooling_blocks(times, ac_on, prices, max_gap=1):
    """Turn the hour-by-hour plan into readable blocks. Blocks on the same day
    separated by <= max_gap off-hours are merged ("cycles on and off").
    times: list of datetimes. Returns a list of dicts like
    {"day": "Sat 4 Jan", "start": "9am", "end": "12pm", "hours": 3,
     "avg_price": 30.0, "in_peak": False}"""
    blocks, i, n = [], 0, len(ac_on)
    while i < n:
        if not ac_on[i]:
            i += 1
            continue
        j = i
        while True:
            nxt = next((k for k in range(j + 1, min(n, j + 2 + max_gap)) if ac_on[k]), None)
            if nxt is None or times[nxt].date() != times[i].date():
                break
            j = nxt
        on_hours = [k for k in range(i, j + 1) if ac_on[k]]
        block_prices = [prices[k] for k in on_hours]
        blocks.append({
            "day": f"{times[i]:%a} {times[i].day} {times[i]:%b}",
            "start": _clock(times[i].hour),
            "end": _clock(times[j].hour + 1),
            "hours": len(on_hours),
            "avg_price": sum(block_prices) / len(block_prices),
            "in_peak": any(times[k].hour in PEAK_HOURS for k in on_hours),
        })
        i = j + 1
    return blocks


# Example time-of-use tariff (c/kWh). REPLACE with a real NSW retailer tariff
# and cite it. Hours 15-20 peak, 7-14 & 21-21 shoulder, rest off-peak.
def example_tou_price(hour):
    if 15 <= hour < 21:
        return 55.0
    if 7 <= hour < 15 or hour == 21:
        return 30.0
    return 20.0
