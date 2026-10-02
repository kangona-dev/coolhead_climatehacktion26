"""Static charts for the app (no zooming when people scroll past them)."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

NAVY, PANEL, LINE, TEXT, MUTED = "#0E1B2B", "#15263A", "#26405C", "#E8EEF5", "#93A7BD"

COLOURS = {
    "Outdoor": MUTED,
    "Room – no cooling": "#FF5A4E",
    "Room – usual thermostat": "#B39DDB",
    "Room – CoolHead": "#7FD1F5",
}


def room_chart(times, series, band_max):
    """series: dict of name -> list of °C. Returns a matplotlib figure."""
    fig, ax = plt.subplots(figsize=(9, 3.8))
    fig.patch.set_facecolor(PANEL)
    ax.set_facecolor(PANEL)
    lo = min(min(v) for v in series.values()) - 2
    hi = max(max(v) for v in series.values()) + 2
    ax.axhspan(lo, band_max, color="#4FD1A5", alpha=0.10, lw=0)
    ax.axhline(band_max, color="#4FD1A5", lw=1.2, ls="--")
    ax.text(times[0], band_max + 0.5, f" brain-safe limit {band_max}°C ", color="#4FD1A5",
            fontsize=9, ha="left", va="bottom", zorder=1,
            bbox=dict(facecolor=PANEL, edgecolor="none", pad=1.5))
    for name, values in series.items():
        ax.plot(times, values, label=name, color=COLOURS.get(name),
                lw=1.4 if name == "Outdoor" else (2.6 if name == "Room – CoolHead" else 1.8),
                ls=":" if name == "Outdoor" else "-", zorder=3 if name == "Room – CoolHead" else 2)
    ax.set_ylim(lo, hi)
    ax.set_ylabel("°C", color=MUTED)
    ax.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 12]))
    # (no "%-I": that format code crashes on Windows)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(
        lambda x, _: (lambda d: f"{d:%a} {d.hour % 12 or 12}{'am' if d.hour < 12 else 'pm'}")(mdates.num2date(x))))
    ax.tick_params(colors=MUTED, labelsize=8.5)
    ax.grid(color=LINE, alpha=0.6, lw=0.6)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(LINE)
    leg = ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=4, frameon=False, fontsize=9)
    for t in leg.get_texts():
        t.set_color(TEXT)
    fig.tight_layout()
    return fig
