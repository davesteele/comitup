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


import hashlib
import logging
from functools import wraps
from typing import Callable, List, Optional

import dbus
import NetworkManager
from gi.repository.GLib import timeout_add

from comitup import iwscan, mdns, modemgr, nm, nmmon, routemgr, wpa

log = logging.getLogger("comitup")

# constants
DEFAULT_TIMEOUT = 180  # default time for state timeout functions
FAIL_TIMEOUT = 360  # hotspot timeout after a connecting fail

# Global state information
dns_names: List[str] = []
com_state: Optional[str] = None
conn_list: List[str] = []
connection: str = ""
state_id: int = 0
startup: bool = False

state_callbacks: List[Callable[[str, str], None]] = []

hotspot_name: str = ""


def state_callback(fn: Callable[[int], None]) -> Callable[[int], None]:
    @wraps(fn)
    def wrapper(reason: int) -> None:
        state: str
        action: str
        state, action = fn.__name__.split("_")

        log.debug("State call - {}-{}".format(state, action))

        state = state.upper()

        fn(reason)

        call_callbacks(state, action)

    return wrapper


def call_callbacks(state: str, action: str) -> None:
    if state not in ["HOTSPOT", "CONNECTING", "CONNECTED"]:
        log.debug("Illegal state {}".format(state))

    if action not in ["start", "pass", "fail", "timeout"]:
        log.debug("Illegal action {}".format(action))

    log.debug("Calling callbacks for {}:{}".format(state, action))
    for callback in state_callbacks:
        callback(state, action)
    log.debug("Callbacks complete")


def timeout(fn: Callable[[int], None]) -> Callable[[int, int], bool]:
    @wraps(fn)
    def wrapper(id: int, reason: int) -> bool:
        if id == state_id:
            fn(reason)
            return True
        else:
            return False

    return wrapper


def dns_to_conn(host: str) -> str:
    if ".local" in host:
        return host[: -len(".local")]
    else:
        return host


#
# Hotspot state
#


def fake_hs_pass(sid: int) -> bool:
    hotspot_pass(sid, 0)
    return False


@state_callback
def hotspot_start(dummy: int) -> None:
    global conn_list
    log.info("Activating hotspot")

    if startup:
        mdns.clear_entries()
        mdns.add_hosts(dns_names)

    hs_ssid: str = dns_to_conn(dns_names[0])

    if startup and modemgr.get_mode() == modemgr.SINGLE_MODE:
        log.debug("Passing on hotspot connection for now")
        timeout_add(100, fake_hs_pass, state_id)
    elif hs_ssid != nm.get_active_ssid(modemgr.get_state_device("HOTSPOT")):
        conn_list = []

        log.debug("Activating connection {}".format(hs_ssid))
        activate_connection(hs_ssid, "HOTSPOT")
    else:
        log.debug("Didn't need to reactivate - already running")
        # the connect callback won't happen - let's 'pass' manually
        timeout_add(100, fake_hs_pass, state_id)


@timeout
@state_callback
def hotspot_pass(reason: int) -> None:
    global startup

    dev: NetworkManager.Device = modemgr.get_state_device("CONNECTED")
    conn_list = candidate_connections(dev)
    active_ssid = nm.get_active_ssid(modemgr.get_state_device("CONNECTED"))
    if startup or active_ssid in conn_list:
        set_state("CONNECTING", conn_list)
        startup = False


@timeout
@state_callback
def hotspot_fail(reason: int) -> None:
    log.warning("Hotspot mode failure")
    set_state("HOTSPOT", force=True)


@timeout
def hotspot_timeout(dummy: int) -> None:
    if iwscan.ap_conn_count() == 0 or modemgr.get_mode() != "single":
        log.debug("Periodic connection attempt")

        dev = modemgr.get_state_device("CONNECTED")
        conn_list: List[str] = candidate_connections(dev)
        if conn_list:
            set_state("CONNECTING", conn_list)
        else:
            log.info("No candidates - skipping CONNECTING scan")
    else:
        log.info("AP active - skipping CONNECTING scan")

    wpa.check_wpa(modemgr.get_ap_device().Interface)


#
# Connecting state
#


def fake_cg_pass(sid: int) -> bool:
    connecting_pass(sid, 0)
    return False


@state_callback
def connecting_start(dummy: int) -> None:
    global connection

    dev = modemgr.get_state_device("CONNECTED")
    full_conn_list = candidate_connections(dev)
    active_ssid = nm.get_active_ssid(modemgr.get_state_device("CONNECTED"))
    if active_ssid in full_conn_list:
        log.debug("Didn't need to connect - already connected")
        connection = active_ssid
        # the connect callback won't happen - let's 'pass' manually
        timeout_add(100, fake_cg_pass, state_id)
    else:
        if conn_list:
            log.debug("states: Calling nm.disconnect()")
            nm.disconnect(modemgr.get_state_device("CONNECTING"))

            conn = conn_list.pop(0)
            log.info("Attempting connection to %s" % conn)
            try:
                activate_connection(conn, "CONNECTING")
            except dbus.exceptions.DBusException:
                msg = "DBUS failure connecting to {} - skipping".format(conn)
                log.warning(msg)
                connecting_fail(state_id, 0)
        else:
            set_state("HOTSPOT")


@timeout
@state_callback
def connecting_pass(reason: int) -> None:
    log.debug("Connection successful")
    set_state("CONNECTED")


