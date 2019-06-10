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

import dbus
import dbus.service
import logging
from comitup import iwscan
import os
import re
import socket
import subprocess

import sys
sys.path.append("/usr/share/comitup")

import pkg_resources                          # noqa

from gi.repository.GLib import MainLoop, timeout_add       # noqa
import time                                   # noqa
from dbus.mainloop.glib import DBusGMainLoop  # noqa
DBusGMainLoop(set_as_default=True)

from comitup import states                                 # noqa
from comitup import nm                                     # noqa
from comitup import modemgr                                # noqa

comitup_path = "/com/github/davesteele/comitup"

comitup_int = "com.github.davesteele.comitup"

log = logging.getLogger('comitup')


com_obj = None
conf = None
data = None

apcache = None
cachetime = 0


class Comitup(dbus.service.Object):
    def __init__(self):
        bus_name = dbus.service.BusName(comitup_int, bus=dbus.SystemBus())
        dbus.service.Object.__init__(self, bus_name, comitup_path)

    @dbus.service.method(comitup_int, in_signature="", out_signature="aa{ss}")
    def access_points(self):
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
    def connect(self, ssid, password):
        def to_fn(ssid, password):
            if nm.get_connection_by_ssid(ssid):
                nm.del_connection_by_ssid(ssid)

            nm.make_connection_for(ssid, password)

            states.set_state('CONNECTING', [ssid, ssid])
            return False

        timeout_add(1, to_fn, ssid, password)

    @dbus.service.method(comitup_int, in_signature="", out_signature="")
    def delete_connection(self):
        def to_fn():
            ssid = nm.get_active_ssid(modemgr.get_link_device())
            nm.del_connection_by_ssid(ssid)
            states.set_state('HOTSPOT')
            return False

        timeout_add(1, to_fn)

    @dbus.service.method(comitup_int, in_signature="", out_signature="a{ss}")
    def get_info(self):
        info = {
            'version': pkg_resources.get_distribution("comitup").version,
            'apname': expand_ap(conf.ap_name, data.id),
            'hostnames': ';'.join(get_hosts(conf, data)),
            'imode': modemgr.get_mode(),
            }

        return info


def expand_ap(ap_name, id):
    returnval = ap_name

    for l in range(5):
        returnval = re.sub("<{}>".format("n"*l), id[:l], returnval)

    returnval = re.sub("<hostname>", socket.gethostname(), returnval)

    return returnval


def get_hosts(conf, data):
    return [
        "{}.local".format(expand_ap(conf.ap_name, data.id)),
    ]


def external_callback(state, action):
    if action != 'start':
        return

    script = conf.external_callback

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


def init_state_mgr(gconf, gdata, callbacks):
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
