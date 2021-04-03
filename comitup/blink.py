"""
blink.py

Add support to blink the green led on a Raspberry pi one time, for a half sec.

https://mlagerberg.gitbooks.io/raspberry-pi/content/5.2-leds.html
"""

import re
import time
from pathlib import Path

brightPath = Path("/sys/class/leds/led0/brightness")
triggerPath = Path("/sys/class/leds/led0/trigger")
modelPath = Path("/sys/firmware/devicetree/base/model")


def onval():
    """A "1" turns on the led, except on a Zero."""
    val = "1"
    if can_blink():
        if "Zero" in modelPath.read_text():
            val = "0"

    return val


def offval():
    """Value to turn the led off."""
    return "0" if onval() == "1" else "1"


def can_blink():
    """ Is this a Pi with a blinkable green led?"""
    if brightPath.exists() and triggerPath.exists():
        return True

    return False


def get_trigger():
    """Save the current led trigger, for later restoration."""
    text = triggerPath.read_text()

    try:
        mode = re.search(r"\[(.+)\]", text).group(1)
    except Exception:
        mode = "none"

    return mode


def set_trigger(trigger):
    """Set the green led trigger."""
    triggerPath.write_text(trigger)


def blink():
    """Blink the green led once."""
    if can_blink():
        oldtrig = get_trigger()

        set_trigger("gpio")
        brightPath.write_text(onval())
        time.sleep(0.5)
        brightPath.write_text(offval())

        set_trigger(oldtrig)


if __name__ == "__main__":
    print(can_blink())
    print(get_trigger())
    blink()
