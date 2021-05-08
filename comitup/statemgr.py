#!/usr/bin/python3
# Copyright (c) 2017-2019 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE

#
# Copyright 2016-2017 David Steele <steele@debian.org>
# This file is part of comitup
# Available under the terms of the GNU General Public License version 2
# or later
#

import logging
import os
import re
import socket
import subprocess
import sys
from typing import Dict, List, Optional, TYPE_CHECKING

import dbus
import dbus.service

from comitup import iwscan

if TYPE_CHECKING:
    from comitup.persist import persist
    from comitup.config import Config

sys.path.append("/usr/share/comitup")

import time  # noqa

import pkg_resources  # noqa
from dbus.mainloop.glib import DBusGMainLoop  # noqa
from gi.repository.GLib import MainLoop, timeout_add  # noqa

DBusGMainLoop(set_as_default=True)

from comitup import modemgr  # noqa
from comitup import nm  # noqa
from comitup import states  # noqa

comitup_path: str = "/com/github/davesteele/comitup"

comitup_int: str = "com.github.davesteele.comitup"

log: logging.Logger = logging.getLogger('comitup')


com_obj: Optional["Comitup"] = None
conf: Optional["Config"] = None
data: Optional["persist"] = None

apcache: List[Dict[str, str]] = []
cachetime: float = 0


class Comitup(dbus.service.Object):
    def __init__(self):
        bus_name = dbus.service.BusName(comitup_int, bus=dbus.SystemBus())
        dbus.service.Object.__init__(self, bus_name, comitup_path)

    @dbus.service.method(comitup_int, in_signature="", out_signature="aa{ss}")
    def access_points(self) -> List[Dict[str, str]]:
        global apcache, cachetime

        if time.time() - cachetime > 5:
            cachetime = time.time()   # keep anyone else from processing
            aps = iwscan.candidates()
            aps = [x for x in aps if x['ssid'] != states.hotspot_name]
            apcache = aps

            # set a timeout, if we got something
            if len(apcache):
                cachetime = time.time()   # cache time actually starts now
            else:
                cachetime = 0

        return apcache

    @dbus.service.method(comitup_int, in_signature="", out_signature="ss")
    def state(self):
        return [states.com_state, states.connection]

    @dbus.service.method(comitup_int, in_signature="ss", out_signature="")
    def connect(self, ssid: str, password: str) -> None:
        def to_fn(ssid, password):
            if nm.get_connection_by_ssid(ssid):
                nm.del_connection_by_ssid(ssid)

            nm.make_connection_for(ssid, password)

            states.set_state('CONNECTING', [ssid, ssid])
            return False

        timeout_add(1, to_fn, ssid, password)

    @dbus.service.method(comitup_int, in_signature="", out_signature="")
    def delete_connection(self) -> None:
        def to_fn():
            ssid = nm.get_active_ssid(modemgr.get_link_device())
            nm.del_connection_by_ssid(ssid)
            states.set_state('HOTSPOT')
            return False

        timeout_add(1, to_fn)

    @dbus.service.method(comitup_int, in_signature="", out_signature="a{ss}")
    def get_info(self) -> Dict[str, str]:
        if not conf or not data:
            sys.exit(1)
        return get_info(conf, data)


def get_info(conf: "Config", data: "persist") -> Dict[str, str]:
    if not conf or not data:
        sys.exit(1)

    info = {
        'version': pkg_resources.get_distribution("comitup").version,
        'apname': expand_ap(conf.ap_name, data.id),
        'hostnames': ';'.join(get_hosts(conf, data)),
        'imode': modemgr.get_mode(),
        }

    return info


def expand_ap(ap_name: str, id: str) -> str:
    returnval = ap_name

    for num in range(5):
        returnval = re.sub("<{}>".format("n"*num), id[:num], returnval)

    returnval = re.sub("<hostname>", socket.gethostname(), returnval)

    return returnval


def get_hosts(conf: "Config", data: "persist") -> List[str]:
    return [
        "{}.local".format(expand_ap(conf.ap_name, data.id)),
    ]


def external_callback(state: str, action: str) -> None:
    if action != 'start':
        return

    script = conf.external_callback  # type: ignore

    if not os.path.isfile(script):
        return

    if not os.access(script, os.X_OK):
        log.error("Callback script %s is not executable" % script)
        return

    def demote(uid, gid):
        def dodemote():
            os.setgroups([])
            os.setgid(gid)
            os.setuid(uid)

        return dodemote

    stats = os.stat(script)

    with open(os.devnull, 'w') as nul:
        subprocess.call(
            [script, state],
            stdout=nul,
            stderr=subprocess.STDOUT,
            preexec_fn=demote(stats.st_uid, stats.st_gid),
        )


def init_state_mgr(gconf: "Config", gdata: "persist", callbacks) -> None:
    global com_obj, conf, data

    conf, data = (gconf, gdata)

    states.init_states(
        get_hosts(conf, data),
        callbacks + [external_callback],
        conf.ap_password
    )
    com_obj = Comitup()


def main():
    handler = logging.StreamHandler(stream=None)
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

    log.info('starting')

    init_state_mgr('comitup.local', 'comitup-1111.local')
    states.set_state('HOTSPOT', timeout=5)

    loop = MainLoop()
    loop.run()


if __name__ == '__main__':
    main()
