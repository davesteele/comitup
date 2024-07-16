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

import argparse
import getpass
import logging
import pprint
import sys
import uuid
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar, cast

import dbus
import NetworkManager as nm

device_list: Optional[List[nm.Device]] = None
settings_cache: Dict[str, Any] = {}

pp = pprint.PrettyPrinter(indent=4)

log = logging.getLogger("comitup")


def initialize() -> None:
    nm.Settings.ReloadConnections()


A = TypeVar("A")
R = TypeVar("R")


# TODO - use ParamSpec["A"] once 3.10 become ubiquitous
def none_on_exception(
    *exceptions,
) -> Callable[[Callable[[A], R]], Callable[[A], Optional[R]]]:
    def _none_on_exception(fp: Callable[..., R]) -> Callable[..., Optional[R]]:
        @wraps(fp)
        def wrapper(*args, **kwargs) -> Optional[R]:
            try:
                return fp(*args, **kwargs)
            except exceptions:
                log.debug("Got an exception, returning None, %s", fp.__name__)
                return None

        return wrapper

    return _none_on_exception


def get_devices() -> Optional[List[nm.Device]]:
    global device_list

    if not device_list:
        try:
            device_list = nm.NetworkManager.GetDevices()
        except TypeError:
            # NetworkManager is gone for some reason. Bail big time.
            sys.exit(1)

    if not device_list:
        log.error("No devices found in nm.get_devices()")

    return device_list


def device_name(device: nm.Device) -> str:
    return device.Interface


def get_wifi_devices() -> List[nm.Wireless]:
    devices: Optional[List[nm.Device]] = get_devices()

    if devices is not None:
        devices_filt = []
        for device in devices:
            try:
                if device.DeviceType == 2:
                    devices_filt.append(device)
            except nm.ObjectVanished:
                pass

        return [cast(nm.Wireless, x) for x in devices_filt]
    else:
        log.error("No WiFi devices found in nm.get_wifi_devices()")
        return []


def get_phys_dev_names() -> List[str]:
    devices = get_devices()

    returnval = []
    if devices is not None:
        for device in devices:
            try:
                if device.DeviceType in (1, 2):
                    returnval.append(device_name(device))
            except nm.ObjectVanished:
                pass

    return returnval


@none_on_exception(IndexError)
def get_wifi_device(index: int = 0) -> Optional[nm.Device]:
    return get_wifi_devices()[index]


def get_device_path(device: nm.Device) -> dbus.ObjectPath:
    log.debug("Getting specific device for path")
    return device.SpecificDevice().object_path


def disconnect(device: nm.Device) -> None:
    try:
        log.debug("Calling disconnect")
        device.Disconnect()
    except:  # noqa
        log.debug("Error received in disconnect")


def get_connection_settings(connection: nm.Connection) -> Dict[str, Any]:
    global settings_cache

    if connection.uuid not in settings_cache:
        log.debug("Not in cache")
        settings_cache[connection.uuid] = connection.GetSettings()

    return settings_cache[connection.uuid]


def get_device_settings(device: nm.Device) -> Dict[str, Any]:
    try:
        connection = device.ActiveConnection
    except nm.ObjectVanished:
        sys.exit(1)

    return get_connection_settings(connection.Connection)


@none_on_exception(AttributeError, nm.ObjectVanished)
def get_active_ssid(device: nm.Device) -> Optional[str]:
    return get_device_settings(device)["802-11-wireless"]["ssid"]


@none_on_exception(AttributeError, IndexError, nm.ObjectVanished)
def get_active_ip(device: nm.Device) -> Optional[str]:
    addr: str = device.Ip4Address
    if addr == "0.0.0.0":
        addr = device.Ip4Config.Addresses[0][0]

    return addr


@none_on_exception(AttributeError, IndexError, nm.ObjectVanished)
def get_active_ip6(device: nm.Device) -> Optional[str]:
    addr6 = device.Ip6Config.Addresses[0][0]

    return addr6


def get_all_connections() -> List[nm.Connection]:
    return [x for x in nm.Settings.ListConnections()]


def get_all_wifi_connection_ssids():
    for conn in get_all_connections():
        ssid = get_ssid_from_connection(conn)
        if ssid:
            yield ssid


@none_on_exception(AttributeError, KeyError, nm.ObjectVanished)
def get_ssid_from_connection(connection: nm.Connection) -> Optional[str]:
    settings = get_connection_settings(connection)

    return settings["802-11-wireless"]["ssid"]


def get_connection_by_ssid(name: str) -> Optional[nm.Connection]:
    for connection in get_all_connections():
        ssid = get_ssid_from_connection(connection)
        if name == ssid:
            return connection

    return None


def del_connection_by_ssid(name: str) -> None:
    for connection in get_all_connections():
        ssid = get_ssid_from_connection(connection)
        if name == ssid:
            connection.Delete()


