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


from functools import wraps
import hashlib
import logging
import time

from comitup import iwscan
from comitup import wpa

from gi.repository.GLib import MainLoop, timeout_add
if __name__ == '__main__':
    from dbus.mainloop.glib import DBusGMainLoop
    DBusGMainLoop(set_as_default=True)

from comitup import nmmon    # noqa
from comitup import nm       # noqa
from comitup import mdns     # noqa
from comitup import modemgr  # noqa


log = logging.getLogger('comitup')

# definitions
dns_names = []


# Global state information
com_state = None
conn_list = []
connection = ''
state_id = 0

points = []

state_callbacks = []

hotspot_name = None


def state_callback(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        returnvalue = fn(*args, **kwargs)

        state, action = fn.__name__.split('_')

        state = state.upper()

        for callback in state_callbacks:
            callback(state, action)

        return returnvalue
    return wrapper


def timeout(fn):
    @wraps(fn)
    def wrapper(id):
        if id == state_id:
            fn()
            return True
        else:
            return False

    return wrapper


def dns_to_conn(host):
    if '.local' in host:
        return host[:-len('.local')]
    else:
        return host


#
# Hotspot state
#

def fake_hs_pass(sid):
    hotspot_pass(sid)
    return False


@state_callback
def hotspot_start():
    global conn_list
    log.info("Activating hotspot")

    hs_ssid = dns_to_conn(dns_names[0])

    log.debug("states: Calling nm.get_active_ssid()")
    if hs_ssid != nm.get_active_ssid(modemgr.get_state_device('HOTSPOT')):
        mdns.clear_entries()
        conn_list = []

        activate_connection(hs_ssid, 'HOTSPOT')
    else:
        log.debug("Didn't need to reactivate - already running")
        # the connect callback won't happen - let's 'pass' manually
        timeout_add(100, fake_hs_pass, state_id)


@timeout
@state_callback
def hotspot_pass():
    log.debug("Activating mdns")

    # IP tolerance for PI 2
    for _ in range(5):
        log.debug("states: Calling nm.get_active_ip()")
        ip = nm.get_active_ip(modemgr.get_state_device('HOTSPOT'))
        if ip:
            mdns.clear_entries()
            mdns.add_hosts(dns_names)
            break
        time.sleep(1)


@timeout
@state_callback
def hotspot_fail():
    log.warning("Hotspot mode failure")
    pass


@timeout
def hotspot_timeout():
    if iwscan.ap_conn_count() == 0 or modemgr.get_mode() != 'single':
        log.debug('Periodic connection attempt')

        dev = modemgr.get_state_device('CONNECTED')
        conn_list = candidate_connections(dev)
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


@state_callback
def connecting_start():
    global conn_list

    mdns.clear_entries()

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
def connecting_pass():
    log.debug("Connection successful")
    set_state('CONNECTED')


@timeout
@state_callback
def connecting_fail():
    log.debug("Connection failed")
    if conn_list:
        set_state('CONNECTING')
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

    # IP tolerance for PI 2
    for _ in range(5):
        log.debug("states: Calling nm.get_active_ip()")
        ip = nm.get_active_ip(modemgr.get_state_device('CONNECTED'))
        if ip:
            mdns.clear_entries()
            mdns.add_hosts(dns_names)
            break
        time.sleep(1)

    conn_list = []


@timeout
@state_callback
def connected_pass():
    pass


@timeout
@state_callback
def connected_fail():
    log.warning('Connection lost')
    set_state('HOTSPOT')
    timeout_add(5*1000, hotspot_timeout, state_id)


@timeout
def connected_timeout():
    log.debug("states: Calling nm.get_active_ssid()")
    if connection != nm.get_active_ssid(modemgr.get_state_device('CONNECTED')):
        log.warning("Connection lost on timeout")
        set_state('HOTSPOT')

    if modemgr.get_mode() == modemgr.MULTI_MODE:
        wpa.check_wpa(modemgr.get_ap_device().Interface)


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


def set_state(state, connections=None, timeout=180):
    global com_state, conn_list, state_id, points

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

    if connections:
        conn_list = connections

    com_state = state
    timeout_add(timeout*1000, state_info.timeout_fn, state_id)
    state_info.start_fn()


def activate_connection(name, state):
    global connection
    connection = name
    log.debug('Connecting to %s' % connection)

    try:
        path = [x['nmpath'] for x in points if x['ssid'] == name][0]
    except IndexError:
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


def assure_hotspot(ssid, device, password):
    log.debug("states: Calling nm.get_connection_by_ssid()")
    nm.del_connection_by_ssid(ssid)
    if not nm.get_connection_by_ssid(ssid):
        nm.make_hotspot(ssid, device, password)


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


def init_states(hosts, callbacks, hotspot_pw):
    global hotspot_name

    nmmon.init_nmmon()
    set_hosts(*hosts)

    for callback in callbacks:
        add_state_callback(callback)

    hotspot_name = dns_to_conn(hosts[0])
    assure_hotspot(hotspot_name, modemgr.get_ap_device(), hotspot_pw)

    # Set an early kick to set CONNECTING mode
    set_state('HOTSPOT')
    timeout_add(5*1000, hotspot_timeout, state_id)


def add_state_callback(callback):
    global state_callbacks

    state_callbacks.append(callback)


if __name__ == '__main__':
    handler = logging.StreamHandler(stream=None)
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

    log.info("Starting")

    init_states('comitup.local', 'comitup-1111.local', "")

    set_state('HOTSPOT')
    # set_state('CONNECTING', candidate_connections())

    loop = MainLoop()
    loop.run()
