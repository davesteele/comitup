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

import logging
import socket
import subprocess
from typing import Dict, List, Optional, TYPE_CHECKING

import dbus

from comitup import config, nm

if TYPE_CHECKING:
    import NetworkManager  # noqa

log = logging.getLogger('comitup')

# globals

CLASS_IN = 0x01
TYPE_A = 0x01
TTL = 5

DBUS_NAME = 'org.freedesktop.Avahi'
DBUS_PATH_SERVER = '/'
DBUS_INTERFACE_SERVER = 'org.freedesktop.Avahi.Server'
DBUS_INTERFACE_ENTRY_GROUP = 'org.freedesktop.Avahi.EntryGroup'
PROTO_INET = 0
group: Optional[dbus.Interface] = None

# functions


def establish_group() -> None:
    global group

    if not group:
        bus = dbus.SystemBus()

        server = dbus.Interface(
            bus.get_object(DBUS_NAME, DBUS_PATH_SERVER),
            DBUS_INTERFACE_SERVER
        )

        group = dbus.Interface(
            bus.get_object(DBUS_NAME, server.EntryGroupNew()),
            DBUS_INTERFACE_ENTRY_GROUP
        )


def encode_dns(name: str) -> bytes:
    components = [x for x in name.split('.') if len(x) > 0]
    fixed_name = '.'.join(components)
    return fixed_name.encode('ascii')


def make_a_record(host: str, devindex: int, addr: str) -> None:
    if group:
        group.AddRecord(
            devindex,
            PROTO_INET,
            dbus.UInt32(0),
            encode_dns(host),
            CLASS_IN,
            TYPE_A,
            TTL,
            socket.inet_aton(addr)
        )


def string_to_txt_array(strng: str) -> List[bytes]:
    if strng:
        return [dbus.Byte(x) for x in strng.encode()]
    else:
        return []


def string_array_to_txt_array(txt_array: List[str]) -> List[List[bytes]]:
    return [string_to_txt_array(x) for x in txt_array]


def add_service(host: str, devindex: int, addr: str) -> None:
    name = host
    (conf, data) = config.load_data()
    if '.local' in name:
        name = name[:-len('.local')]

    if group:
        group.AddService(
            devindex,
            PROTO_INET,
            dbus.UInt32(0),
            name,
            "_%s._tcp" % conf.service_name,
            "",
            host,
            dbus.UInt16(9),
            string_array_to_txt_array([
                "hostname=%s" % host,
                "ipaddr=%s" % addr,
                "comitup-home=https://davesteele.github.io/comitup/",
            ])
        )

# public functions


def clear_entries() -> None:
    global group

    if group and not group.IsEmpty():
        group.Reset()
        group.Free()
        group = None

    establish_group()


def get_interface_mapping() -> Dict[str, int]:
    mapping: Dict[str, int] = {}

    for line in subprocess.check_output(["ip", "addr"]).decode().split('\n'):
        try:
            asc_index, name = line.split(": ")[0:2]
            mapping[name] = int(asc_index)
        except ValueError:
            pass

    return mapping


def add_hosts(hosts: List[str]) -> None:
    establish_group()
    int_mapping = get_interface_mapping()

    devices: Optional[List["NetworkManager.Device"]] = nm.get_devices()

    if devices is None:
        log.error("Null device list returned in add_hosts()")
        return

    if not devices:
        log.error("No devices found in add_hosts()")
        return

    for device in devices:
        name = nm.device_name(device)
        addr = nm.get_active_ip(device)
        if (name in nm.get_phys_dev_names()
                and name in int_mapping
                and addr):

            index = int_mapping[name]
            for host in hosts:
                make_a_record(host, index, addr)

            add_service(hosts[0], index, addr)

    try:
        if group:
            group.Commit()
    except dbus.exceptions.DBusException:
        log.error("Error committing Avahi group")


if __name__ == '__main__':
    add_hosts(['comitup-1111.local', 'comitup.local'])

    while True:
        pass
