#!/usr/bin/python

import NetworkManager as nm
import argparse
import dbus
import sys
import uuid
import random
import getpass
import tabulate
from functools import wraps


import pprint
pp = pprint.PrettyPrinter(indent=4)


def initialize():
    nm.Settings.ReloadConnections()


def nm_state():
    return nm.NetworkManager.State


def none_on_exception(*exceptions):
    def _none_on_exception(fp):
        @wraps(fp)
        def wrapper(*args, **kwargs):
            try:
                return fp(*args, **kwargs)
            except exceptions:
                return None

        return wrapper

    return _none_on_exception


@none_on_exception(IndexError)
def get_wifi_device():
    return [x for x in nm.NetworkManager.GetDevices() if x.DeviceType == 2][0]


def get_device_path(device=None):
    if not device:
        device = get_wifi_device()

    return device.SpecificDevice().object_path


def get_device_settings(device):
    if not device:
        device = get_wifi_device()

    connection = device.ActiveConnection
    return connection.Connection.GetSettings()


@none_on_exception(AttributeError)
def get_active_ssid(device=None):
    return get_device_settings(device)['802-11-wireless']['ssid']


@none_on_exception(AttributeError, IndexError)
def get_active_ip(device=None):
    if not device:
        device = get_wifi_device()

    return device.Ip4Config.Addresses[0][0]


def get_all_connections():
    return [x for x in nm.Settings.ListConnections()]


@none_on_exception(AttributeError, KeyError)
def get_ssid_from_connection(connection):
    settings = connection.GetSettings()

    return settings['802-11-wireless']['ssid']


def get_connection_by_ssid(name):
    for connection in get_all_connections():
        ssid = get_ssid_from_connection(connection)
        if name == ssid:
            return connection

    return None


def del_connection_by_ssid(name):
    for connection in get_all_connections():
        ssid = get_ssid_from_connection(connection)
        if name == ssid:
            connection.Delete()


def activate_connection_by_ssid(ssid, device=None):
    if not device:
        device = get_wifi_device()

    connection = get_connection_by_ssid(ssid)

    nm.NetworkManager.ActivateConnection(connection, device, '/')


@none_on_exception(AttributeError)
def get_access_points(device=None):
    if not device:
        device = get_wifi_device()

    return device.SpecificDevice().GetAllAccessPoints()


@none_on_exception(IndexError, TypeError)
def get_access_point_by_ssid(ssid, device=None):
    return [x for x in get_access_points(device) if x.Ssid == ssid][0]


def get_candidate_connections(device=None):
    if not device:
        device = get_wifi_device()

    conns = [get_ssid_from_connection(x) for x in get_all_connections()]

    return conns


def make_hotspot(basename='comitup'):
    name = "%s-%d" % (basename, random.randint(1000, 9999))

    settings = {
        'connection':
        {
            'type': '802-11-wireless',
            'uuid': str(uuid.uuid4()),
            'id': name,
            'autoconnect': False,
        },
        '802-11-wireless':
        {
            'mode': 'ap',
            'ssid': name,
        },
        'ipv4':
        {
            'method': 'shared',
        },
        'ipv6':
        {
            'method': 'ignore',
        },
    }

    nm.Settings.AddConnection(settings)


def make_connection_for(point, password=None):

    settings = {
        'connection':
        {
            'id': point.Ssid,
            'type': '802-11-wireless',
            'uuid': str(uuid.uuid4()),
        },
        '802-11-wireless':
        {
            'ssid': point.Ssid,
        },
        'ipv4':
        {
            # assume DHCP
            'method': 'auto',
        },
        'ipv6':
        {
            # assume ipv4-only
            'method': 'ignore',
        },
    }

    # assume privacy = WPA(2) psk
    if point.Flags & 1:
        settings['802-11-wireless']['security'] = '802-11-wireless-security'
        settings['802-11-wireless-security'] = {
            'auth-alg': 'open',
            'key-mgmt': 'wpa-psk',
            'psk': password,
        }

    nm.Settings.AddConnection(settings)


#
# CLI Interface
#


def do_listaccess(arg):
    """List all accessible access points"""
    rows = []
    for point in get_access_points():
        row = (
            point.Ssid, point.HwAddress,
            point.Flags, point.WpaFlags,
            point.RsnFlags, ord(point.Strength),
            point.Frequency
        )
        rows.append(row)

    bypwr = sorted(rows, key=lambda x: -x[5])

    hdrs = ('SSID', 'MAC', 'Private', 'WPA', 'RSN', 'Power', 'Frequency')
    print(tabulate.tabulate(bypwr, headers=hdrs))


def do_listconnections(arg):
    """List all defined connections"""
    for connection in get_all_connections():
        ssid = get_ssid_from_connection(connection)

        if ssid:
            print(ssid)


def do_setconnection(ssid):
    """Connect to a connection"""
    activate_connection_by_ssid(ssid)


def do_getconnection(dummy):
    """Print the active connection ssid"""
    print(get_active_ssid())


def do_getip(dummy):
    """Print the current IP address"""
    print(get_active_ip())


def do_detailconnection(ssid):
    """Print details about a connection"""

    connection = get_connection_by_ssid(ssid)

    pp.pprint(connection.GetSettings())
    pp.pprint(connection.GetSecrets())


def do_delconnection(ssid):
    """Delete a connection id'd by ssid"""

    del_connection_by_ssid(ssid)


def do_makehotspot(dummy):
    """Create a hotspot connection for future use"""

    make_hotspot()


def do_listcandidates(dummy):
    """List available connections for current access points"""

    for candidate in get_candidate_connections():
        print(candidate)


def do_makeconnection(ssid):
    """Create a connection for a visible access point, for future use"""
    point = get_access_point_by_ssid(ssid)

    password = ''
    if point.Flags & 1:
        password = getpass.getpass('password: ')

    make_connection_for(point, password)


def get_command(cmd):
    cmd_name = "do_" + cmd

    try:
        return(globals()[cmd_name])
    except KeyError:
        return None


def parse_args():
    prog = 'comitup'
    epilog = "Commands:\n"
    for x in sorted([x for x in globals().keys() if x[0:3] == "do_"]):
        epilog += "  %s - %s\n" % (x[3:], globals()[x].__doc__)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        prog=prog,
        description="Manage NetworkManager Wifi connections",
        epilog=epilog,
    )

    parser.add_argument(
        'command',
        help="command",
    )

    parser.add_argument(
        'arg',
        nargs='?',
        help="command argument",
    )

    args = parser.parse_args()

    if get_command(args.command) is None:
        parser.error("Invalid command")

    return args


def main():
    try:
        initialize()
    except dbus.exceptions.DBusException:
        print("Must run as root")
        sys.exit(1)

    args = parse_args()
    fn = get_command(args.command)
    fn(args.arg)

if __name__ == '__main__':
    main()
