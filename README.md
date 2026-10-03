# CoolHead – step-by-step guide (for total beginners)

> Every heat app tells you the temperature. **CoolHead simulates your room** and plans cooling
> around your **brain-safe range**, at the cheapest, cleanest hour.
>
> **COP31 priority:** Resilient Cities & Buildings (supporting: Electrification)

No sensor needed. CoolHead uses free public weather and electricity-price data.

---

## What's in this folder

| File | What it does |
|---|---|
| `coolhead/model.py` | The brain of the project: room simulation, cooling planner, scorecard, carer text |
| `coolhead/data.py` | Downloads weather + electricity prices and saves copies in `data/` |
| `backtest.py` | **The proof.** Replays a real heatwave and compares CoolHead with a normal thermostat |
| `app.py` | The website (made with Streamlit) |
| `tests/test_model.py` | 7 automatic checks that the logic works |
| `DISCLOSURES.md` | Every data source, assumption and tool we used |

---

## PART A – Set up your laptop (≈30 min, do this first)

### Step 1. Install Python
1. Go to **python.org/downloads** and download the latest Python 3.
2. **Windows:** when the installer opens, TICK **"Add python.exe to PATH"** at the bottom, then Install.
   **Mac:** just run the installer.

### Step 2. Install VS Code (the program you'll write code in)
Download from **code.visualstudio.com** and install it.

### Step 3. Open the project
1. Unzip the `coolhead` folder somewhere easy, like your Desktop.
2. Open VS Code → **File → Open Folder** → pick the `coolhead` folder.
3. Open a terminal inside VS Code: **Terminal → New Terminal**. A box appears at the bottom.
   This is where you type the commands below. Press Enter after each one.

### Step 4. Install the libraries
First check you're in the right folder: type `dir` (Windows) or `ls` (Mac). You must see
`requirements.txt` listed. If you only see another `coolhead` folder, type `cd coolhead` and check again.

**Windows:**
```
py -m pip install -r requirements.txt
```
**Mac:**
```
python3 -m pip install -r requirements.txt
```

> ⚠️ **Windows users: use `py` for EVERY command in this guide** (e.g. `py backtest.py`,
> `py -m streamlit run app.py`). `python` and `py` can be two different Pythons, and only the
> one you installed into has the libraries. Mac users: use `python3`.
>
> Type or paste **one command at a time**, never error text. If the line starts with `>>`,
> press **Ctrl + C** to get back to the normal prompt.

### Step 5. Check everything works
```
py tests/test_model.py
```
You should see 7 lines starting with `PASS`. 🎉 If so, your setup is done.

---

## PART B – Run the proof (the heatwave replay)

### Step 6. Try it with made-up data first (no internet needed)
```
py backtest.py --demo
```
You'll see a table, and a chart is saved at `outputs/backtest_chart.png`. Open it.

### Step 7. Run it with REAL data
```
py backtest.py
```
This downloads the real Penrith weather for 3–5 January 2020 and real NSW electricity prices.
- Check that the hottest outdoor temperature printed is close to 48–49°C. If not, change the
  `START`/`END` dates at the top of `backtest.py`.
- If it says "Couldn't get AEMO prices", it falls back to the time-of-use tariff. That's OK, but say so in the pitch.
  You can also download the file by hand from AEMO's "Aggregated price and demand data" page
  (NSW, January 2020) and put it in the `data/` folder with its original name.

Try other room types:
```
py backtest.py --room "Brick house"
py backtest.py --room "Top-floor apartment"
```

