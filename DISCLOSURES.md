# DISCLOSURES

Everything CoolHead uses, so judges can check our work.

## Data
| What | Source | Notes |
|---|---|---|
| Weather forecast | Open-Meteo Forecast API (open-meteo.com) | Free, no key. Hourly temperature + sunshine. |
| Historical weather | Open-Meteo Historical Weather API | Used for the January 2020 Penrith heatwave replay. |
| Suburb → location | Open-Meteo Geocoding API | |
| Electricity prices | AEMO "Aggregated price and demand data", NSW1 region | Wholesale $/MWh converted to c/kWh, plus a flat 25c/kWh for network/retail charges (an approximation). |
| Time-of-use tariff | EXAMPLE values in `coolhead/model.py` | Replace with a real NSW retailer tariff and cite it here. |

## Assumptions (be upfront about these)
- Room temperatures are **estimates** from a simple room simulation, not sensor readings.
- Room presets (brick, fibro, top-floor) are starting estimates, not measured values.
- Air-con modelled as removing up to 8°C per hour from one room at 1.5 kW.
- Brain-safe limits are **user-set**. Profiles are starting points only. CoolHead is not medical advice.

## Tools
- Python, pandas, matplotlib, Streamlit, pytest
- Streamlit Community Cloud (hosting)

## AI tools
- Claude (Anthropic) helped draft the starter code, tests and documentation. The team reviewed, ran and modified it.
  (Edit this line to describe honestly what your team did.)
