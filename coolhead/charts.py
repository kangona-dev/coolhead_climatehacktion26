"""Static charts for the app (no zooming when people scroll past them)."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

COLOURS = {
    "Outdoor": "#9e9e9e",
    "Room – no cooling": "#d62728",
    "Room – usual thermostat": "#9467bd",
    "Room – CoolHead": "#1f77b4",
}


def room_chart(times, series, band_max):
    """series: dict of name -> list of °C. Returns a matplotlib figure."""
    fig, ax = plt.subplots(figsize=(9, 4))
    lo = min(min(v) for v in series.values()) - 2
    hi = max(max(v) for v in series.values()) + 2
    ax.axhspan(lo, band_max, color="#2ca02c", alpha=0.08)
    ax.axhline(band_max, color="#2ca02c", lw=1.2, ls="--")
    ax.text(times[-1], band_max - 0.6, f"brain-safe limit {band_max}°C  ", color="#2ca02c",
            fontsize=9, ha="right", va="top")
    for name, values in series.items():
        ax.plot(times, values, label=name, color=COLOURS.get(name),
                lw=1.5 if name == "Outdoor" else 2.2,
                ls=":" if name == "Outdoor" else "-")
    ax.set_ylim(lo, hi)
    ax.set_ylabel("°C")
    ax.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 12]))
    # (no "%-I": that format code crashes on Windows)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(
        lambda x, _: (lambda d: f"{d:%a} {d.hour % 12 or 12}{'am' if d.hour < 12 else 'pm'}")(mdates.num2date(x))))
    ax.grid(alpha=0.2)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=4, frameon=False, fontsize=9)
    fig.tight_layout()
    return fig
