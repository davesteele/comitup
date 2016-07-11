#!/usr/bin/python

#
# Copyright 2016 David Steele <dsteele@gmail.com>
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


log = logging.getLogger('comitup')

# definitions
dns_names = []


# Global state information
com_state = None
conn_list = []
connection = ''
state_id = 0
last_activity = 0

points = []

state_callbacks = []


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
            if time.time() - last_activity > 60:
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
    activate_connection(dns_to_conn(dns_names[0]))


@state_callback
def hotspot_pass():
    log.debug("Activating mdns")

    ip = nm.get_active_ip()
    mdns.add_hosts(dns_names, ip)


@state_callback
def hotspot_fail():
    pass


@timeout
def hotspot_timeout():

    if iwscan.ap_conn_count() == 0:
        log.debug('Periodic connection attempt')

        conn_list = candidate_connections()
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
        nm.disconnect()

        conn = conn_list.pop(0)
        log.info('Attempting connection to %s' % conn)
        activate_connection(conn)
    else:
        # Give NetworkManager a chance to update the access point list
        try:
            nm.deactivate_connection()  # todo - clean this up
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

    ip = nm.get_active_ip()
    mdns.add_hosts(dns_names, ip)

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
    if connection != nm.get_active_ssid():
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
            print attr
            raise AttributeError


def set_state(state, connections=None):
    global com_state, conn_list, state_id, points

    log.info('Setting state to %s' % state)

    if com_state != 'HOTSPOT':
        points = nm.get_points_ext()

    state_info = state_matrix(state)

    nmmon.set_device_callbacks(state_info.pass_fn, state_info.fail_fn)

    if connections:
        conn_list = connections

    state_id += 1
    com_state = state
    state_info.start_fn()

    gobject.timeout_add(60*1000, state_info.timeout_fn, state_id)


def set_activity():
    global last_activity

    last_activity = time.time()


def activate_connection(name):
    global connection
    connection = name
    log.debug('Connecting to %s' % connection)

    try:
        path = [x['nmpath'] for x in points if x['ssid'] == name][0]
    except IndexError:
        path = '/'

    nm.activate_connection_by_ssid(connection, path=path)


def candidate_connections():
    return nm.get_candidate_connections()


def set_hosts(*args):
    global dns_names
    dns_names = args


def assure_hotspot(ssid):
    if not nm.get_connection_by_ssid(ssid):
        nm.make_hotspot(ssid)


def init_states(hosts, callbacks):
    nmmon.init_nmmon()
    set_hosts(*hosts)

    for callback in callbacks:
        add_state_callback(callback)

    assure_hotspot(dns_to_conn(hosts[0]))


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
