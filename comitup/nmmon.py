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
from gi.repository.GLib import MainLoop

from dbus.mainloop.glib import DBusGMainLoop

import logging

if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)

if __name__ == '__main__':
    import os, sys
    fullpath = os.path.abspath(__file__)
    parentdir = '/'.join(fullpath.split('/')[:-2])
    sys.path.insert(0, parentdir)

from comitup import nm       # noqa
from comitup import modemgr  # noqa

log = logging.getLogger('comitup')

bus = dbus.SystemBus()

monitored_dev = None
ap_device = None
second_device = None

nm_dev_connect = None
nm_dev_fail = None


def disable():
    global monitored_dev, nm_dev_connect, nm_dev_fail

    monitored_dev = None

    nm_dev_connect = None
    nm_dev_fail = None


def enable(dev, connect_fn, fail_fn):
    global monitored_dev, nm_dev_connect, nm_dev_fail

    monitored_dev = None

    nm_dev_connect = connect_fn
    nm_dev_fail = fail_fn

    monitored_dev = dev


def ap_changed_state(state, *args):
    if monitored_dev == ap_device:
        # see for device states:
        # https://developer.gnome.org/NetworkManager/stable/spec.html
        # #type-NM_DEVICE_STATE
        if state == 100:
            nm_dev_connect()
        elif state == 120:
            nm_dev_fail()


def second_changed_state(state, *args):
    if monitored_dev == second_device:
        if state == 100:
            nm_dev_connect()
        elif state == 120:
            nm_dev_fail()


def set_device_listeners(ap_dev, second_dev):
    global ap_device, second_device

    ap_device = ap_dev
    device_listener = bus.add_signal_receiver(
        ap_changed_state,
        signal_name="StateChanged",
        dbus_interface="org.freedesktop.NetworkManager.Device",
        path=nm.get_device_path(ap_dev)
    )

    if second_dev != ap_dev:
        second_device = second_dev
        device_listener = bus.add_signal_receiver(
            second_changed_state,
            signal_name="StateChanged",
            dbus_interface="org.freedesktop.NetworkManager.Device",
            path=nm.get_device_path(second_dev)
    )


def init_nmmon():
    set_device_listeners(
        modemgr.get_ap_device(),
        modemgr.get_link_device()
    )


def main():
    handler = logging.StreamHandler(stream=None)
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

    log.info('starting')

    init_nmmon()

    def up():
        print("wifi up")

    def down():
        print("wifi down")

    enable(modemgr.get_ap_device(), up, down)

    loop = MainLoop()
    loop.run()


if __name__ == '__main__':
    main()
