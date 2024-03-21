# Copyright (c) 2022 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE
#

"""
blink.py

Add support to blink the green led on a Raspberry pi one time, for a half sec.

https://mlagerberg.gitbooks.io/raspberry-pi/content/5.2-leds.html
"""

import re
import time
from pathlib import Path
from typing import List

brightPaths: List[Path] = [
    Path("/sys/class/leds/led0/brightness"),
    Path("/sys/class/leds/ACT/brightness"),
]
triggerPaths: List[Path] = [
    Path("/sys/class/leds/led0/trigger"),
    Path("/sys/class/leds/ACT/trigger"),
]
modelPath: Path = Path("/sys/firmware/devicetree/base/model")


def bright_path():
    try:
        return [x for x in brightPaths if x.exists()][0]
    except IndexError:
        return None


def trigger_path():
    try:
        return [x for x in triggerPaths if x.exists()][0]
    except IndexError:
        return None


def onval() -> str:
    """A "1" turns on the led."""
    return "1"


def offval() -> str:
    """Value to turn the led off."""
    return "0" if onval() == "1" else "1"


def can_blink() -> bool:
    """Is this a Pi with a blinkable green led?"""
    return bright_path() and trigger_path()


def get_trigger() -> str:
    """Save the current led trigger, for later restoration."""
    text: str = trigger_path().read_text()

    match = re.search(r"\[(.+)\]", text)

    mode: str
    if match:
        mode = match.group(1)
    else:
        mode = "none"

    return mode


def set_trigger(trigger: str) -> None:
    """Set the green led trigger."""
    trigger_path().write_text(trigger)


def blink(times: int = 1) -> None:
    """Blink the green led once."""
    if can_blink():
        oldtrig = get_trigger()

        try:
            set_trigger("gpio")
        except OSError:
            set_trigger("input")

        bright_path().write_text(offval())

        for _ in range(times):
            time.sleep(0.25)
            bright_path().write_text(onval())
            time.sleep(0.5)
            bright_path().write_text(offval())
            time.sleep(0.25)

        set_trigger(oldtrig)


if __name__ == "__main__":
    print(can_blink())
    if can_blink():
        print(get_trigger())
        blink(3)
