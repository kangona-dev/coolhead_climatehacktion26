"""Unit tests. Run:  python -m pytest   (or just: python tests/test_model.py)"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coolhead.model import (ROOM_PRESETS, FIXES, simulate, plan_thermostat,
                            plan_coolhead, scorecard, example_tou_price, TOLERANCE)

HOT_DAY_OUT = [24] * 8 + [28, 32, 36, 40, 43, 45, 46, 45, 42, 38, 34, 31, 29, 27, 26, 25]
HOT_DAY_SUN = [0] * 7 + [200, 400, 600, 800, 900, 1000, 900, 800, 600, 400, 200, 50] + [0] * 5
PRICES = [example_tou_price(h) for h in range(24)]
ROOM = ROOM_PRESETS["Fibro / weatherboard"]


def test_room_heats_up_without_ac():
    temps = simulate(ROOM, HOT_DAY_OUT, HOT_DAY_SUN, [False] * 24)
    assert max(temps) > 35


def test_room_lags_behind_outdoor():
    brick = ROOM_PRESETS["Brick house"]
    temps = simulate(brick, HOT_DAY_OUT, HOT_DAY_SUN, [False] * 24)
    assert max(temps) < max(HOT_DAY_OUT)                 # brick dampens the peak
    assert temps.index(max(temps)) > HOT_DAY_OUT.index(max(HOT_DAY_OUT))  # and delays it


def test_ac_never_below_floor():
    temps = simulate(ROOM, HOT_DAY_OUT, HOT_DAY_SUN, [True] * 24)
    assert min(temps[1:]) >= ROOM.ac_floor


def test_coolhead_keeps_room_safe():
    plan = plan_coolhead(ROOM, HOT_DAY_OUT, HOT_DAY_SUN, PRICES, 27)
    temps = simulate(ROOM, HOT_DAY_OUT, HOT_DAY_SUN, plan)
    assert all(t <= 27 + TOLERANCE for t in temps)


def test_coolhead_no_dearer_than_thermostat():
    usual = plan_thermostat(ROOM, HOT_DAY_OUT, HOT_DAY_SUN, 27)
    plan = plan_coolhead(ROOM, HOT_DAY_OUT, HOT_DAY_SUN, PRICES, 27)
    hours = list(range(24))
    s_u = scorecard(ROOM, simulate(ROOM, HOT_DAY_OUT, HOT_DAY_SUN, usual), usual, PRICES, hours, 27)
    s_p = scorecard(ROOM, simulate(ROOM, HOT_DAY_OUT, HOT_DAY_SUN, plan), plan, PRICES, hours, 27)
    assert s_p["Cooling cost $"] <= s_u["Cooling cost $"]


def test_fixes_reduce_heat():
    base = max(simulate(ROOM, HOT_DAY_OUT, HOT_DAY_SUN, [False] * 24))
    for apply_fix in FIXES.values():
        assert max(simulate(apply_fix(ROOM), HOT_DAY_OUT, HOT_DAY_SUN, [False] * 24)) <= base


def test_cool_day_needs_no_ac():
    plan = plan_coolhead(ROOM, [20] * 24, [0] * 24, PRICES, 27)
    assert not any(plan)


def test_cooling_blocks_group_hours():
    from datetime import datetime, timedelta
    from coolhead.model import cooling_blocks
    times = [datetime(2020, 1, 4) + timedelta(hours=h) for h in range(24)]
    ac_on = [9 <= h < 12 or h == 17 for h in range(24)]
    blocks = cooling_blocks(times, ac_on, PRICES)
    assert len(blocks) == 2
    assert (blocks[0]["start"], blocks[0]["end"], blocks[0]["hours"]) == ("9am", "12pm", 3)
    assert blocks[1]["in_peak"] and not blocks[0]["in_peak"]


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
