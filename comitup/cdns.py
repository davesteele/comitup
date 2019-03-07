
# Copyright (c) 2019 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE
#

import logging
import os
from pathlib import Path
import shlex
import signal
import subprocess
import time

if __name__ == '__main__':
    import os, sys
    fullpath = os.path.abspath(__file__)
    parentdir = '/'.join(fullpath.split('/')[:-2])
    sys.path.insert(0, parentdir)

from comitup import modemgr

log = logging.getLogger('comitup')

conf_src = Path("/usr/share/comitup/dns/dns-hotspot.conf")
conf_dst = Path("/etc/NetworkManager/dnsmasq-shared.d/dns-hotspot.conf")

callmatrix = {
    ('HOTSPOT',    'start'): (lambda: kick_dns, True),
    ('CONNECTING', 'start'): (lambda: kick_dns, False),
}


def nm_pid_path():
    dev = modemgr.get_ap_device()
    return Path("/var/run/nm-dnsmasq-{}.pid".format(dev.Interface))


def pid_str(pid_path):
    try:
        return int(pid_path.read_text().strip())
    except (ValueError, FileNotFoundError):
        return None


def command_line(pid):
    cmd = "ps -p {} -o cmd h".format(pid)
    cp = subprocess.run(
                shlex.split(cmd),
                stdout=subprocess.PIPE,
            )

    out = cp.stdout
    if out is None:
        out = ""

    return out.decode().strip()


def proc_info(user, ppath, required_args):
    cp = subprocess.run("ps wwuax".split(), stdout=subprocess.PIPE)

    for line in cp.stdout.decode().split("\n"):
        tokens = line.split()
        try:
            if tokens[0] == user and tokens[10] == ppath \
              and all((x in tokens for x in required_args)):
                cmdline = " ".join(tokens[10:])
                pid = tokens[1]
                return(pid, cmdline)
        except IndexError:
            pass

    return (None, None)


def kill_pid(pid):
    try:
        os.kill(pid, signal.SIGTERM)
        os.waitpid(pid, 0)
    except ChildProcessError:
        pass


def kick_dns(is_hotspot):
    if conf_dst.exists():
        conf_dst.unlink()

    if is_hotspot:
        conf_dst.write_text(conf_src.read_text())

    pid_path = nm_pid_path()
    pid = pid_str(pid_path)

    if pid:
        cmd = command_line(pid)
        kill_pid(pid)

        for _ in range(5):
            p = subprocess.Popen(shlex.split(cmd))
            time.sleep(0.1)
            if p.poll() is None:
                pid_path.write_text(str(p.pid) + "\n")
                break


def state_callback(state, action):
    try:
        (fn_fact, svc_fact) = callmatrix[(state, action)]
    except KeyError:
        return

    fn_fact()(svc_fact)


if __name__ == "__main__":

    # print(nm_pid_path())
    # print(pid_str(nm_pid_path()))
    # print(command_line(pid_str(Path("/var/run/sshd.pid"))))
    # print(command_line(pid_str(Path("/var/run/sshdx.pid"))))
    # print(len(command_line(pid_str(Path("/var/run/sshdx.pid")))))

    if sys.argv[1] == "up":
        kick_dns(True)
    elif sys.argv[1] == "down":
        kick_dns(False)
    else:
        print ("either up or down")


