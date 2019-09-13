
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

from comitup import modemgr

log = logging.getLogger('comitup')

hotspot_config = "/usr/share/comitup/dns/dns-hotspot.conf"
connected_config = "/usr/share/comitup/dns/dns-connected.conf"

pidpath = Path("/var/run/comitup-dns")

callmatrix = {
    ('HOTSPOT',    'pass', "router"):
        (lambda: run_dns, lambda: hotspot_config),
    ('CONNECTING', 'start', "router"):
        (lambda: run_dns, lambda: connected_config),
    ('HOTSPOT',    'pass', "single"):
        (lambda: run_dns, lambda: hotspot_config),
    ('CONNECTING', 'start', "single"):
        (lambda: run_dns, lambda: ""),
}


def kill_dns(ppath, sig):
    try:
        pid = int(pidpath.read_text().strip())
        os.kill(pid, signal.SIGTERM)
        os.waitpid(pid, 0)
    except (ValueError, ProcessLookupError,
            FileNotFoundError, ChildProcessError):
        pass


def run_dns(confpath):
    log.debug("Running dnsmasq using {}".format(confpath))

    kill_dns(pidpath, signal.SIGTERM)

    if os.path.exists(confpath):
        dev = modemgr.get_ap_device().Interface

        cmd = "dnsmasq --conf-file={0} --interface={1}".format(confpath, dev)

        for _ in range(5):
            cp = subprocess.run(cmd.split())
            if cp.returncode == 0:
                break
            time.sleep(.1)


def state_callback(state, action):
    try:
        (fn_fact, svc_fact) = callmatrix[(state, action, modemgr.get_mode())]
    except KeyError:
        return

    fn_fact()(svc_fact())


def callback_target():
    return state_callback
