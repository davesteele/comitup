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

import NetworkManager
from gi.repository.GLib import timeout_add

from comitup import iwscan, routemgr, wpa

if __name__ == '__main__':
    from dbus.mainloop.glib import DBusGMainLoop
    DBusGMainLoop(set_as_default=True)

from comitup import modemgr  # noqa
from comitup import nm  # noqa
from comitup import nmmon  # noqa

log = logging.getLogger('comitup')

# definitions
dns_names: List[str] = []


# Global state information
com_state: Optional[str] = None
conn_list: List[str] = []
connection: str = ''
state_id: int = 0
startup: bool = False

state_callbacks: List[Callable[[str, str], None]] = []

hotspot_name: str = ""


def state_callback(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        state, action = fn.__name__.split('_')

        log.debug("State call - {}-{}".format(state, action))

        state = state.upper()

        returnvalue = fn(*args, **kwargs)

        call_callbacks(state, action)

        return returnvalue
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


def timeout(fn):
    @wraps(fn)
    def wrapper(id, *args, **kwargs):
        if id == state_id:
            fn(*args, **kwargs)
            return True
        else:
            return False

    return wrapper


def dns_to_conn(host: str) -> str:
    if '.local' in host:
        return host[:-len('.local')]
    else:
        return host


#
# Hotspot state
#

def fake_hs_pass(sid: int) -> bool:
    hotspot_pass(sid, 0)
    return False


@state_callback
def hotspot_start() -> None:
    global conn_list
    log.info("Activating hotspot")

    hs_ssid: str = dns_to_conn(dns_names[0])

    if startup and modemgr.get_mode() == modemgr.SINGLE_MODE:
        log.debug("Passing on hotspot connection for now")
        timeout_add(100, fake_hs_pass, state_id)
    elif hs_ssid != nm.get_active_ssid(modemgr.get_state_device('HOTSPOT')):
        conn_list = []

        activate_connection(hs_ssid, 'HOTSPOT')
    else:
        log.debug("Didn't need to reactivate - already running")
        # the connect callback won't happen - let's 'pass' manually
        timeout_add(100, fake_hs_pass, state_id)


@timeout
@state_callback
def hotspot_pass(reason):
    global startup

    dev = modemgr.get_state_device("CONNECTED")
    conn_list = candidate_connections(dev)
    active_ssid = nm.get_active_ssid(modemgr.get_state_device('CONNECTED'))
    if startup or active_ssid in conn_list:
        set_state("CONNECTING", conn_list)
        startup = False


@timeout
@state_callback
def hotspot_fail(reason):
    log.warning("Hotspot mode failure")
    set_state("HOTSPOT", force=True)


@timeout
def hotspot_timeout():
    if iwscan.ap_conn_count() == 0 or modemgr.get_mode() != 'single':
        log.debug('Periodic connection attempt')

        dev = modemgr.get_state_device('CONNECTED')
        conn_list: List[str] = candidate_connections(dev)
        if conn_list:
            set_state('CONNECTING', conn_list)
        else:
            log.info('No candidates - skipping CONNECTING scan')
    else:
        log.info('AP active - skipping CONNECTING scan')

    wpa.check_wpa(modemgr.get_ap_device().Interface)


#
# Connecting state
#

def fake_cg(sid: int) -> bool:
    connecting_pass(sid, 0)
    return False


@state_callback
def connecting_start():
    global conn_list, connection

    dev = modemgr.get_state_device("CONNECTED")
    full_conn_list = candidate_connections(dev)
    active_ssid = nm.get_active_ssid(modemgr.get_state_device('CONNECTED'))
    if active_ssid in full_conn_list:
        log.debug("Didn't need to connect - already connected")
        connection = active_ssid
        # the connect callback won't happen - let's 'pass' manually
        timeout_add(100, fake_cg, state_id)
    else:
        if conn_list:
            log.debug("states: Calling nm.disconnect()")
            nm.disconnect(modemgr.get_state_device('CONNECTING'))

            conn = conn_list.pop(0)
            log.info('Attempting connection to %s' % conn)
            activate_connection(conn, 'CONNECTING')
        else:
            set_state('HOTSPOT')


@timeout
@state_callback
def connecting_pass(reason):
    log.debug("Connection successful")
    set_state('CONNECTED')


@timeout
@state_callback
def connecting_fail(reason):
    global conn_list

    log.debug("Connection failed - reason {}".format(reason))

    badreasons = [
        NetworkManager.NM_DEVICE_STATE_REASON_NO_SECRETS,
    ]
    if reason in badreasons:
        log.error("Connection {} config failure - DELETING".format(connection))
        nm.del_connection_by_ssid(connection)

    if conn_list:
        set_state('CONNECTING', force=True)
    else:
        set_state('HOTSPOT')


@timeout
def connecting_timeout():
    connecting_fail(state_id)


#
# Connect state
#


@state_callback
def connected_start():
    global conn_list

    conn_list = []


@timeout
@state_callback
def connected_pass(reason):
    pass


@timeout
@state_callback
def connected_fail(reason):
    global startup
    log.warning('Connection lost')

    active_ssid: str = nm.get_active_ssid(modemgr.get_state_device("HOTSPOT"))
    if modemgr.get_mode() == modemgr.MULTI_MODE and not active_ssid:
        log.warning("Hotspot lost while CONNECTED")
        set_state("HOTSPOT")
    else:
        startup = True
        set_state("HOTSPOT")


@timeout
def connected_timeout() -> None:
    log.debug("states: Calling nm.get_active_ssid()")
    active_ssid: str
    active_ssid = nm.get_active_ssid(modemgr.get_state_device('CONNECTED'))
    log.debug("connected_timeout comparing {} to {}".format(
        connection, active_ssid
    ))
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

        defroute_devname = routemgr.defroute_dev()
        ap_dev = modemgr.get_ap_device()
        link_dev = modemgr.get_link_device()
        if defroute_devname == nm.device_name(ap_dev):
            # default route is bad. Disconnect link and count on state
            # processing to restore
            log.error("AP is holding default route while CONNECTED, kicking")
            nm.disconnect(link_dev)


#
# State Management
#


class state_matrix(object):
    """Map e.g. state_matrix('HOTSPOT').pass_fn to the function hotspot_pass"""

    def __init__(self, state):
        self.state = state.lower()

    def __getattr__(self, attr):
        try:
            fname = self.state + '_' + attr[:-3]
            return globals()[fname]
        except KeyError:
            print(attr)
            raise AttributeError


def set_state(state, connections=[], timeout=180, force=False) -> None:
    timeout_add(0, set_state_to, state, connections, timeout, force, state_id)


def set_state_to(state, connections, timeout, force, curr_state_id):
    global com_state, conn_list, state_id

    if state == com_state and not force:
        return False

    if curr_state_id < state_id:
        return False

    log.info('Setting state to %s' % state)

    state_info = state_matrix(state)

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
    timeout_add(timeout*1000, state_info.timeout_fn, state_id)
    state_info.start_fn()

    return False


def activate_connection(name, state):
    global connection
    connection = name
    log.debug('Connecting to %s' % connection)

    path = '/'

    log.debug("states: Calling nm.activate_connection_by_ssid()")
    nm.activate_connection_by_ssid(connection,
                                   modemgr.get_state_device(state),
                                   path=path)


def candidate_connections(device):
    log.debug("states: Calling nm.get_candidate_connections()")
    return nm.get_candidate_connections(device)


def set_hosts(*args):
    global dns_names
    dns_names = args


def hash_conf():
    m = hashlib.sha256()
    with open("/etc/comitup.conf", 'rb') as fp:
        m.update(fp.read())

    return m.hexdigest()[-4:]


def is_hotspot_current(connection):
    hs_filename = nm.get_connection_settings(connection)['connection']['id']

    hs_hash = hs_filename[-4:]

    cf_hash = hash_conf()

    return hs_hash == cf_hash


def assure_hotspot(ssid, device, password):
    log.debug("states: Calling nm.get_connection_by_ssid()")
    nm.del_connection_by_ssid(ssid)
    if not nm.get_connection_by_ssid(ssid):
        nm.make_hotspot(ssid, device, password)


def init_states(
    hosts: List[str],
    callbacks: List[Callable],
    hotspot_pw: str,
):
    global hotspot_name, conn_list, connection, startup

    nmmon.init_nmmon()
    set_hosts(*hosts)

    for callback in callbacks:
        add_state_callback(callback)

    hotspot_name = dns_to_conn(hosts[0])
    assure_hotspot(hotspot_name, modemgr.get_ap_device(), hotspot_pw)

    startup = True
    set_state('HOTSPOT')


def add_state_callback(callback):
    global state_callbacks

    state_callbacks.append(callback)
