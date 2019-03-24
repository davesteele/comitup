#!/usr/bin/python3
# Copyright (c) 2019 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE

import logging
import subprocess
import time

log = logging.getLogger("comitup")

# The AP hotspot is eventually failing. Restarting wpa_supplicant recovers it.
# I haven't found a way to detect that the wpa_supplicant is not working
# properly without involving the outside world.
#
# The minimal workaround fix is to call disconnect, then reconnect from
# wpa_cli.

last_kick_time = 0
kick_period_secs = 5*60


def needs_kick(devstring):
    return (time.time() - kick_period_secs) > last_kick_time


def kick_wpa(devstring):
    global last_kick_time

    log.debug("Kicking wpa on {}".format(devstring))

    for wpa_cmd in ("disconnect", "reconnect"):
        shell_cmd = "/sbin/wpa_cli -i {0} {1}".format(devstring, wpa_cmd)
        subprocess.run(shell_cmd.split())

    last_kick_time = time.time()


def check_wpa(devstring):
    if needs_kick(devstring):
        kick_wpa(devstring)