@timeout
@state_callback
def connecting_fail(reason: int) -> None:
    log.debug("Connection failed - reason {}".format(reason))

    badreasons: List[int] = [
        # NetworkManager.NM_DEVICE_STATE_REASON_NO_SECRETS,  # Disable delete
    ]
    if reason in badreasons:
        log.error("Connection {} config failure - DELETING".format(connection))
        nm.del_connection_by_ssid(connection)

    if conn_list:
        set_state("CONNECTING", force=True)
    else:
        set_state("HOTSPOT", timeout=FAIL_TIMEOUT)


@timeout
def connecting_timeout(dummy: int) -> None:
    connecting_fail(state_id, 0)


#
# Connect state
#


def fake_cn_pass(sid: int) -> bool:
    connected_pass(sid, 0)
    return False


@state_callback
def connected_start(dummy: int) -> None:
    global conn_list

    conn_list = []

    # Connected mode always passes
    timeout_add(100, fake_cn_pass, state_id)


@timeout
@state_callback
def connected_pass(reason: int) -> None:
    pass


@timeout
@state_callback
def connected_fail(reason: int) -> None:
    global startup
    log.warning("Connection lost")

    active_ssid: Optional[str]
    active_ssid = nm.get_active_ssid(modemgr.get_state_device("HOTSPOT"))
    if modemgr.get_mode() == modemgr.MULTI_MODE and not active_ssid:
        log.warning("Hotspot lost while CONNECTED")
        set_state("HOTSPOT")
    else:
        startup = True
        set_state("HOTSPOT")


@timeout
def connected_timeout(dummy: int) -> None:
    active_ssid: Optional[str]
    active_ssid = nm.get_active_ssid(modemgr.get_state_device("CONNECTED"))
    log.debug(
        "connected_timeout comparing {} to {}".format(connection, active_ssid)
    )
    if connection != active_ssid:
        log.warning("Connection lost on timeout")
        dev = modemgr.get_state_device("CONNECTED")
        set_state("CONNECTING", candidate_connections(dev))

    if modemgr.get_mode() == modemgr.MULTI_MODE:
        wpa.check_wpa(modemgr.get_ap_device().Interface)

        active_ssid = nm.get_active_ssid(modemgr.get_state_device("HOTSPOT"))
        if not active_ssid:
            log.warning("Hotspot lost on timeout")
            set_state("HOTSPOT")

        defroute_devname: Optional[str] = routemgr.defroute_dev()
        ap_dev: NetworkManager.Device = modemgr.get_ap_device()
        link_dev: NetworkManager.Device = modemgr.get_link_device()
        if defroute_devname == nm.device_name(ap_dev):
            # default route is bad. Disconnect link and count on state
            # processing to restore
            log.error("AP is holding default route while CONNECTED, kicking")
            nm.disconnect(link_dev)

    # Leave this out for now. Disabling dhcpcd may have fixed the instability
    # problem.
    # mdns.check_mdns(dns_names)


#
# State Management
#


class state_matrix(object):
    """Map e.g. state_matrix('HOTSPOT').pass_fn to the function hotspot_pass"""

    def __init__(self, state: str):
        self.state: str = state.lower()

    def __getattr__(self, attr):
        try:
            fname: str = self.state + "_" + attr[:-3]
            return globals()[fname]
        except KeyError:
            print(attr)
            raise AttributeError


def set_state(
    state: str,
    connections: List[str] = [],
    timeout: int = DEFAULT_TIMEOUT,
    force: bool = False,
) -> None:
    timeout_add(0, set_state_to, state, connections, timeout, force, state_id)


def set_state_to(
    state: str,
    connections: List[str],
    timeout: int,
    force: bool,
    curr_state_id: int,
):
    global com_state, conn_list, state_id

    if state == com_state and not force:
        return False

    if curr_state_id < state_id:
        return False

    log.info("Setting state to %s" % state)

    state_info: state_matrix = state_matrix(state)

    nmmon.init_nmmon()

    state_id += 1

    nmmon.enable(
        modemgr.get_state_device(state),
        state_info.pass_fn,
        state_info.fail_fn,
        state_id,
    )

    if state in ["CONNECTED", "HOTSPOT"]:
        nmmon.enhance_fail_states()

    if connections:
        conn_list = connections

    com_state = state
    timeout_add(timeout * 1000, state_info.timeout_fn, state_id, 0)
    state_info.start_fn(0)

    return False


def activate_connection(name: str, state: str) -> None:
    global connection
    connection = name
    log.debug("Connecting to %s" % connection)

    path = "/"

    nm.activate_connection_by_ssid(
        connection, modemgr.get_state_device(state), path=path
    )


def candidate_connections(device: NetworkManager.Device) -> List[str]:
    return nm.get_candidate_connections(device)


def set_hosts(*args):
    global dns_names
    dns_names = args


def hash_conf() -> str:
    m = hashlib.sha256()
    with open("/etc/comitup.conf", "rb") as fp:
        m.update(fp.read())

    return m.hexdigest()[-4:]


def assure_hotspot(
    ssid: str, device: NetworkManager.Device, password: str
) -> None:
    nm.del_connection_by_ssid(ssid)
    if not nm.get_connection_by_ssid(ssid):
        nm.make_hotspot(ssid, device, password)


def init_states(
    hosts: List[str],
    callbacks: List[Callable[[str, str], None]],
    hotspot_pw: str,
) -> None:
    global hotspot_name, startup

    nmmon.init_nmmon()
    set_hosts(*hosts)

    for callback in callbacks:
        add_state_callback(callback)

    hotspot_name = dns_to_conn(hosts[0])
    assure_hotspot(hotspot_name, modemgr.get_ap_device(), hotspot_pw)

    startup = True
    set_state("HOTSPOT")


def add_state_callback(callback: Callable[[str, str], None]) -> None:
    state_callbacks.append(callback)
