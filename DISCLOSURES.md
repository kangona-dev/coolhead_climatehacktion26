# DISCLOSURES

Everything CoolHead uses, so judges can check our work.

## Data
| What | Source | Notes |
|---|---|---|
| Weather forecast | Open-Meteo Forecast API (open-meteo.com) | Free, no key. Hourly temperature and sunshine. |
| Historical weather | Open-Meteo Historical Weather API | Used for the January 2020 Penrith heatwave replay. |
| Suburb → location | Open-Meteo Geocoding API | Limited to Australia, preferring NSW. |
| Electricity prices | AEMO "Aggregated price and demand data", NSW1 region | Wholesale $/MWh converted to c/kWh, plus a flat 25c/kWh for network and retail charges (an approximation). Times are converted from NEM time to Sydney time. |
| Time-of-use tariff | Origin Energy, "Domestic time-of-use", residential standing offer, Endeavour Energy distribution zone (covers Penrith and Western Sydney), prices effective 1 July 2026: [price sheet (PDF)](https://www.originenergy.com.au/content/dam/pricing/2026/pricechange/NSW_Resi_Standing_Endeavour_July_2026.pdf) | Used in live mode and `backtest.py --tou`. Peak 4–8pm business days: 46.5718c/kWh (1 Nov–31 Mar) and 47.1372c/kWh (1 Apr–31 Oct). Solar soak 10am–2pm every day: 12.3475c/kWh, which is about 73% cheaper than peak. All other times: 35.6906c/kWh. All prices include GST. The daily supply charge (185.1344c/day) is left out because cooling doesn't change it. Public holidays are treated as business days. Coded in `tou_price()` in `coolhead/model.py`. |

## Research behind the pitch
| Claim | Source |
|---|---|
| 354 heatwave deaths 2001–2018; 69% aged 60+; 80% of the 244 indoor deaths aged 60+ | *Heatwave fatalities in Australia, 2001–2018: an analysis of coronial records* (2021) |
| Dementia admissions +17.4% and mental-health admissions +7.3% during heatwaves; admissions rise above 26.7°C **outdoor** temperature | Hansen et al., *Environmental Health Perspectives* (2008), Adelaide |
| Youth mental-health admission risk 2× on the hottest days (3× in cooler months) | University of Sydney, *JAACAP* (2026), 720,000 NSW admissions 2001–2022 |
| 88% of health and social professionals aware of households going without cooling; "fear of an unaffordable electricity bill" | RMIT, *Heatwaves, homes and health* (2017), 36 households and 70 professionals |
| 439,000 Australians with dementia (2025), 1.05 million by 2065; 1 in 4 people aged 65+ living at home live alone | AIHW, *Dementia in Australia*; AIHW, *Older Australians* (2016 Census) |
| Penrith 48.9°C on 4 Jan 2020, hottest place on Earth that day | Bureau of Meteorology, as reported by SBS |
| Western Sydney about 5°C hotter than the coast on 1 in 10 summer days | Western Sydney heat research, *The Conversation* |
| 26°C default brain-safe limit | UK Government, *Supporting vulnerable people before and during hot weather* (social care guidance): vulnerable people find it hard to cool down above 26°C |
| WHO sets no maximum indoor temperature | WHO, *Housing and health guidelines* (2018) |

## Assumptions (be upfront about these)
- Room temperatures are **estimates** from a simple room simulation, not sensor readings.
- The room presets (brick, fibro, top-floor) are starting estimates, not measured values.
- Air-con is modelled as removing up to 8°C per hour from one room, using 1.5 kW.
- One retailer's standing offer stands in for a typical NSW tariff. Other plans and market offers differ.
- The heatwave replay uses 2020 wholesale prices plus a flat charge, not a real 2020 bill.
- Brain-safe limits are **set by the user**. The 26°C default for older adults, people with dementia and people on heat-sensitive medication comes from the UK guidance above. The "Teen / young adult" (28°C) and "Custom" (27°C) presets are our own starting points and have no published source. `backtest.py` uses 27°C by default.
- CoolHead is not medical advice.

## Tools
- Python, pandas, numpy, requests, matplotlib, Streamlit, pytest
- Streamlit Community Cloud (hosting)
- GitHub (version control)

## AI tools
- **Claude (Anthropic)** helped write the starter code, fix bugs, and draft the README.

