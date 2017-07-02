#!/usr/bin/python

#
# Copyright 2016-2017 David Steele <steele@debian.org>
# This file is part of comitup
# Available under the terms of the GNU General Public License version 2
# or later
#

import logging
import NetworkManager as nm
import argparse
import dbus
import sys
import uuid
import getpass
from functools import wraps
import iwscan


import pprint
pp = pprint.PrettyPrinter(indent=4)

log = logging.getLogger('comitup')


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
                log.debug("Got an exception, returning None", fp.__name__)
                return None

        return wrapper

    return _none_on_exception


def get_wifi_devices():
    return [x for x in nm.NetworkManager.GetDevices() if x.DeviceType == 2]


@none_on_exception(IndexError)
def get_wifi_device(index=0):
    return get_wifi_devices()[index]


def get_device_path(device=None):
    if not device:
        device = get_wifi_device()

    return device.SpecificDevice().object_path


def disconnect(device=None):
    if not device:
        device = get_wifi_device()

    try:
        device.Disconnect()
    except:
        log.debug("Error received in disconnect")


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


def activate_connection_by_ssid(ssid, device=None, path='/'):
    if not device:
        device = get_wifi_device()

    connection = get_connection_by_ssid(ssid)

    nm.NetworkManager.ActivateConnection(connection, device, path)


def deactivate_connection(device=None):
    if not device:
        device = get_wifi_device()

    connection = device.ActiveConnection
    if connection:
        nm.NetworkManager.DeactivateConnection(connection)


@none_on_exception(AttributeError)
def get_access_points(device=None):
    if not device:
        device = get_wifi_device()

    return device.SpecificDevice().GetAllAccessPoints()


def get_points_ext(device=None):
    try:
        inlist = sorted(get_access_points(device),
                        key=lambda x: -ord(x.Strength))
    except (TypeError, dbus.exceptions.DBusException):
        log.debug("Error getting access points")
        inlist = []

    outlist = []
    for point in inlist:

        try:
            if point.Flags or point.WpaFlags or point.RsnFlags:
                encstr = "encrypted"
            else:
                encstr = "unencrypted"

            outpoint = {
                'ssid': point.Ssid,
                'strength': str(ord(point.Strength)),
                'security': encstr,
                'nmpath': point.object_path,
            }

            outlist.append(outpoint)
        except dbus.exceptions.DBusException:
            log.debug("Error getting point info")

    return outlist


@none_on_exception(IndexError, TypeError)
def get_access_point_by_ssid(ssid, device=None):
    return [x for x in get_access_points(device) if x.Ssid == ssid][0]


def get_candidate_connections(device=None):
    if not device:
        device = get_wifi_device()

    candidates = []

    for conn in get_all_connections():
        settings = conn.GetSettings()
        ssid = get_ssid_from_connection(conn)

        try:
            if ssid \
               and settings['connection']['type'] == '802-11-wireless' \
               and settings['802-11-wireless']['mode'] == 'infrastructure':

                candidates.append(ssid)
        except KeyError:
            log.debug("Unexpected connection format for %s" % ssid)

    points = [x.Ssid for x in get_access_points()]
    iwpoints = [x['ssid'] for x in iwscan.candidates()]

    return list(set(candidates) & (set(points) | set(iwpoints)))


def make_hotspot(name='comitup'):
    settings = {
        'connection':
        {
            'type': '802-11-wireless',
            'uuid': str(uuid.uuid4()),
            'id': name,
            'autoconnect': False,
            'interface-name': 'wlan0',
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


def make_connection_for(ssid, password=None, interface=None):

    settings = dbus.Dictionary({
        'connection': dbus.Dictionary(
            {
                'id': ssid,
                'type': '802-11-wireless',
                'uuid': str(uuid.uuid4()),
            }),
        '802-11-wireless': dbus.Dictionary(
            {
                'ssid': dbus.ByteArray(ssid),
                'mode': 'infrastructure',
            }),
        'ipv4': dbus.Dictionary(
            {
                # assume DHCP
                'method': 'auto',
            }),
        'ipv6': dbus.Dictionary(
            {
                # assume ipv4-only
                'method': 'ignore',
            }),
    })

    if interface:
        settings['connection']['interface-name'] = interface

    # assume privacy = WPA(2) psk
    if password:
        settings['802-11-wireless']['security'] = '802-11-wireless-security'
        settings['802-11-wireless-security'] = dbus.Dictionary({
            'auth-alg': 'open',
            'key-mgmt': 'wpa-psk',
            'psk': password,
        })

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

    try:
        import tabulate
        print(tabulate.tabulate(bypwr, headers=hdrs))
    except:
        for entry in bypwr:
            print(entry)


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
    """Create a connection for an access point, for future use"""

    password = getpass.getpass('password: ')

    make_connection_for(ssid, password)


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
