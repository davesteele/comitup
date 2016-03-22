#!/usr/bin/python

import sys

sys.path.append('.')
sys.path.append('..')

from collections import namedtuple, OrderedDict
from getpass import getpass
from comitup import client as ciu


def do_reload(connection):
    pass


def do_quit(connection):
    sys.exit(0)


def do_delete(connection):
    ciu.ciu_delete(connection)


def do_connect(connection, password):
    ciu.ciu_connect(connection, password)


CmdState = namedtuple('CmdState', "fn, desc, HOTSPOT, CONNECTING, CONNECTED")

commands = OrderedDict([
    ('r',   CmdState(do_reload,  '(r)eload',            True,  True, True)),
    ('d',   CmdState(do_delete,  '(d)elete connection', False, True, True)),
    ('q',   CmdState(do_quit,    '(q)uit',              True,  True, True)),
    ('<n>', CmdState(do_connect, 'connect to <n>',     True, False, False)),
])


def int_value(s):
    try:
        return int(s)
    except (ValueError, TypeError):
        return None


def get_state():
    state, connection = ciu.ciu_state()
    return state, connection


def get_valid_cmds(state):
    cmds = [x for x in commands.keys() if commands[x].__getattribute__(state)]
    return cmds


def print_cmd_prompts(state, connection, points):
    print
    print "State:", state
    print "Connection:", connection

    if state == 'HOTSPOT':
        print "Points:"
        for point in enumerate(points, start=1):
            print "    %d: %s" % (point[0], point[1]['ssid'])

    print "Available commands:"

    for cmd in get_valid_cmds(state):
        print "    %s" % commands[cmd].desc


def interpreter():
    while True:
        state, connection = get_state()

        points = ciu.ciu_points()

        print_cmd_prompts(state, connection, points)

        cmd = raw_input("command?: ")

        index = int_value(cmd)

        if index:
            password = ""
            if points[index-1]['security'] == 'encrypted':
                password = getpass('password: ')
            do_connect(points[index-1]['ssid'], password)
        else:
            ciu.ciu_activity()
            try:
                commands[cmd].fn(connection)
            except KeyError:
                print "\nInvalid command\n"


if __name__ == '__main__':
    interpreter()
