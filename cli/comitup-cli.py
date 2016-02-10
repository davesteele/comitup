#!/usr/bin/python

import sys
from collections import namedtuple
import dbus

bus = dbus.SessionBus()
ciu_service = bus.get_object(
               'com.github.davesteele.comitup',
               '/com/github/davesteele/comitup'
              )

ciu_state = service.get_dbus_method('state', 'com.github.davesteele.comitup')
ciu_activity = service.get_dbus_method('activity', 'com.github.davesteele.comitup')
ciu_points = service.get_dbus_method('access_points', 'com.github.davesteele.comitup')

def do_reload(connection):
    pass


def do_quit(connection):
    sys.exit(0)

def do_delete(connection):
    pass


def do_connect(connection):
    pass

CmdState = namedtuple('CmdState', "fn, desc, HOTSPOT, CONNECTING, CONNECTED")

commands = {
    'r':   CmdState(do_reload,  '(r)eload',            True,  True, True),
    'd':   CmdState(do_delete,  '(d)elete connection', False, True, True),
    'q':   CmdState(do_quit,    '(q)uit',              True,  True, True),
    '<n>': CmdState(do_connect, 'connecto to <n>',     True, False, False),
}

def int_value(s):
    try:
        return int(s)
    except ValueError:
        return None

def get_state():
    state, connection = ciu_state()
    return state, connection

def interpreter():
    while True:
        state, connection = get_state()

        points = get_points()

        print_cmd_prompts(state, connection)

        cmd = get_cmd()

        index = int_value(cmd)

        if index:
            do_connect()
        else:
            ciu_activity()
            commands[cmd].fn(connection)

        
    
