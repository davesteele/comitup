# Copyright (c) 2022 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE
#

import logging
import os
import signal
import time
from functools import wraps

enabled = False
try:
    import RPi.GPIO as GPIO

    enabled = True
except ModuleNotFoundError:
    pass

from comitup import blink  # noqa
from comitup import config  # noqa
from comitup import nm  # noqa

GPIO_INPUT = 21

log = logging.getLogger("comitup")


def checkenabled(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not enabled:
            return

        (conf, _) = config.load_data()
        if not conf.getboolean("enable_nuke"):
            return

        return fn(*args, **kwargs)

    return wrapper


@checkenabled
def nuke():
    for ssid in nm.get_all_wifi_connection_ssids():
        nm.del_connection_by_ssid(ssid)

    os.kill(os.getpid(), signal.SIGTERM)


def gpio_callback(dummy):
    log.debug("Nuke start event detected")
    process_low_event()


def process_low_event():
    total_time = 3
    check_interval = 0.01

    for _ in range(int(total_time / check_interval)):
        time.sleep(check_interval)
        if GPIO.input(GPIO_INPUT):
            return

    log.warning("Nuke function invoked")

    blink.blink(3)

    nuke()


@checkenabled
def init_nuke():
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(GPIO_INPUT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.add_event_detect(GPIO_INPUT, GPIO.FALLING, gpio_callback, 10)

    # So maybe the pin is already shorted?
    process_low_event()


@checkenabled
def cleanup_nuke():
    GPIO.remove_event_detect(GPIO_INPUT)
    GPIO.setup(GPIO_INPUT, GPIO.IN, pull_up_down=GPIO.PUD_OFF)
