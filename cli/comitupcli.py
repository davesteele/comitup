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

import sys

sys.path.append('.')
sys.path.append('..')

from collections import namedtuple, OrderedDict  # noqa
from getpass import getpass                      # noqa
from comitup import client as ciu                # noqa


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
    print("")
    print("Host %s on comitup version %s"
          % (info['hostnames'], info['version']))
    print("'%s' mode" % info['imode'])


CmdState = namedtuple('CmdState', "fn, desc, HOTSPOT, CONNECTING, CONNECTED")

commands = OrderedDict([
    ('i',   CmdState(do_info,    '(i)nfo',               True,  True, True)),
    ('r',   CmdState(do_reload,  '(r)eload',             True,  True, True)),
    ('d',   CmdState(do_delete,  '(d)elete connection',  False, True, True)),
    ('q',   CmdState(do_quit,    '(q)uit',               True,  True, True)),
    ('<n>', CmdState(do_connect, 'connect to <n>',       True,  False, False)),
    ('m',   CmdState(do_connect, '(m)anual connection',  True,  False, False)),
])


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
    print('')
    print("State: %s" % state)
    print("Connection: %s" % connection)

    if state == 'HOTSPOT':
        print("Points:")
        for point in enumerate(points, start=1):
            print("    %d: %s" % (point[0], point[1]['ssid']))

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
            if points[index-1]['security'] == 'encrypted':
                password = getpass('password: ')
            do_connect(ciu_client, points[index-1]['ssid'], password)
        elif cmd == 'm':
            ssid = input("ssid?: ")
            password = getpass('password (if required)?: ')
            do_connect(ciu_client, ssid, password)
        else:
            try:
                commands[cmd].fn(ciu_client, connection)
            except KeyError:
                print("\nInvalid command\n")


if __name__ == '__main__':
    interpreter()
