# Copyright (c) 2019 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE
#

import logging
import os
import signal
import subprocess
import time
from pathlib import Path

from comitup import modemgr

log = logging.getLogger("comitup")

hotspot_config: str = "/usr/share/comitup/dns/dns-hotspot.conf"
connected_config: str = "/usr/share/comitup/dns/dns-connected.conf"

pidpath: Path = Path("/var/run/comitup-dns")

callmatrix = {
    ("HOTSPOT", "pass", "router"): (lambda: run_dns, lambda: hotspot_config),
    ("CONNECTING", "start", "router"): (
        lambda: run_dns,
        lambda: connected_config,
    ),
    ("HOTSPOT", "pass", "single"): (lambda: run_dns, lambda: hotspot_config),
    ("CONNECTING", "start", "single"): (lambda: run_dns, lambda: ""),
}


def kill_dns(ppath: Path, sig: int) -> None:
    try:
        pid: int = int(pidpath.read_text().strip())
        os.kill(pid, sig)
        os.waitpid(pid, 0)
    except (
        ValueError,
        ProcessLookupError,
        FileNotFoundError,
        ChildProcessError,
    ):
        pass


def run_dns(confpath: str) -> None:
    log.debug("Running dnsmasq using {}".format(confpath))

    kill_dns(pidpath, signal.SIGTERM)

    if os.path.exists(confpath):
        dev = modemgr.get_ap_device().Interface

        cmd = "dnsmasq --conf-file={0} --interface={1}".format(confpath, dev)

        for _ in range(5):
            cp = subprocess.run(cmd.split())
            if cp.returncode == 0:
                break
            time.sleep(0.1)


def state_callback(state: str, action: str) -> None:
    try:
        (fn_fact, svc_fact) = callmatrix[(state, action, modemgr.get_mode())]
    except KeyError:
        return

    fn_fact()(svc_fact())
