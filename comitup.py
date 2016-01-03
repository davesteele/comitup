#!/usr/bin/python

import NetworkManager as nm
import argparse
import dbus
import sys
import uuid
import random

import pprint
pp = pprint.PrettyPrinter(indent=4)


def initialize():
    nm.Settings.ReloadConnections()


def get_wifi_device():
    return [x for x in nm.NetworkManager.GetDevices() if x.DeviceType == 2][0]


def get_active_ssid(device=None):
    if not device:
        device = get_wifi_device()

    connection = device.ActiveConnection
    settings = connection.Connection.GetSettings()
    ssid = settings['802-11-wireless']['ssid']

    return ssid


def get_all_connections():
    return [x for x in nm.Settings.ListConnections()]


def get_ssid_from_connection(connection):
    settings = connection.GetSettings()

    try:
        ssid = settings['802-11-wireless']['ssid']
    except KeyError:
        ssid = None

    return ssid


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


def get_access_points(device=None):
    if not device:
        device = get_wifi_device()

    return device.SpecificDevice().GetAllAccessPoints()

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

#
# CLI Interface
#

def do_listaccess(arg):
    """List all accessible access points"""
    for point in get_access_points():
        print "%s %s %d" % (point.Ssid, point.HwAddress, ord(point.Strength))


def do_listconnections(arg):
    """List all defined connections"""
    for connection in get_all_connections():
        ssid = get_ssid_from_connection(connection)

        if ssid:
            print ssid


def do_setconnection(ssid):
    """Connect to a connection"""
    activate_connection_by_ssid(ssid)


def do_getconnection(dummy):
    """Print the active connection ssid"""
    print get_active_ssid()


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
        print "Must run as root"
        sys.exit(1)

    args = parse_args()
    fn = get_command(args.command)
    fn(args.arg)

if __name__ == '__main__':
    main()
