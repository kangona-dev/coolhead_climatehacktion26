# DISCLOSURES

Everything CoolHead uses, so judges can check our work.

## Data
| What | Source | Notes |
|---|---|---|
| Weather forecast | Open-Meteo Forecast API (open-meteo.com) | Free, no key. Hourly temperature + sunshine. |
| Historical weather | Open-Meteo Historical Weather API | Used for the January 2020 Penrith heatwave replay. |
| Suburb → location | Open-Meteo Geocoding API | |
| Electricity prices | AEMO "Aggregated price and demand data", NSW1 region | Wholesale $/MWh converted to c/kWh, plus a flat 25c/kWh for network/retail charges (an approximation). |
| Time-of-use tariff | Origin Energy, "Domestic time-of-use", residential standing offer, Endeavour Energy distribution zone (covers Penrith / Western Sydney), prices effective 1 July 2026: [price sheet (PDF)](https://www.originenergy.com.au/content/dam/pricing/2026/pricechange/NSW_Resi_Standing_Endeavour_July_2026.pdf) | Used in live mode and `backtest.py --tou`. Peak 4–8pm business days: 46.5718c/kWh (1 Nov–31 Mar), 47.1372c/kWh (1 Apr–31 Oct). Solar soak 10am–2pm every day: 12.3475c/kWh. All other times: 35.6906c/kWh. All incl. GST. The daily supply charge (185.1344c/day) is left out because cooling doesn't change it. Public holidays are treated as business days. Coded in `tou_price()` in `coolhead/model.py`. |

## Assumptions (be upfront about these)
- Room temperatures are **estimates** from a simple room simulation, not sensor readings.
- Room presets (brick, fibro, top-floor) are starting estimates, not measured values.
- Air-con modelled as removing up to 8°C per hour from one room at 1.5 kW.
- One retailer's standing offer is used as a representative NSW tariff; other plans and market offers differ. The heatwave replay uses 2020 wholesale prices plus a flat charge, not a real 2020 bill.
- Brain-safe limits are **user-set**. Profiles are starting points only. CoolHead is not medical advice.

## Tools
- Python, pandas, matplotlib, Streamlit, pytest
- Streamlit Community Cloud (hosting)

## AI tools
- Claude (Anthropic) helped draft the starter code, tests and documentation. The team reviewed, ran and modified it.
  (Edit this line to describe honestly what your team did.)
