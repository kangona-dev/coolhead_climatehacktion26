"""HTML building blocks for the app's look. Pure functions returning HTML strings,
so they can be tested without Streamlit."""

from html import escape

from coolhead.model import PEAK_HOURS

# Light "weather instrument" palette. Colour only ever means temperature or price.
BG, PANEL, LINE, TEXT, MUTED = "#EEF3F8", "#FFFFFF", "#D5DFEA", "#12263A", "#5B6F84"
COOL, HEAT, AMBER, SAFE, OFF = "#1B8CC4", "#E5483D", "#E89A1C", "#1F9D74", "#E3EAF2"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
html, body, [class*="css"], .stMarkdown, p, li, label, td, th {{ font-family: 'IBM Plex Sans', sans-serif; }}
h1, h2, h3, .ch-num {{ font-family: 'Space Grotesk', sans-serif !important; letter-spacing: -0.01em; }}
#MainMenu, footer {{ visibility: hidden; }}
.block-container {{ padding-top: 2.2rem; max-width: 860px; }}
h2 {{ font-size: 1.35rem !important; margin-top: 2rem !important; color: {TEXT}; }}

.ch-hero h1 {{ font-size: 3rem; font-weight: 700; margin: 0 0 .2rem 0; color: {TEXT}; }}
.ch-hero h1 span {{ color: {COOL}; }}
.ch-hero p {{ color: {MUTED}; font-size: 1.05rem; margin: 0 0 1rem 0; max-width: 62ch; }}

.ch-panel {{ background: {PANEL}; border: 1px solid {LINE}; border-radius: 14px; padding: 1.2rem 1.4rem;
            box-shadow: 0 1px 2px rgba(18,38,58,.06); }}
.ch-scene {{ color: {MUTED}; font-size: .92rem; margin-bottom: 1.1rem; }}
.ch-scene b {{ color: {TEXT}; font-weight: 600; }}

/* thermal house hero */
.ch-houses {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: .2rem 0 .4rem 0; }}
.ch-house {{ margin: 0; text-align: center; }}
.ch-house svg {{ width: 100%; max-width: 300px; height: auto; display: block; margin: 0 auto; }}
.ch-house figcaption b {{ display: block; font-family: 'Space Grotesk', sans-serif; font-size: 2.3rem;
                         line-height: 1.1; color: {TEXT}; }}
.ch-house figcaption span {{ color: {MUTED}; font-size: .9rem; }}
.ch-house figcaption i {{ display: block; width: 44px; height: 5px; border-radius: 3px; margin: .5rem auto .35rem auto; }}
.ch-limitnote {{ text-align: center; color: {MUTED}; font-size: .85rem; margin-top: .6rem; }}
.ch-limitnote b {{ color: {TEXT}; }}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] label p, [data-testid="stSidebar"] .stMarkdown p {{
  font-family: 'IBM Plex Sans', sans-serif; }}
[data-testid="stSidebar"] h2 {{ font-family: 'Space Grotesk', sans-serif !important; font-size: 1.1rem !important; }}

/* outcome row */
.ch-stats {{ display: grid; grid-template-columns: repeat(4, 1fr); margin-top: 1.1rem; border-top: 1px solid {LINE}; }}
.ch-stat {{ padding: .9rem .6rem 0 .8rem; border-left: 1px solid {LINE}; }}
.ch-stat:first-child {{ border-left: none; padding-left: 0; }}
.ch-stat .ch-num {{ font-size: 1.45rem; color: {TEXT}; display: block; }}
.ch-stat small {{ color: {MUTED}; font-size: .8rem; line-height: 1.35; display: block; }}
.ch-good {{ color: {SAFE} !important; }}

