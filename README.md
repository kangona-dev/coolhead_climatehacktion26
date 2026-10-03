# CoolHead 🧠❄️

**Every heat app tells you it's hot outside. CoolHead tells carers exactly when to cool an older person's room, keeping it under a brain-safe limit at the cheapest hours.**

Built for **Climate Hack-tion 2026: Build for 2035** by **Team Algaerithm** (Justin Lakra, Ujan Pal, Kangona Sinha).

**COP31 priority:** Resilient Cities & Buildings (supporting: Electrification)

🔗 **Live app:** https://coolheadclimatehacktion26-erflpkcon9bpic2ff4u7mf.streamlit.app

> No sensor needed. CoolHead runs on free public weather data, real NSW electricity prices and a real household tariff.

---

## The problem

- Heat is Australia's deadliest natural hazard: **354 heatwave deaths** in coronial records (2001–2018). **69%** of those who died were aged 60+, and **80% of the 244 indoor deaths** were people aged 60+.
- Heat hits the brain. During Adelaide heatwaves, **dementia hospital admissions rose 17.4%** (Hansen et al., 2008).
- Many older people have air-con but don't use it, out of *"fear of an unaffordable electricity bill"*. **88%** of health and social workers surveyed had seen this happen (RMIT, 2017).

## What CoolHead does

1. **Simulates the room.** A small thermal model estimates indoor temperature hour by hour from the outdoor forecast and sunshine. It covers three room types: brick house, fibro/weatherboard and top-floor apartment.
2. **Sets a brain-safe limit.** The default is **26°C**. Above this, UK hot-weather guidance says vulnerable people struggle to cool themselves. Carers can adjust it with the person's GP.
3. **Plans pre-cooling at the cheapest hours.** It cools early, in cheap midday solar-soak hours, so the room stays safe through the expensive 4–8pm peak.
4. **Writes a carer text.** It gives a plain-English message with the exact times to switch the air-con on and off.
5. **Tests cheap upgrades.** It shows how much blinds, draught sealing or ceiling insulation would cut cooling energy, which links to the 2035 building-energy target.

## Proof: replaying a real heatwave

We replayed **Penrith, 3–5 January 2020**. On 4 Jan 2020 Penrith reached 48.9°C, the hottest place on Earth that day. We used real weather and real AEMO NSW prices.

| Top-floor apartment, 26°C limit | Result |
|---|---|
| Peak room temperature | **46°C** with no cooling → **26°C** with CoolHead |
| Hours above the safe limit | **40 h** → **0 h** |
| Energy vs a thermostat set at the limit | **27.0 vs 31.5 kWh (−14%)** |
| Plus ceiling insulation | a further **−17%** energy |

## Data and tools

| Source | Used for |
|---|---|
| [Open-Meteo](https://open-meteo.com) | Forecast, historical weather and suburb lookup |
| [AEMO](https://aemo.com.au) | NSW wholesale price and demand data |
| Origin Energy time-of-use tariff, Endeavour zone (July 2026) | Real household prices: peak 4–8pm, solar soak 10am–2pm (73% cheaper than peak) |
| Python, Streamlit, pandas, matplotlib | App, model and charts |

All sources, assumptions and AI-tool use are listed in [DISCLOSURES.md](DISCLOSURES.md).

## What's in this repo

| File | What it does |
|---|---|
| `coolhead/model.py` | Room simulation, cooling planner, scorecard, carer text and the real tariff |
| `coolhead/data.py` | Downloads weather and electricity prices, and caches copies in `data/` |
| `coolhead/ui.py`, `coolhead/charts.py` | App design: thermal-house hero, plan strip and charts |
| `app.py` | The Streamlit website |
| `backtest.py` | The proof: replays a real heatwave and compares CoolHead with a normal thermostat |
| `tests/test_model.py` | 11 automatic checks |
| `DISCLOSURES.md` | Data sources, assumptions and tools used |
| `GIT.md` | How the team shares code with GitHub |

---

## Run it yourself

You need **Python 3** from [python.org](https://www.python.org/downloads/). On Windows, tick **"Add python.exe to PATH"** when you install it.

> **Windows:** use `py` for every command below. **Mac/Linux:** use `python3` instead.

```bash
# 1. Install the libraries (run inside the folder that contains requirements.txt)
py -m pip install -r requirements.txt

# 2. Check everything works. You should see 11 PASS lines.
py tests/test_model.py

# 3. Run the app. It opens at http://localhost:8501
py -m streamlit run app.py
```

### Run the heatwave replay

```bash
py backtest.py --demo                    # made-up data, no internet needed
py backtest.py                           # real Penrith Jan 2020 weather + AEMO prices
py backtest.py --tou                     # real weather + the Origin household tariff
py backtest.py --room "Top-floor apartment"   # or "Brick house", "Fibro / weatherboard"
```

Each run prints a **PITCH NUMBERS** box. It also saves a chart and a scorecard to `outputs/` (for example `outputs/chart_fibro.png`). To try a different heatwave, change `PLACE`, `START` and `END` at the top of `backtest.py`.

## How it works (plain language)

- **Mini room simulation:** a room slowly follows the outdoor temperature and heats up in the sun. Brick rooms follow slowly; fibro and top-floor rooms follow fast. Air-con pulls the temperature down.
- **Smart cooling plan:** CoolHead finds the first hour the room would get too hot. It switches cooling on at the best-value hour before that: cheap power, but not so early that the coolness leaks away. It repeats until the whole day is safe, then removes any cooling hours that aren't needed.
- **Scorecard:** it compares CoolHead with a thermostat that keeps the person equally safe. It reports cost, energy used in the evening peak, and the share of energy used in solar hours.

## Honest limits

- Room temperatures are **estimates**, not measurements. Next step: calibrate them with a $10 sensor in a 20-home pilot.
- The replay uses wholesale prices plus a flat network charge to approximate a bill. The app uses the real Origin tariff.
- The brain-safe limit is set by the carer. **CoolHead is not medical advice.**
- It needs a home with air-con. Homes without one still get the warning.

## Troubleshooting

| Problem | Fix |
|---|---|
| `python` not found | Use `py` (Windows) or `python3` (Mac). On Windows, reinstall Python and tick "Add to PATH". |
| `ModuleNotFoundError` | You're using a different Python from the one you installed into. On Windows, use `py` for everything. |
| `streamlit` not recognised | Use `py -m streamlit run app.py` |
| `requirements.txt` not found | You're one folder too high. Run `cd coolhead` and try again. |
| Lines start with `>>` / red parse errors | You pasted error text into the terminal. Press Ctrl + C and type only the command. |
| Weather error in the app | Check the suburb spelling and your internet. Saved copies in `data/` are used when offline. |

---

*Team Algaerithm, Climate Hack-tion 2026*
