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
from functools import partial
import threading

import dbus
import NetworkManager
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository.GLib import MainLoop, timeout_add

if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)

if __name__ == '__main__':
    import os
    import sys
    fullpath = os.path.abspath(__file__)
    parentdir = '/'.join(fullpath.split('/')[:-2])
    sys.path.insert(0, parentdir)

from comitup import modemgr  # noqa
from comitup import nm  # noqa
from comitup import config  # noqa

log = logging.getLogger('comitup')

bus = dbus.SystemBus()

monitored_dev = None
ap_device = None
second_device_name = None
wired_device = None
wired_is_connected = False

nm_dev_connect = None
nm_dev_fail = None

PASS_STATES = [
    NetworkManager.NM_DEVICE_STATE_IP_CHECK,
    NetworkManager.NM_DEVICE_STATE_ACTIVATED
]
FAIL_STATES = [NetworkManager.NM_DEVICE_STATE_FAILED]

TIMER_WIRED_PUSH_STATE_S = 5.0  # delay to push eth0 (wired) state

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


def wired_changed_state(state, *args):
    global wired_is_connected

    from comitup.states import set_state

    if state in [NetworkManager.NM_DEVICE_STATE_ACTIVATED, ]:
        wired_is_connected = True
        log.info("nmm - wired CONNECTED")
        set_state('CONNECTED')
    elif state in [NetworkManager.NM_DEVICE_STATE_DISCONNECTED, ]:
        wired_is_connected = False
        set_state('HOTSPOT')
        log.debug("nmm - wired {}".format(state))
    else:
        wired_is_connected = False
        log.debug("nmm - wired {}".format(state))


def ap_changed_state(state, *args):
    if wired_is_connected:
        return

    if state in PASS_STATES:
        log.debug("nmm - primary pass")
        send_cb(nm_dev_connect)
    elif state in FAIL_STATES:
        log.debug("nmm - primary fail")
        send_cb(nm_dev_fail)
    else:
        log.debug("nmm - primary state {}".format(state))


def second_changed_state(state, *args):
    if wired_is_connected:
        return

    if state in PASS_STATES:
        log.debug("nmm - secondary pass")
        send_cb(nm_dev_connect)
    elif state in FAIL_STATES:
        log.debug("nmm - secondary fail")
        send_cb(nm_dev_fail)
    else:
        log.debug("nmm - secondary state {}".format(state))


def any_changed_state(state, *args):
    from comitup import mdns
    from comitup.states import dns_names

    interesting_states = PASS_STATES + FAIL_STATES

    if state in interesting_states:
        mdns.clear_entries()
        mdns.add_hosts(dns_names)


def set_device_listeners(ap_dev, second_dev, wired_dev):
    global ap_device, second_device_name, wired_device

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

    if wired_device is None and wired_dev is not None:
        wired_device = wired_dev
        device_listener = bus.add_signal_receiver(
            wired_changed_state,
            signal_name="StateChanged",
            dbus_interface="org.freedesktop.NetworkManager.Device",
            path=nm.get_device_path(wired_dev)
        )
        log.debug("Listener is {}".format(device_listener))
        # kicks wired state on boot, otherwise wired state is missed
        if wired_device.State == NetworkManager.NM_DEVICE_STATE_ACTIVATED:
            threading.Timer(TIMER_WIRED_PUSH_STATE_S, wired_changed_state, [wired_device.State]).start()

    device_listener = bus.add_signal_receiver(
        any_changed_state,
        signal_name="StateChanged",
        dbus_interface="org.freedesktop.NetworkManager.Device",
        path=None,
    )


def init_nmmon():
    (conf, data) = config.load_data()

    if conf.manage_wired_device:
        wd = nm.get_wired_device()
    else:
        wd = None

    set_device_listeners(
        modemgr.get_ap_device(),
        modemgr.get_link_device(),
        wd,
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
