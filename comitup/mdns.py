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
from typing import Dict, List, Optional

import dbus
import NetworkManager

from comitup import config, nm

log = logging.getLogger("comitup")

# globals

CLASS_IN = 0x01
TYPE_A = 0x01
TYPE_AAAA = 0x1C
TTL = 5

DBUS_NAME = "org.freedesktop.Avahi"
DBUS_PATH_SERVER = "/"
DBUS_INTERFACE_SERVER = "org.freedesktop.Avahi.Server"
DBUS_INTERFACE_ENTRY_GROUP = "org.freedesktop.Avahi.EntryGroup"
PROTO_UNSPECIFIED = -1
PROTO_INET = 0
PROTO_INET6 = 1
group: Optional[dbus.Interface] = None

# functions


def establish_group() -> None:
    global group

    if not group:
        bus = dbus.SystemBus()

        server = dbus.Interface(
            bus.get_object(DBUS_NAME, DBUS_PATH_SERVER), DBUS_INTERFACE_SERVER
        )

        group = dbus.Interface(
            bus.get_object(DBUS_NAME, server.EntryGroupNew()),
            DBUS_INTERFACE_ENTRY_GROUP,
        )


def encode_dns(name: str) -> bytes:
    components = [x for x in name.split(".") if len(x) > 0]
    fixed_name = ".".join(components)
    return fixed_name.encode("ascii")


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
            socket.inet_aton(addr),
        )


def make_aaaa_record(host: str, devindex: int, addr: str) -> None:
    if group:
        group.AddRecord(
            devindex,
            PROTO_INET6,
            dbus.UInt32(0),
            encode_dns(host),
            CLASS_IN,
            TYPE_AAAA,
            TTL,
            socket.inet_pton(socket.AF_INET6, addr),
        )


def string_to_txt_array(strng: str) -> List[bytes]:
    if strng:
        return [dbus.Byte(x) for x in strng.encode()]
    else:
        return []


def string_array_to_txt_array(txt_array: List[str]) -> List[List[bytes]]:
    return [string_to_txt_array(x) for x in txt_array]


def add_service(
    host: str, devindex: int, addr: Optional[str], addr6: Optional[str]
) -> None:
    name = host
    (conf, data) = config.load_data()
    if ".local" in name:
        name = name[: -len(".local")]

    if group:
        group.AddService(
            devindex,
            PROTO_UNSPECIFIED,
            dbus.UInt32(0),
            name,
            "_%s._tcp" % conf.service_name,
            "",
            host,
            dbus.UInt16(9),
            string_array_to_txt_array(
                [
                    "hostname=%s" % host,
                    (
                        "ipaddr=%s" % addr
                        if (addr and addr != "0.0.0.0")
                        else "ipaddr="
                    ),
                    "ip6addr=%s" % addr6 if addr6 else "ip6addr=",
                    "comitup-home=https://davesteele.github.io/comitup/",
                ]
            ),
        )


# public functions


def clear_entries(emphatic=False) -> None:
    global group

    if group and (not group.IsEmpty() or emphatic):
        group.Reset()

        if emphatic:
            group.Free()
            group = None

    establish_group()


def get_interface_mapping() -> Dict[str, int]:
    mapping: Dict[str, int] = {}

    for line in subprocess.check_output(["ip", "addr"]).decode().split("\n"):
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

    entries: bool = False
    for device in devices:
        try:
            name = nm.device_name(device)
            addr = nm.get_active_ip(device)
            addr6 = nm.get_active_ip6(device)
            log.debug("add_hosts: {}, {}".format(name, addr))
            if name in nm.get_phys_dev_names() and name in int_mapping:
                index = int_mapping[name]

                try:
                    if addr and addr != "0.0.0.0":
                        for host in hosts:
                            log.debug(
                                "Add A record {}-{}-{}".format(
                                    host, index, addr
                                )
                            )
                            make_a_record(host, index, addr)

                        entries = True

                    if addr6:
                        for host in hosts:
                            log.debug(
                                "Add AAAA record {}-{}-{}".format(
                                    host, index, addr6
                                )
                            )
                            make_aaaa_record(host, index, addr6)

                        entries = True

                    if addr6 or (addr and addr != "0.0.0.0"):
                        log.debug(
                            "Add service {}, {}, {}-{}".format(
                                host, index, addr, addr6
                            )
                        )
                        add_service(hosts[0], index, addr, addr6)

                except Exception:
                    log.error("Exception encountered adding avahi record")
                    clear_entries(emphatic=True)
                    entries = False
        except NetworkManager.ObjectVanished:
            pass

    if group and entries:
        group.Commit()


def check_mdns(hosts: List[str]) -> None:
    reset = False

    log.debug("Checking mdns")

    try:
        socket.gethostbyname(hosts[0])
    except socket.gaierror:
        reset = True

    if reset:
        log.error("Mdns check failed - resetting records and services.")
        clear_entries(emphatic=True)
        add_hosts(hosts)


if __name__ == "__main__":
    add_hosts(["comitup-1111.local", "comitup.local"])

    while True:
        pass
