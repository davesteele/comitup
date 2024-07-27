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
from typing import Callable, List, Optional

import dbus
import NetworkManager
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository.GLib import MainLoop, timeout_add

if __name__ == "__main__":
    DBusGMainLoop(set_as_default=True)

if __name__ == "__main__":
    import os
    import sys

    fullpath = os.path.abspath(__file__)
    parentdir = "/".join(fullpath.split("/")[:-2])
    sys.path.insert(0, parentdir)

from comitup import modemgr  # noqa
from comitup import nm  # noqa

log: logging.Logger = logging.getLogger("comitup")

bus: dbus.SystemBus = dbus.SystemBus()

monitored_dev: Optional[NetworkManager.Device] = None
ap_device: Optional[NetworkManager.Device] = None
second_device_name: Optional[str] = None

nm_dev_connect: Optional[Callable[[], None]] = None
nm_dev_fail: Optional[Callable[[], None]] = None

PASS_STATES: List[int] = [
    # NetworkManager.NM_DEVICE_STATE_IP_CHECK,
    NetworkManager.NM_DEVICE_STATE_ACTIVATED
]
BASE_FAIL_STATES: List[int] = [NetworkManager.NM_DEVICE_STATE_FAILED]
ENHANCED_FAIL_STATES: List[int] = [NetworkManager.NM_DEVICE_STATE_DISCONNECTED]
FAIL_STATES: List[int] = BASE_FAIL_STATES


def base_fail_states() -> None:
    global FAIL_STATES

    FAIL_STATES = BASE_FAIL_STATES


def enhance_fail_states() -> None:
    global FAIL_STATES

    FAIL_STATES = BASE_FAIL_STATES + ENHANCED_FAIL_STATES


def disable() -> None:
    global monitored_dev, nm_dev_connect, nm_dev_fail

    monitored_dev = None

    nm_dev_connect = None
    nm_dev_fail = None


def enable(
    dev: NetworkManager.Device,
    connect_fn: Callable[[], None],
    fail_fn: Callable[[], None],
    state_id: int,
) -> None:
    global monitored_dev, nm_dev_connect, nm_dev_fail

    base_fail_states()

    monitored_dev = None

    nm_dev_connect = partial(connect_fn, state_id)  # type: ignore
    nm_dev_fail = partial(fail_fn, state_id)  # type: ignore

    monitored_dev = dev


def send_cb(cb: Callable[[], None], reason) -> None:
    def cb_to(cb, reason):
        cb(reason)
        return False

    timeout_add(0, cb_to, cb, reason)


def ap_changed_state(state, oldstate, reason, *args) -> None:
    log.debug(
        "nmm - primary state {}, was {}, reason {}".format(
            state, oldstate, reason
        )
    )
    if state in PASS_STATES:
        log.debug("nmm - primary pass")
        if nm_dev_connect:
            send_cb(nm_dev_connect, reason)
    elif state in FAIL_STATES:
        log.debug("nmm - primary fail")
        if nm_dev_fail:
            send_cb(nm_dev_fail, reason)


def second_changed_state(state, oldstate, reason, *args) -> None:
    log.debug(
        "nmm - secondary state {}, was {}, reason {}".format(
            state, oldstate, reason
        )
    )
    if state in PASS_STATES:
        log.debug("nmm - secondary pass")
        if nm_dev_connect:
            send_cb(nm_dev_connect, reason)
    elif state in FAIL_STATES:
        log.debug("nmm - secondary fail")
        if nm_dev_fail:
            send_cb(nm_dev_fail, reason)


def any_changed_state(state: int, *args) -> None:
    from comitup import mdns
    from comitup.states import dns_names

    interesting_states = PASS_STATES + FAIL_STATES

    def reset_mdns():
        mdns.clear_entries()
        mdns.add_hosts(dns_names)

    if state in interesting_states:
        timeout_add(0, reset_mdns)


def set_device_listeners(
    ap_dev: NetworkManager.Device,
    second_dev: NetworkManager.Device,
) -> None:
    global ap_device, second_device_name

    if ap_device is None:
        log.debug("nmm - Setting primary listener for {}".format(ap_dev))
        ap_device = ap_dev
        device_listener = bus.add_signal_receiver(
            ap_changed_state,
            signal_name="StateChanged",
            dbus_interface="org.freedesktop.NetworkManager.Device",
            path=nm.get_device_path(ap_dev),
        )
        log.debug("Listener is {}".format(device_listener))

    if (
        second_device_name != second_dev.Interface
        and ap_dev.Interface != second_dev.Interface
    ):
        log.debug("nmm - Setting 2nd listener for {}".format(second_dev))
        second_device_name = second_dev.Interface
        device_listener = bus.add_signal_receiver(
            second_changed_state,
            signal_name="StateChanged",
            dbus_interface="org.freedesktop.NetworkManager.Device",
            path=nm.get_device_path(second_dev),
        )
        log.debug("Listener is {}".format(device_listener))

    device_listener = bus.add_signal_receiver(
        any_changed_state,
        signal_name="StateChanged",
        dbus_interface="org.freedesktop.NetworkManager.Device",
        path=None,
    )


def init_nmmon() -> None:
    set_device_listeners(modemgr.get_ap_device(), modemgr.get_link_device())


def main():
    handler = logging.StreamHandler(stream=None)
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

    log.info("starting")

    init_nmmon()

    def up():
        print("wifi up")

    def down():
        print("wifi down")

    enable(modemgr.get_ap_device(), up, down)

    loop = MainLoop()
    loop.run()


if __name__ == "__main__":
    main()
