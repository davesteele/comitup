#!/usr/bin/python

import logging
from functools import wraps
from collections import namedtuple

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


def timeout(fn):
    @wraps(fn)
    def wrapper(id):
        if id == state_id:
            fn()
            return True
        else:
            return False

    return wrapper

#
# Hotspot state
#


def hotspot_start():
    global conn_list
    log.info("Activating hotspot")

    mdns.clear_entries()
    conn_list = []
    activate_connection(dns_names[0])


def hotspot_pass():
    log.debug("Activating mdns")

    ip = nm.get_active_ip()
    mdns.add_hosts(dns_names, ip)


def hotspot_fail():
    pass


@timeout
def hotspot_timeout():
    log.debug('Periodic connection attempt')

    set_state('CONNECTING', candidate_connections())


#
# Connecting state
#


def connecting_start():
    global conn_list

    mdns.clear_entries()

    conn = conn_list.pop(0)
    log.info('Attempting connection to %s' % conn)
    activate_connection(conn)


def connecting_pass():
    log.debug("Connection successful")
    set_state('CONNECTED')


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


def connected_start():
    global conn_list

    ip = nm.get_active_ip()
    mdns.add_hosts(dns_names, ip)

    conn_list = []


def connected_pass():
    pass


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

StateInfo = namedtuple('StateInfo', "start_fn, pass_fn, fail_fn, timeout_fn")

state_matrix = {
    'HOTSPOT':      StateInfo(
                        hotspot_start,
                        hotspot_pass,
                        hotspot_fail,
                        hotspot_timeout,
                    ),
    'CONNECTING':   StateInfo(
                        connecting_start,
                        connecting_pass,
                        connecting_fail,
                        connecting_timeout,
                    ),
    'CONNECTED':    StateInfo(
                        connected_start,
                        connected_pass,
                        connected_fail,
                        connected_timeout,
                    ),
}


def set_state(state, connections=None):
    global com_state, conn_list, state_id

    log.info('Setting state to %s' % state)

    state_info = state_matrix[state]

    nmmon.set_device_callbacks(state_info.pass_fn, state_info.fail_fn)

    if connections:
        conn_list = connections

    state_id += 1
    com_state = state
    state_info.start_fn()

    gobject.timeout_add(60*1000, state_info.timeout_fn, state_id)


def activate_connection(name):
    global connection
    connection = name
    log.debug('Connecting to %s' % connection)

    nm.activate_connection_by_ssid(connection)


def candidate_connections():
    return nm.get_candidate_connections()


def sethosts(*args):
    global dns_names
    dns_names = args


if __name__ == '__main__':
    handler = logging.StreamHandler(stream=None)
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

    log.info("Starting")

    set_hosts('comitup', 'comitup-1111')

    set_state('HOTSPOT')
    # set_state('CONNECTING', candidate_connections())

    nmmon.init_nmmon()

    loop = gobject.MainLoop()
    loop.run()
