#!/usr/bin/python

#
# Copyright 2016-2017 David Steele <steele@debian.org>
# This file is part of comitup
# Available under the terms of the GNU General Public License version 2
# or later
#

import logging
import time
from functools import wraps
from dbus.exceptions import DBusException
import iwscan


import gobject
if __name__ == '__main__':
    from dbus.mainloop.glib import DBusGMainLoop
    DBusGMainLoop(set_as_default=True)

import nmmon    # noqa
import nm       # noqa
import mdns     # noqa
import modemgr  # noqa


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


@state_callback
def hotspot_start():
    global conn_list
    log.info("Activating hotspot")

    mdns.clear_entries()
    conn_list = []

    # tolerate Raspberry Pi 2
    try:
        activate_connection(dns_to_conn(dns_names[0]), 'HOTSPOT')
    except DBusException:
        log.warn("Error connecting hotspot")


@state_callback
def hotspot_pass():
    log.debug("Activating mdns")

    # IP tolerance for PI 2
    for _ in range(5):
        ip = nm.get_active_ip(modemgr.get_state_device('HOTSPOT'))
        if ip:
            mdns.clear_entries()
            mdns.add_hosts(dns_names)
            break
        time.sleep(1)


@state_callback
def hotspot_fail():
    pass


@timeout
def hotspot_timeout():

    if iwscan.ap_conn_count() == 0 or modemgr.get_mode() != 'single':
        log.debug('Periodic connection attempt')

        conn_list = candidate_connections(modemgr.get_state_device('CONNECTED'))
        if conn_list:
            # bug - try the first connection twice
            set_state('CONNECTING', [conn_list[0], conn_list[0]] + conn_list)
        else:
            set_state('CONNECTING')
    else:
        log.info('AP active - skipping CONNECTING scan')


#
# Connecting state
#


@state_callback
def connecting_start():
    global conn_list

    mdns.clear_entries()

    if conn_list:
        nm.disconnect(modemgr.get_state_device('CONNECTING'))

        conn = conn_list.pop(0)
        log.info('Attempting connection to %s' % conn)
        activate_connection(conn, 'CONNECTING')
    else:
        # Give NetworkManager a chance to update the access point list
        try:
            # todo - clean this up
            nm.deactivate_connection(modemgr.get_state_device('CONNECTING'))
        except DBusException:
            pass
        time.sleep(5)
        set_state('HOTSPOT')


@state_callback
def connecting_pass():
    log.debug("Connection successful")
    set_state('CONNECTED')


@state_callback
def connecting_fail():
    log.debug("Connection failed")
    if conn_list:
        set_state('CONNECTING')
    else:
        set_state('HOTSPOT')


@timeout
def connecting_timeout():
    connecting_fail()


#
# Connect state
#


@state_callback
def connected_start():
    global conn_list

    # IP tolerance for PI 2
    for _ in range(5):
        ip = nm.get_active_ip(modemgr.get_state_device('CONNECTED'))
        if ip:
            mdns.clear_entries()
            mdns.add_hosts(dns_names)
            break
        time.sleep(1)

    conn_list = []


@state_callback
def connected_pass():
    pass


@state_callback
def connected_fail():
    log.warn('Connection lost')
    set_state('HOTSPOT')


@timeout
def connected_timeout():
    if connection != nm.get_active_ssid(modemgr.get_state_device('CONNECTED')):
        log.warn("Connection lost on timeout")
        set_state('HOTSPOT')


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


def set_state(state, connections=None, timeout=60):
    global com_state, conn_list, state_id, points

    log.info('Setting state to %s' % state)

    if com_state != 'HOTSPOT':
        points = nm.get_points_ext(modemgr.get_state_device(com_state))

    state_info = state_matrix(state)

    nmmon.set_device_callbacks(state, state_info.pass_fn, state_info.fail_fn)

    if connections:
        conn_list = connections

    state_id += 1
    com_state = state
    state_info.start_fn()

    gobject.timeout_add(timeout*1000, state_info.timeout_fn, state_id)


def activate_connection(name, state):
    global connection
    connection = name
    log.debug('Connecting to %s' % connection)

    try:
        path = [x['nmpath'] for x in points if x['ssid'] == name][0]
    except IndexError:
        path = '/'

    nm.activate_connection_by_ssid(connection,
                                   modemgr.get_state_device(state),
                                   path=path)


def candidate_connections(device):
    return nm.get_candidate_connections(device)


def set_hosts(*args):
    global dns_names
    dns_names = args


def assure_hotspot(ssid):
    if not nm.get_connection_by_ssid(ssid):
        nm.make_hotspot(ssid)


def init_states(hosts, callbacks):
    global hotspot_name

    nmmon.init_nmmon()
    set_hosts(*hosts)

    for callback in callbacks:
        add_state_callback(callback)

    hotspot_name = dns_to_conn(hosts[0])

    assure_hotspot(hotspot_name)


def add_state_callback(callback):
    global state_callbacks

    state_callbacks.append(callback)


if __name__ == '__main__':
    handler = logging.StreamHandler(stream=None)
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

    log.info("Starting")

    init_states('comitup.local', 'comitup-1111.local')

    set_state('HOTSPOT')
    # set_state('CONNECTING', candidate_connections())

    loop = gobject.MainLoop()
    loop.run()
