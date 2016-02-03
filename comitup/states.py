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
dns_name = 'comitup.local'
hotspot_name = 'hotspot'


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
    activate_connection(hotspot_name)


def hotspot_pass():
    log.debug("Activating mdns")

    ip = nm.get_active_ip()
    mdns.add_hosts([dns_name], ip)


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
    pass
    # go to HOTSPOT


#
# Connect state
#


def connect_start():
    global conn_list

    ip = nm.get_active_ip()
    mdns.add_hosts([dns_name], ip)

    conn_list = []


def connect_pass():
    pass


def connect_fail():
    log.warn('Connection lost')
    set_state('HOTSPOT')


@timeout
def connect_timeout():
    pass
    # todo - check for valid connection, else go to hotspot


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
                        connect_start,
                        connect_pass,
                        connect_fail,
                        connect_timeout,
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


def timeout_fn():
    state_info = state_matrix[com_state]
    state_info.timeout_fn()


def candidate_connections():
    return nm.get_candidate_connections()


if __name__ == '__main__':
    handler = logging.StreamHandler(stream=None)
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

    log.info("Starting")

    set_state('HOTSPOT')
    # set_state('CONNECTING', candidate_connections())

    nmmon.init_nmmon()

    loop = gobject.MainLoop()
    loop.run()
