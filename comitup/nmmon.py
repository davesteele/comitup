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
from functools import partial
from gi.repository.GLib import MainLoop, timeout_add

from dbus.mainloop.glib import DBusGMainLoop

import logging

if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)

if __name__ == '__main__':
    import os
    import sys
    fullpath = os.path.abspath(__file__)
    parentdir = '/'.join(fullpath.split('/')[:-2])
    sys.path.insert(0, parentdir)

from comitup import nm       # noqa
from comitup import modemgr  # noqa

log = logging.getLogger('comitup')

bus = dbus.SystemBus()

monitored_dev = None
ap_device = None
second_device_name = None

nm_dev_connect = None
nm_dev_fail = None

PASS_STATES = [nm.NM_DEVICE_STATE_IP_CHECK, nm.NM_DEVICE_STATE_ACTIVATED]
FAIL_STATES = [nm.NM_DEVICE_STATE_FAILED]


def disable():
    global monitored_dev, nm_dev_connect, nm_dev_fail

    monitored_dev = None

    nm_dev_connect = None
    nm_dev_fail = None


def enable(dev, connect_fn, fail_fn, state_id):
    global monitored_dev, nm_dev_connect, nm_dev_fail

    monitored_dev = None

    nm_dev_connect = partial(connect_fn, state_id)
    nm_dev_fail = partial(fail_fn, state_id)

    monitored_dev = dev


def send_cb(cb):
    def cb_to(cb):
        cb()
        return False

    timeout_add(1, cb_to, cb)


def ap_changed_state(state, *args):
    if state in PASS_STATES:
        log.debug("nmm - primary pass")
        send_cb(nm_dev_connect)
    elif state in FAIL_STATES:
        log.debug("nmm - primary fail")
        send_cb(nm_dev_fail)
    else:
        log.debug("nmm - primary state {}".format(state))


def second_changed_state(state, *args):
    if state in PASS_STATES:
        log.debug("nmm - secondary pass")
        send_cb(nm_dev_connect)
    elif state in FAIL_STATES:
        log.debug("nmm - secondary fail")
        send_cb(nm_dev_fail)
    else:
        log.debug("nmm - secondary state {}".format(state))


def set_device_listeners(ap_dev, second_dev):
    global ap_device, second_device_name

    if ap_device is None:
        log.debug("nmm - Setting primary listener for {}".format(ap_dev))
        ap_device = ap_dev
        device_listener = bus.add_signal_receiver(
            ap_changed_state,
            signal_name="StateChanged",
            dbus_interface="org.freedesktop.NetworkManager.Device",
            path=nm.get_device_path(ap_dev)
        )
        log.debug("Listener is {}".format(device_listener))

    if second_device_name != second_dev.Interface:
        log.debug("nmm - Setting 2nd listener for {}".format(second_dev))
        second_device_name = second_dev.Interface
        device_listener = bus.add_signal_receiver(
            second_changed_state,
            signal_name="StateChanged",
            dbus_interface="org.freedesktop.NetworkManager.Device",
            path=nm.get_device_path(second_dev)
        )
        log.debug("Listener is {}".format(device_listener))


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
