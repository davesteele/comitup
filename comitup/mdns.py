#!/usr/bin/python

import avahi
import dbus
from encodings.idna import ToASCII
import socket
import logging

log = logging.getLogger('comitup')

# globals

CLASS_IN = 0x01
TYPE_A = 0x01
TTL = 5

server = None
group = None


# functions

def establish_group():
    global server, group

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


def make_a_record(host, addr):
    group.AddRecord(
        avahi.IF_UNSPEC,
        avahi.PROTO_UNSPEC,
        dbus.UInt32(0),
        encode_dns(host),
        CLASS_IN,
        TYPE_A,
        TTL,
        socket.inet_aton(addr)
    )


def add_service(host):
    group.AddService(
        avahi.IF_UNSPEC,
        avahi.PROTO_UNSPEC,
        dbus.UInt32(0),
        "Comitup Service",
        "_http._tcp",
        "",
        host,
        dbus.UInt16(80),
        avahi.string_array_to_txt_array("")
    )

# public functions


def clear_entries():
    try:
        if not group.IsEmpty():
            group.Reset()
    except:
        log.warn("Error encountered clearing mdns data")

    establish_group()


def add_hosts(hosts, addr):
    establish_group()

    for host in hosts:
        make_a_record(host, addr)

    add_service(hosts[0])

    group.Commit()

if __name__ == '__main__':
    add_hosts(['comitup-1111.local', 'comitup.local'], '192.168.200.32')

    while True:
        pass
