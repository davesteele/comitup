#!/usr/bin/python

import dbus
import dbus.service

import logging

import gobject
from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

import states   # noqa
import nm       # noqa

comitup_path = "/com/github/davesteele/comitup"

comitup_int = "com.github.davesteele.comitup"

log = logging.getLogger('comitup')


com_obj = None

class Comitup(dbus.service.Object):
    def __init__(self):
        bus_name = dbus.service.BusName(comitup_int, bus=dbus.SystemBus())
        dbus.service.Object.__init__(self, bus_name, comitup_path)

    @dbus.service.method(comitup_int, in_signature="", out_signature="")
    def activity(self):
        states.set_activity()

    @dbus.service.method(comitup_int, in_signature="", out_signature="as")
    def candidate_connections(self):
        return nm.get_candidate_connections()

    @dbus.service.method(comitup_int, in_signature="", out_signature="aa{ss}")
    def access_points(self):
        points = [x for x in states.points if x['ssid']]

        return sorted(points, key=lambda x: -float(x['strength']))

    @dbus.service.method(comitup_int, in_signature="", out_signature="ss")
    def state(self):
        return [states.com_state, states.connection]

    @dbus.service.method(comitup_int, in_signature="s", out_signature="")
    def connect(self, ssid):
        pass


def init_state_mgr(*hosts):
    global com_obj

    states.init_states(*hosts)
    com_obj = Comitup()


def main():
    handler = logging.StreamHandler(stream=None)
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

    log.info('starting')

    init_state_mgr('comitup.local', 'comitup-1111.local')
    states.set_state('HOTSPOT')

    print com_obj.access_points()

    loop = gobject.MainLoop()
    loop.run()


if __name__ == '__main__':
    main()