def activate_connection_by_ssid(ssid: str, device: nm.Device, path: str = "/"):
    connection = get_connection_by_ssid(ssid)

    if connection:
        log.debug("    {}".format(get_ssid_from_connection(connection)))
        log.debug("    {}".format(device_name(device)))

        opath = nm.NetworkManager.ActivateConnection(connection, device, path)

        log.debug("ActivateConnection returned {}".format(opath.object_path))
    else:
        log.error("Connection for {} not found".format(ssid))


@none_on_exception(AttributeError)
def get_access_points(device: nm.Device) -> Optional[List[nm.AccessPoint]]:
    return device.SpecificDevice().GetAllAccessPoints()


def get_candidate_connections(device: nm.Device) -> List[str]:
    candidates = []

    for conn in get_all_connections():
        log.debug("Getting settings 2")
        settings = get_connection_settings(conn)
        ssid = get_ssid_from_connection(conn)

        try:
            if (
                ssid
                and settings["connection"]["type"] == "802-11-wireless"
                and settings["802-11-wireless"]["mode"] == "infrastructure"
            ):
                candidates.append(ssid)
        except KeyError:
            log.debug("Unexpected connection format for %s" % ssid)

    log.debug("candidates: %s" % candidates)

    return candidates


def make_hotspot(name="comitup", device=None, password="", hash="0000"):
    comitup_uuid = str(uuid.uuid4())
    settings = {
        "connection": {
            "type": "802-11-wireless",
            "uuid": comitup_uuid,
            "id": "{0}-{1}".format(name, hash),
            "autoconnect": False,
        },
        "802-11-wireless": {
            "mode": "ap",
            "ssid": name,
            "band": "bg",
        },
        "ipv4": {
            "method": "manual",
            "address-data": [
                {
                    "address": "10.41.0.1",
                    "prefix": 24,
                }
            ],
        },
        "ipv6": {
            "method": "ignore",
        },
    }

    if device:
        settings["connection"]["interface-name"] = device_name(device)

    if password and len(password) >= 8:
        settings["802-11-wireless-security"] = {}
        settings["802-11-wireless-security"]["key-mgmt"] = "wpa-psk"
        settings["802-11-wireless-security"]["psk"] = password

    nm.Settings.AddConnection(settings)


def make_connection_for(
    ssid: str,
    password: Optional[str] = None,
    interface: Optional[str] = None,
    link_local: bool = True,
) -> None:
    settings = dbus.Dictionary(
        {
            "connection": dbus.Dictionary(
                {
                    "id": ssid,
                    "type": "802-11-wireless",
                    "uuid": str(uuid.uuid4()),
                }
            ),
            "802-11-wireless": dbus.Dictionary(
                {
                    "ssid": dbus.ByteArray(ssid.encode()),
                    "mode": "infrastructure",
                }
            ),
            "ipv4": dbus.Dictionary(
                {
                    # assume DHCP
                    "method": "auto",
                }
            ),
            "ipv6": dbus.Dictionary(
                {
                    "method": "link-local",
                }
            ),
        }
    )

    if not link_local:
        settings["ipv6"]["method"] = "auto"

    if interface:
        settings["connection"]["interface-name"] = interface

    # assume privacy = WPA(2) psk
    if password:
        settings["802-11-wireless"]["security"] = "802-11-wireless-security"
        settings["802-11-wireless-security"] = dbus.Dictionary(
            {
                "auth-alg": "open",
                "key-mgmt": "wpa-psk",
                "psk": password,
            }
        )

    nm.Settings.AddConnection(settings)


#
# CLI Interface
#


def do_listaccess(arg):
    """List all accessible access points"""
    rows = []
    for point in get_access_points(get_wifi_devices()[-1]):
        row = (
            point.Ssid,
            point.HwAddress,
            point.Flags,
            point.WpaFlags,
            point.RsnFlags,
            point.Strength,
            point.Frequency,
        )
        rows.append(row)

    bypwr = sorted(rows, key=lambda x: -x[5])

    hdrs = ("SSID", "MAC", "Private", "WPA", "RSN", "Power", "Frequency")

    try:
        import tabulate

        print(tabulate.tabulate(bypwr, headers=hdrs))
    except:  # noqa
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
    activate_connection_by_ssid(ssid, get_wifi_device())


def do_getconnection(dummy):
    """Print the active connection ssid"""
    print(get_active_ssid(get_wifi_device()))


def do_getip(dummy):
    """Print the current IP address"""
    print(get_active_ip(get_wifi_device()))


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

    for candidate in get_candidate_connections(get_wifi_device()):
        print(candidate)


def do_makeconnection(ssid):
    """Create a connection for an access point, for future use"""

    password = getpass.getpass("password: ")

    make_connection_for(ssid, password)


def get_command(cmd):
    cmd_name = "do_" + cmd

    try:
        return globals()[cmd_name]
    except KeyError:
        return None


def parse_args():
    prog = "comitup"
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
        "command",
        help="command",
    )

    parser.add_argument(
        "arg",
        nargs="?",
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


if __name__ == "__main__":
    main()
