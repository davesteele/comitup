#!/usr/bin/python

#
# Copyright 2016-2017 David Steele <steele@debian.org>
# This file is part of comitup
# Available under the terms of the GNU General Public License version 2
# or later
#

import avahi
import dbus
from encodings.idna import ToASCII
import socket
import logging
import nm

log = logging.getLogger('comitup')

# globals

CLASS_IN = 0x01
TYPE_A = 0x01
TTL = 5

group = None


# functions

def establish_group():
    global group

    bus = dbus.SystemBus()

    server = dbus.Interface(
            bus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER),
            avahi.DBUS_INTERFACE_SERVER
    )

    group = dbus.Interface(
            bus.get_object(avahi.DBUS_NAME, server.EntryGroupNew()),
            avahi.DBUS_INTERFACE_ENTRY_GROUP
    )


def encode_dns(name):
    out = []
    for part in name.split('.'):
        if len(part) == 0:
            continue
        out.append(ToASCII(part))
    return '.'.join(out)


def make_a_record(host, devindex, addr):
    group.AddRecord(
        devindex,
        avahi.PROTO_INET,
        dbus.UInt32(0),
        encode_dns(host),
        CLASS_IN,
        TYPE_A,
        TTL,
        socket.inet_aton(addr)
    )


def add_service(host, devindex, addr):
    name = host
    if '.local' in name:
        name = name[:-len('.local')]

    group.AddService(
        devindex,
        avahi.PROTO_INET,
        dbus.UInt32(0),
        name,
        "_workstation._tcp",
        "",
        host,
        dbus.UInt16(9),
        avahi.string_array_to_txt_array([
            "hostname=%s" % host,
            "ipaddr=%s" % addr,
            "comitup-home=https://davesteele.github.io/comitup/",
        ])
    )

# public functions


def clear_entries():
    if group and not group.IsEmpty():
        group.Reset()

    establish_group()


def add_hosts(hosts):
    establish_group()

    i = 0
    for device in nm.get_devices():
        i += 1
        name = nm.device_name(device)
        addr = nm.get_active_ip(device)
        if (name in nm.get_phys_dev_names()) and addr:
            for host in hosts:
                make_a_record(host, i, addr)

            add_service(hosts[0], i, addr)

    group.Commit()


if __name__ == '__main__':
    add_hosts(['comitup-1111.local', 'comitup.local'])

    while True:
        pass