### Step 8. Write down your numbers
The script prints a **PITCH NUMBERS** box at the end with these worked out for you.
From the table, the headline comparison is **"Usual: thermostat at limit" vs "CoolHead plan"**
(both keep the person safe, so it's a fair comparison). Note:
- Cooling cost $ saved
- Evening-peak kWh saved
- Solar-hours share % increase
- The Cool Room Fixes % savings

**Only use the numbers your real run gives you.** Don't quote the demo numbers in the pitch.

---

## PART C – Run the app

### Step 9. Start the website on your laptop
```
py -m streamlit run app.py
```
A browser tab opens at `http://localhost:8501`. Change the suburb, profile and room in the left sidebar.
To stop it, click the terminal and press **Ctrl + C**.

### Step 10. Share the code and put it online
The team works from one shared copy on GitHub. **Follow `GIT.md`.** It covers publishing the repo,
adding teammates, the daily pull → commit → push loop, and deploying the live app on Streamlit.

---

## PART D – Make it yours (who does what)

| Person | Job |
|---|---|
| Data & model | Steps 6–8. Try different heatwaves and suburbs. Tune the room presets in `ROOM_PRESETS` so they feel realistic, and write down why. |
| Planner & prices | ✅ Done: real NSW tariff (Origin Energy, Endeavour zone, July 2026) in `tou_price()` in `model.py`, cited in `DISCLOSURES.md`. |
| App | Steps 9–10. Make the app look good: larger text, clearer labels, maybe a translated carer message. |
| Kangona (story) | Persona, interviews, evidence for the heat–brain-health link (with citations), the video and the written submission. |

### Easy changes (good first edits)
- **Change the safe-limit presets:** `PROFILES` near the top of `app.py`.
- **Change the carer message wording:** `carer_message` in `coolhead/model.py`.
- **Add a new Cool Room Fix:** add a line to `FIXES` in `coolhead/model.py`.
- **Change the heatwave:** `PLACE`, `START`, `END` at the top of `backtest.py`.

After any change to `model.py`, run `python tests/test_model.py` again to make sure nothing broke.

---

## PART E – Timeline

| When | Do |
|---|---|
| **Fri afternoon** | Part A on every laptop. Steps 6–7. Agree persona + one-line pitch. |
| **Fri night** | Real replay numbers (Step 8). Swap in a real tariff. Start interviews. |
| **Sat** | App running and deployed (Steps 9–10). Polish the carer message and scorecard. Record a backup demo video. |
| **Sat night** | **Submit a first version.** |
| **Sun** | No new features. Fix bugs, final video, written submission, DISCLOSURES. Submit early. |

---

## How it works (plain language for the pitch)

1. **Mini room simulation.** A room slowly follows the outdoor temperature and heats up in the sun.
   Brick rooms follow slowly; fibro and top-floor rooms follow fast. Air-con pulls the temperature down.
2. **Smart cooling plan.** CoolHead finds the first hour the room would get too hot, then switches
   on cooling at the best-value hour just before it (cheap power, but not so early the coolness leaks away).
   It repeats until the whole day is safe, then removes any cooling hours that aren't needed.
3. **Scorecard.** Compares CoolHead with a normal thermostat that keeps the person equally safe:
   cost, energy used in the 4–9pm evening peak, and share of energy used in solar hours (10am–3pm).
4. **Cool Room Fixes.** Re-runs the simulation with blinds, draught sealing or insulation to show
   how much cooling energy each one saves, which is the link to the 2035 building-energy target.

## Be honest about limits (judges respect this)
- Room temperatures are **estimates**, not measurements. Next step: calibrate with a cheap sensor or smart thermostat.
- Electricity prices in the replay are wholesale plus a flat charge, an approximation of a real bill.
- Brain-safe limits are set by the user. **CoolHead is not medical advice.**

## Troubleshooting
| Problem | Fix |
|---|---|
| `python` not found | Use `python3` (Mac) or `py` (Windows). On Windows, reinstall Python and tick "Add to PATH". |
| `ModuleNotFoundError` | You're using a different Python than the one you installed into. On Windows use `py` for everything (`py backtest.py`). |
| `streamlit` not found | `py -m streamlit run app.py` (Windows) or `python3 -m streamlit run app.py` (Mac) |
| Lines start with `>>` / red parse errors | You pasted error text into the terminal. Press Ctrl + C and type just the command. |
| Weather error in app | Check the suburb spelling and your internet. Saved copies in `data/` are used when offline. |
| Anything else | Copy the **whole** red error message and paste it to Claude or a mentor. |
