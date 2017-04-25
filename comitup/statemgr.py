#!/usr/bin/python

#
# Copyright 2016-2017 David Steele <steele@debian.org>
# This file is part of comitup
# Available under the terms of the GNU General Public License version 2
# or later
#

import dbus
import dbus.service
import logging
import iwscan

import sys
sys.path.append("/usr/share/comitup")

import pkg_resources # noqa

import gobject                               # noqa
from dbus.mainloop.glib import DBusGMainLoop # noqa
DBusGMainLoop(set_as_default=True)

import states   # noqa
import nm       # noqa

comitup_path = "/com/github/davesteele/comitup"

comitup_int = "com.github.davesteele.comitup"

log = logging.getLogger('comitup')


com_obj = None
conf = None
data = None


class Comitup(dbus.service.Object):
    def __init__(self):
        bus_name = dbus.service.BusName(comitup_int, bus=dbus.SystemBus())
        dbus.service.Object.__init__(self, bus_name, comitup_path)

    @dbus.service.method(comitup_int, in_signature="", out_signature="as")
    def candidate_connections(self):
        return nm.get_candidate_connections()

    @dbus.service.method(comitup_int, in_signature="", out_signature="aa{ss}")
    def access_points(self):
        return iwscan.candidates()

    @dbus.service.method(comitup_int, in_signature="", out_signature="ss")
    def state(self):
        return [states.com_state, states.connection]

    @dbus.service.method(comitup_int, in_signature="ss", out_signature="")
    def connect(self, ssid, password):
        if nm.get_connection_by_ssid(ssid):
            nm.del_connection_by_ssid(ssid)

        nm.make_connection_for(ssid, password)

        states.set_state('CONNECTING', [ssid, ssid])

    @dbus.service.method(comitup_int, in_signature="", out_signature="")
    def delete_connection(self):
        nm.del_connection_by_ssid(nm.get_active_ssid())
        states.set_state('HOTSPOT')

    @dbus.service.method(comitup_int, in_signature="", out_signature="a{ss}")
    def get_info(self):
        info = {
            'version': pkg_resources.get_distribution("comitup").version,
            'basename': conf.base_name,
            'id': data.id,
            'hostnames': ';'.join(get_hosts(conf, data)),
            }

        return info


def get_hosts(conf, data):
    return [
        "%s-%s.local" % (conf.base_name, data.id),
    ]


def init_state_mgr(gconf, gdata, callbacks):
    global com_obj, conf, data

    conf, data = (gconf, gdata)

    states.init_states(get_hosts(conf, data), callbacks)
    com_obj = Comitup()

    states.set_state('HOTSPOT')


def main():
    handler = logging.StreamHandler(stream=None)
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

    log.info('starting')

    init_state_mgr('comitup.local', 'comitup-1111.local')
    states.set_state('HOTSPOT')

    loop = gobject.MainLoop()
    loop.run()


if __name__ == '__main__':
    main()
