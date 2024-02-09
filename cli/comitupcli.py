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
import sys
from pathlib import Path
from re import MULTILINE, search, sub
from subprocess import run
from typing import List

sys.path.append(".")
sys.path.append("..")

from collections import OrderedDict, namedtuple  # noqa
from getpass import getpass  # noqa

from comitup import client as ciu  # noqa


def do_reload(ciu_client, connection):
    pass


def do_quit(ciu_client, connection):
    sys.exit(0)


def do_delete(ciu_client, connection):
    ciu_client.ciu_delete(connection)


def do_connect(ciu_client, ssid, password):
    ciu_client.ciu_connect(ssid, password)


def do_info(ciu_client, connection):
    info = ciu_client.ciu_info(connection)
    print(
        "Host %s on comitup version %s" % (info["hostnames"], info["version"])
    )
    print("'%s' mode" % info["imode"])

    state, _ = get_state(ciu_client)
    print("{} state".format(state))


def do_locate(ciu_client, connection):
    print("Attempting to blink the Pi front green led once")
    try:
        ciu.blink()
    except PermissionError:
        print("ERROR: Run as root")


def set_conf(key, val):
    confpath = Path("/etc/comitup.conf")

    confdata = confpath.read_text()

    if search("^{}: .+$".format(key), confdata, flags=MULTILINE):
        confdata = sub(
            "^{}: .+$".format(key),
            "{}: {}".format(key, val),
            confdata,
            flags=MULTILINE,
        )
    elif search("^# {}:.+$".format(key), confdata, flags=MULTILINE):
        confdata = sub(
            "^(# {}:.+)$".format(key),
            r"\1\n{}: {}".format(key, val),
            confdata,
            flags=MULTILINE,
        )
    else:
        confdata += "{}: {}\n".format(key, val)

    confpath.write_text(confdata)


def do_name(ciu_client, name):
    with open("/etc/hostname", "w", encoding="utf-8") as fp:
        fp.write(name)
    with open("/etc/hosts", "a", encoding="utf-8") as fp:
        fp.write("127.0.0.1\t{}\n".format(name))
    run(["/usr/bin/hostname", name])
    set_conf("ap_name", name)
    run(["/usr/bin/systemctl", "restart", "comitup"])

    sys.exit(0)


def do_nuke(ciu_client, connection):
    ciu_client.ciu_nuke()


CmdState = namedtuple(
    "CmdState", "fn, desc, HOTSPOT, CONNECTING, CONNECTED, scriptable"
)

commands = OrderedDict(
    [
        ("r", CmdState(do_reload, "(r)eload", True, True, True, False)),
        ("i", CmdState(do_info, "(i)nfo", True, True, True, True)),
        (
            "l",
            CmdState(do_locate, "(l)ocate the device", True, True, True, True),
        ),
        (
            "n",
            CmdState(
                do_name,
                "re(n)ame the device (restarts the service)",
                True,
                True,
                True,
                True,
            ),
        ),
        (
            "d",
            CmdState(
                do_delete, "(d)elete connection", False, True, True, True
            ),
        ),
        (
            "<n>",
            CmdState(do_connect, "connect to <n>", True, False, False, False),
        ),
        (
            "m",
            CmdState(
                do_connect, "(m)anual connection", True, False, False, True
            ),
        ),
        (
            "x",
            CmdState(
                do_nuke,
                "(x) Factory reset (no warning)",
                True,
                True,
                True,
                True,
            ),
        ),
        ("q", CmdState(do_quit, "(q)uit", True, True, True, False)),
    ]
)


def int_value(s):
    try:
        return int(s)
    except (ValueError, TypeError):
        return None


def get_state(ciu_client):
    state, connection = ciu_client.ciu_state()
    return state, connection


def get_valid_cmds(state):
    cmds = [x for x in commands.keys() if commands[x].__getattribute__(state)]
    return cmds


def print_cmd_prompts(state, connection, points):
    print("")
    print("State: %s" % state)
    print("Connection: %s" % connection)

    if state == "HOTSPOT":
        print("Points:")
        for point in enumerate(points, start=1):
            print("    %d: %s" % (point[0], point[1]["ssid"]))

    print("Available commands:")

    for cmd in get_valid_cmds(state):
        print("    %s" % commands[cmd].desc)


def interpreter():
    ciu_client = ciu.CiuClient()

    while True:
        state, connection = get_state(ciu_client)

        points = ciu_client.ciu_points()

        print_cmd_prompts(state, connection, points)

        cmd = input("command?: ")

        index = int_value(cmd)

        if index:
            password = ""
            if points[index - 1]["security"] == "encrypted":
                password = getpass("password: ")
            do_connect(ciu_client, points[index - 1]["ssid"], password)
        elif cmd == "m":
            ssid = input("ssid?: ")
            password = getpass("password (if required)?: ")
            do_connect(ciu_client, ssid, password)
        elif cmd == "n":
            name = input("new host name?: ")
            do_name(ciu_client, name)
        else:
            try:
                print()
                commands[cmd].fn(ciu_client, connection)
            except KeyError:
                print("\nInvalid command\n")


def one_shot(cmdlist: List[str]):
    cmd = cmdlist[0]

    if cmd not in commands:
        print("Invalid command {}".format(cmd))
        return

    if not commands[cmd].scriptable:
        print("Command is not scriptable")
        return

    ciu_client = ciu.CiuClient()

    state, connection = get_state(ciu_client)

    if cmd == "m":
        print("Attempting to connect to {}".format(cmdlist[1]))
        do_connect(ciu_client, *cmdlist[1:])
    elif cmd == "n":
        do_name(ciu_client, *cmdlist[1:])
    else:
        commands[cmd].fn(ciu_client, connection)


def parse_args():
    parser = argparse.ArgumentParser(
        description="A CLI front end for the Comitup service"
    )

    parser.add_argument("command", nargs="*", help="a one-shot command")

    return parser.parse_args()


def main():
    args = parse_args()

    if args.command:
        one_shot(args.command)
    else:
        interpreter()


if __name__ == "__main__":
    main()