/* text message */
.ch-phone {{ max-width: 460px; }}
.ch-from {{ color: {MUTED}; font-size: .8rem; margin: 0 0 .3rem .2rem; }}
.ch-bubble {{ background: {COOL}; color: #FFFFFF; padding: .8rem 1rem; border-radius: 18px 18px 18px 4px; line-height: 1.5; }}

/* plan strip */
.ch-plan {{ display: grid; grid-template-columns: 88px 1fr; gap: .45rem .8rem; align-items: center; }}
.ch-day {{ color: {TEXT}; font-size: .9rem; }}
.ch-hours {{ display: grid; grid-template-columns: repeat(24, 1fr); gap: 2px; }}
.ch-h {{ height: 26px; border-radius: 3px; background: {OFF}; }}
.ch-h.pk {{ box-shadow: inset 0 -4px 0 rgba(18,38,58,.55); }}
.ch-h.c1 {{ background: {COOL}; }} .ch-h.c2 {{ background: {AMBER}; }} .ch-h.c3 {{ background: {HEAT}; }}
.ch-axis {{ display: grid; grid-template-columns: repeat(4, 1fr); color: {MUTED}; font-size: .72rem; margin-top: .2rem; }}
.ch-key {{ display: flex; flex-wrap: wrap; gap: .4rem 1.2rem; color: {MUTED}; font-size: .8rem; margin-top: .9rem; }}
.ch-key i {{ display: inline-block; width: 12px; height: 12px; border-radius: 3px; margin-right: .35rem; vertical-align: -1px; }}

/* fixes */
.ch-fix {{ display: grid; grid-template-columns: minmax(150px, 1.2fr) 2fr 52px; gap: .8rem; align-items: center; margin: .55rem 0; }}
.ch-fix span {{ color: {TEXT}; font-size: .92rem; }}
.ch-track {{ background: {OFF}; border-radius: 6px; height: 12px; }}
.ch-fill {{ background: {COOL}; border-radius: 6px; height: 12px; }}
.ch-fix b {{ font-family: 'Space Grotesk', sans-serif; color: {TEXT}; text-align: right; }}
.ch-note {{ color: {MUTED}; font-size: .82rem; margin-top: .3rem; }}

@media (max-width: 640px) {{
  .ch-hero h1 {{ font-size: 2.1rem; }}
  .ch-stats {{ grid-template-columns: repeat(2, 1fr); }}
  .ch-house figcaption b {{ font-size: 1.8rem; }}
  .ch-stat:nth-child(3) {{ border-left: none; padding-left: 0; }}
  .ch-plan {{ grid-template-columns: 58px 1fr; }}
  .ch-day {{ font-size: .78rem; }}
  .ch-fix {{ grid-template-columns: 1fr 1fr 44px; }}
}}
</style>
"""

# Thermal-camera colours: the same stops as a heat map, from cool blue to deep red.
THERMAL_STOPS = [(18, (43, 108, 176)), (25, (91, 192, 235)), (29, (61, 191, 143)),
                 (36, (242, 179, 61)), (44, (229, 72, 61)), (50, (163, 18, 47))]


def thermal_colour(t):
    """Temperature (°C) -> hex colour on the thermal scale."""
    if t <= THERMAL_STOPS[0][0]:
        r, g, b = THERMAL_STOPS[0][1]
    elif t >= THERMAL_STOPS[-1][0]:
        r, g, b = THERMAL_STOPS[-1][1]
    else:
        for (t0, c0), (t1, c1) in zip(THERMAL_STOPS, THERMAL_STOPS[1:]):
            if t0 <= t <= t1:
                f = (t - t0) / (t1 - t0)
                r, g, b = (round(a + (bb - a) * f) for a, bb in zip(c0, c1))
                break
    return f"#{r:02X}{g:02X}{b:02X}"


def house_svg(room_kind, room_temp, hot):
    """A building cross-section. The person's room is filled with its thermal colour.
    room_kind: 'apartment' (top floor of a block) or 'house'. hot: draw heat shimmer."""
    fill = thermal_colour(room_temp)
    wall, frame, pale, win = "#F4F7FA", "#5B6F84", "#E3EAF2", "#FFFFFF"
    parts = [f'<line x1="10" y1="160" x2="210" y2="160" stroke="{frame}" stroke-width="2"/>']
    if room_kind == "apartment":
        room_top = 48
        parts.append(f'<rect x="48" y="40" width="124" height="8" rx="2" fill="{frame}"/>')
        parts.append(f'<rect x="52" y="48" width="116" height="112" fill="{wall}" stroke="{frame}" stroke-width="2"/>')
        for y in (86, 123):                       # the two floors below
            parts.append(f'<line x1="52" y1="{y}" x2="168" y2="{y}" stroke="{frame}" stroke-width="2"/>')
            for x in (66, 98, 130):
                parts.append(f'<rect x="{x}" y="{y + 9}" width="22" height="18" rx="2" fill="{pale}"/>')
        room = (54, 50, 112, 35)
    else:
        room_top = 88
        parts.append(f'<polygon points="38,88 110,34 182,88" fill="{wall}" stroke="{frame}" stroke-width="2" stroke-linejoin="round"/>')
        parts.append(f'<rect x="52" y="88" width="116" height="72" fill="{wall}" stroke="{frame}" stroke-width="2"/>')
        room = (54, 90, 112, 68)
    x, y, w, h = room
    gid = f"g{abs(hash((room_kind, round(room_temp, 1), hot))) % 10**6}"
    parts.append(f'<defs><radialGradient id="{gid}" cx="50%" cy="55%" r="70%">'
                 f'<stop offset="0%" stop-color="{fill}" stop-opacity="1"/>'
                 f'<stop offset="100%" stop-color="{fill}" stop-opacity=".72"/></radialGradient></defs>')
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{gid})"/>')
    # a window and a simple bed so it reads as someone's room
    parts.append(f'<rect x="{x + 10}" y="{y + 8}" width="24" height="17" rx="2" fill="{win}" fill-opacity=".55"/>')
    parts.append(f'<rect x="{x + w - 46}" y="{y + h - 13}" width="36" height="9" rx="2" fill="{win}" fill-opacity=".55"/>')
    parts.append(f'<rect x="{x + w - 46}" y="{y + h - 19}" width="9" height="7" rx="2" fill="{win}" fill-opacity=".55"/>')
    if hot:
        for hx in (82, 110, 138):
            top = room_top - (8 if room_kind == "apartment" else 50)
            parts.append(f'<path d="M{hx} {top} q -6 -7 0 -14 t 0 -14" fill="none" stroke="{fill}" '
                         f'stroke-width="3" stroke-linecap="round" opacity=".75"/>')
    return f'<svg viewBox="0 0 220 168" role="img" aria-hidden="true">{"".join(parts)}</svg>'


def hero(outdoor_peak, none_peak, plan_peak, band_max, place, period, room_name="Top-floor apartment"):
    """Title + two thermal houses (without / with CoolHead). Opens a panel that outcome_row() closes."""
    kind = "apartment" if "apartment" in room_name.lower() else "house"

    def figure(temp, caption, hot):
        return (f'<figure class="ch-house">{house_svg(kind, temp, hot)}'
                f'<figcaption><i style="background:{thermal_colour(temp)}"></i>'
                f'<b>{temp:.0f}°C</b><span>{escape(caption)}</span></figcaption></figure>')

    return f"""
<div class="ch-hero">
  <h1>Cool<span>Head</span></h1>
  <p>Simulates the room, plans cooling around a brain-safe limit, and runs the air-con
     at cheaper hours before the evening peak. No sensor needed.</p>
</div>
<div class="ch-panel">
  <div class="ch-scene">Their room in <b>{escape(place)}</b>, {escape(period)},
     when it reached <b>{outdoor_peak:.0f}°C</b> outside</div>
  <div class="ch-houses">
    {figure(none_peak, "without cooling", hot=none_peak > band_max + 0.5)}
    {figure(plan_peak, "with CoolHead", hot=plan_peak > band_max + 0.5)}
  </div>
  <div class="ch-limitnote">Brain-safe limit set by the carer: <b>{band_max:.0f}°C</b></div>
"""


def outcome_row(s_none, s_usual, s_plan):
    """Closes the hero panel: what CoolHead achieved vs a normal thermostat."""
    def stat(value, label, good=False):
        cls = "ch-num ch-good" if good else "ch-num"
        return f'<div class="ch-stat"><span class="{cls}">{value}</span><small>{label}</small></div>'

    cost_u, cost_p = s_usual["Cooling cost $"], s_plan["Cooling cost $"]
    kwh_u, kwh_p = s_usual["Cooling kWh"], s_plan["Cooling kWh"]
    pk_u, pk_p = s_usual["Evening-peak kWh"], s_plan["Evening-peak kWh"]
    return (
        '<div class="ch-stats">'
        + stat(f'{s_plan["Hours too hot"]:.0f} h',
               f'above the safe limit<br>({s_none["Hours too hot"]:.0f} h with no cooling)',
               good=s_plan["Hours too hot"] == 0)
        + stat(f"${cost_p:.2f}", f"cooling cost<br>(thermostat ${cost_u:.2f})", good=cost_p < cost_u - 0.5)
        + stat(f"{kwh_p:.1f} kWh", f"energy used<br>(thermostat {kwh_u:.1f})", good=kwh_p < kwh_u - 0.5)
        + stat(f"{pk_p:.1f} kWh", f"in the 4–9pm peak<br>(thermostat {pk_u:.1f})", good=pk_p < pk_u - 0.5)
        + "</div></div>"   # closes .ch-stats and the hero .ch-panel
    )


def text_message(text, to_name):
    return (f'<div class="ch-phone"><div class="ch-from">Text to {escape(to_name)}\'s carer</div>'
            f'<div class="ch-bubble">{escape(text)}</div></div>')


def price_tier(c):
    """1 = cheap, 2 = normal, 3 = price spike (c/kWh)."""
    return 1 if c <= 35 else (2 if c < 100 else 3)


def plan_strip(times, ac_on, prices):
    """One row of 24 hour-cells per day. Lit cells = air-con on, coloured by price."""
    days = {}
    for t, on, p in zip(times, ac_on, prices):
        days.setdefault(t.date(), {})[t.hour] = (on, p)
    rows = []
    for d, hours in days.items():
        cells = []
        for h in range(24):
            on, p = hours.get(h, (False, 0))
            cls = "ch-h" + (f" c{price_tier(p)}" if on else "") + (" pk" if h in PEAK_HOURS else "")
            tip = f"{h:02d}:00, {p:.0f}c/kWh" + (", cooling" if on else "")
            cells.append(f'<div class="{cls}" title="{tip}"></div>')
        label = f"{d:%a} {d.day} {d:%b}"
        rows.append(f'<div class="ch-day">{label}</div><div class="ch-hours">{"".join(cells)}</div>')
    axis = ('<div></div><div class="ch-axis"><span>12am</span><span>6am</span>'
            '<span>12pm</span><span>6pm</span></div>')
    key = (f'<div class="ch-key"><span><i style="background:{COOL}"></i>cooling, cheap power</span>'
           f'<span><i style="background:{AMBER}"></i>cooling, normal price</span>'
           f'<span><i style="background:{HEAT}"></i>cooling during a price spike</span>'
           f'<span><i style="background:{OFF};box-shadow:inset 0 -3px 0 rgba(18,38,58,.55)"></i>'
           f'underline: 4–9pm peak</span></div>')
    return f'<div class="ch-panel"><div class="ch-plan">{"".join(rows)}{axis}</div>{key}</div>'


def fixes_bars(rows):
    """rows: list of (fix name, % energy saved, cost $)."""
    top = max([r[1] for r in rows] + [1])
    out = []
    for name, pct, cost in rows:
        width = 100 * max(pct, 0) / top
        out.append(f'<div class="ch-fix"><span>{escape(name)}</span>'
                   f'<div class="ch-track"><div class="ch-fill" style="width:{width:.0f}%"></div></div>'
                   f'<b>{pct:.0f}%</b></div>')
    return ('<div class="ch-panel">' + "".join(out)
            + '<div class="ch-note">Cooling energy saved over the same days, with the same safe limit.</div></div>')
