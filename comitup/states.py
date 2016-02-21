#!/usr/bin/python

import logging
import time
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
last_activity = 0

points = []


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


def hotspot_start():
    global conn_list
    log.info("Activating hotspot")

    mdns.clear_entries()
    conn_list = []
    activate_connection(dns_to_conn(dns_names[0]))


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

    if conn_list:
        conn = conn_list.pop(0)
        log.info('Attempting connection to %s' % conn)
        activate_connection(conn)
    else:
        # Give NetworkManager a chance to update the access point list
        nm.deactivate_connection()  # todo - clean this up
        time.sleep(5)
        set_state('HOTSPOT')


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
    global com_state, conn_list, state_id, points

    log.info('Setting state to %s' % state)

    if com_state != 'HOTSPOT':
        points = nm.get_points_ext()

    state_info = state_matrix[state]

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

    nm.activate_connection_by_ssid(connection)


def candidate_connections():
    return nm.get_candidate_connections()


def set_hosts(*args):
    global dns_names
    dns_names = args


def assure_hotspot(ssid):
    if not nm.get_connection_by_ssid(ssid):
        nm.make_hotspot(ssid)


def init_states(*hosts):
    nmmon.init_nmmon()
    set_hosts(*hosts)

    assure_hotspot(dns_to_conn(hosts[0]))


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
