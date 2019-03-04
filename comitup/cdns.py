
# Copyright (c) 2019 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE
#

import logging
import os
from pathlib import Path
import signal
import subprocess
import time

log = logging.getLogger('comitup')

hotspot_config = "/usr/share/comitup/dns/dns-hotspot.conf"
connected_config = "/usr/share/comitup/dns/dns-connected.conf"

pidpath = Path("/var/run/comitup-dns")

callmatrix = {
    ('HOTSPOT',    'pass'): (lambda: run_dns, lambda: hotspot_config),
    ('CONNECTING', 'start'): (lambda: run_dns, lambda: connected_config),
}


def kill_dns(ppath, sig):
    try:
        pid = int(pidpath.read_text().strip())
        os.kill(pid, signal.SIGTERM)
        os.waitpid(pid, 0)
    except (ValueError, ProcessLookupError, \
            FileNotFoundError, ChildProcessError):
        pass


def run_dns(confpath):
    log.debug("Running dnsmasq using {}".format(confpath))

    kill_dns(pidpath, signal.SIGTERM)

    cmd = "dnsmasq --conf-file={}".format(confpath)

    for _ in range(5):
        cp = subprocess.run(cmd.split())
        if cp.returncode == 0:
            break
        time.sleep(.1)


def state_callback(state, action):
    try:
        (fn_fact, svc_fact) = callmatrix[(state, action)]
    except KeyError:
        return

    if svc_fact():
        fn_fact()(svc_fact())


def callback_target():
    return state_callback
