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

.ch-hero h1 {{ font-size: 2.6rem; margin: 0 0 .2rem 0; color: {TEXT}; }}
.ch-hero h1 span {{ color: {COOL}; }}
.ch-hero p {{ color: {MUTED}; font-size: 1.05rem; margin: 0 0 1rem 0; max-width: 62ch; }}

.ch-panel {{ background: {PANEL}; border: 1px solid {LINE}; border-radius: 14px; padding: 1.2rem 1.4rem;
            box-shadow: 0 1px 2px rgba(18,38,58,.06); }}
.ch-scene {{ color: {MUTED}; font-size: .92rem; margin-bottom: 1.1rem; }}
.ch-scene b {{ color: {TEXT}; font-weight: 600; }}

/* thermal scale bar: markers sit ON the bar, numbers sit in a row BELOW it (never overlap) */
.ch-scale {{ position: relative; height: 26px; margin: 0 .5rem; }}
.ch-bar {{ position: absolute; top: 6px; left: 0; right: 0; height: 14px; border-radius: 7px;
          background: linear-gradient(90deg, #2B6CB0 0%, #5BC0EB 22%, #3DBF8F 34%, #F2B33D 58%, #E5483D 82%, #A3122F 100%); }}
.ch-dot {{ position: absolute; top: 2px; width: 22px; height: 22px; margin-left: -11px; border-radius: 50%;
          background: {PANEL}; border: 4px solid; box-shadow: 0 1px 3px rgba(0,0,0,.25); }}
.ch-limit {{ position: absolute; top: -4px; height: 34px; border-left: 2px dashed {TEXT}; }}
.ch-ends {{ display: flex; justify-content: space-between; color: {MUTED}; font-size: .72rem; margin: .3rem .5rem 0 .5rem; }}
.ch-legend {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: .6rem; margin-top: 1rem; }}
.ch-leg b {{ display: block; font-family: 'Space Grotesk', sans-serif; font-size: 1.4rem; color: {TEXT}; }}
.ch-leg span {{ color: {MUTED}; font-size: .82rem; }}
.ch-leg i {{ display: inline-block; width: 11px; height: 11px; border-radius: 50%; border: 3px solid;
            margin-right: .35rem; vertical-align: -2px; }}
.ch-leg i.lim {{ border: none; border-left: 2px dashed {TEXT}; border-radius: 0; width: 2px; height: 14px; margin-right: .5rem; }}

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
  .ch-legend, .ch-stats {{ grid-template-columns: repeat(2, 1fr); }}
  .ch-stat:nth-child(3) {{ border-left: none; padding-left: 0; }}
  .ch-plan {{ grid-template-columns: 58px 1fr; }}
  .ch-day {{ font-size: .78rem; }}
  .ch-fix {{ grid-template-columns: 1fr 1fr 44px; }}
}}
</style>
"""

# marker colours on the scale (each also used as its legend swatch)
M_PLAN, M_NONE, M_OUT = COOL, HEAT, "#7A8A9B"


def hero(outdoor_peak, none_peak, plan_peak, band_max, place, period):
    """Title + thermal scale bar. Opens a panel that outcome_row() closes."""
    lo = 18.0
    hi = max(50.0, outdoor_peak + 2, none_peak + 2)

    def pos(t):
        return max(0.0, min(100.0, 100 * (t - lo) / (hi - lo)))

    def dot(t, colour):
        return f'<div class="ch-dot" style="left:{pos(t):.1f}%;border-color:{colour}"></div>'

    def leg(t, label, swatch):
        return f'<div class="ch-leg"><b>{t:.0f}°C</b><span>{swatch}{escape(label)}</span></div>'

    return f"""
<div class="ch-hero">
  <h1>Cool<span>Head</span></h1>
  <p>Simulates the room, plans cooling around a brain-safe limit, and runs the air-con
     at cheaper hours before the evening peak. No sensor needed.</p>
</div>
<div class="ch-panel">
  <div class="ch-scene">Hottest temperatures in <b>{escape(place)}</b>, {escape(period)}</div>
  <div class="ch-scale">
    <div class="ch-bar"></div>
    <div class="ch-limit" style="left:{pos(band_max):.1f}%"></div>
    {dot(outdoor_peak, M_OUT)}
    {dot(none_peak, M_NONE)}
    {dot(plan_peak, M_PLAN)}
  </div>
  <div class="ch-ends"><span>{lo:.0f}°C</span><span>{hi:.0f}°C</span></div>
  <div class="ch-legend">
    {leg(plan_peak, "room with CoolHead", f'<i style="border-color:{M_PLAN}"></i>')}
    {leg(band_max, "brain-safe limit", '<i class="lim"></i>')}
    {leg(none_peak, "room without cooling", f'<i style="border-color:{M_NONE}"></i>')}
    {leg(outdoor_peak, "outdoors", f'<i style="border-color:{M_OUT}"></i>')}
  </div>
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
