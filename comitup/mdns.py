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

import dbus
import socket
import logging
from comitup import nm
import subprocess

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

group = None

# functions


def establish_group():
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


def encode_dns(name):
    components = [x for x in name.split('.') if len(x) > 0]
    fixed_name = '.'.join(components)
    return fixed_name.encode('ascii')


def make_a_record(host, devindex, addr):
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


def string_to_txt_array(strng):
    if strng:
        return [dbus.Byte(x) for x in strng.encode()]
    else:
        return strng


def string_array_to_txt_array(txt_array):
    return [string_to_txt_array(x) for x in txt_array]


def add_service(host, devindex, addr):
    name = host
    if '.local' in name:
        name = name[:-len('.local')]

    group.AddService(
        devindex,
        PROTO_INET,
        dbus.UInt32(0),
        name,
        "_workstation._tcp",
        "",
        host,
        dbus.UInt16(9),
        string_array_to_txt_array([
            "hostname=%s" % host.encode(),
            "ipaddr=%s" % addr,
            "comitup-home=https://davesteele.github.io/comitup/",
        ])
    )

# public functions


def clear_entries():
    global group

    if group and not group.IsEmpty():
        group.Reset()
        group.Free()
        group = None

    establish_group()


def get_interface_mapping():
    mapping = {}

    for line in subprocess.check_output(["ip", "addr"]).decode().split('\n'):
        try:
            asc_index, name = line.split(": ")[0:2]
            mapping[name] = int(asc_index)
        except ValueError:
            pass

    return mapping


def add_hosts(hosts):
    establish_group()
    int_mapping = get_interface_mapping()

    for device in nm.get_devices():
        name = nm.device_name(device)
        addr = nm.get_active_ip(device)
        if (name in nm.get_phys_dev_names()
                and name in int_mapping
                and addr):

            index = int_mapping[name]
            for host in hosts:
                make_a_record(host, index, addr)

            add_service(hosts[0], index, addr)

    group.Commit()


if __name__ == '__main__':
    add_hosts(['comitup-1111.local', 'comitup.local'])

    while True:
        pass
