#!/usr/bin/python
# Copyright (c) 2017 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2+
# License-Filename: LICENSE

#
# Copyright 2016-2017 David Steele <steele@debian.org>
# This file is part of comitup
# Available under the terms of the GNU General Public License version 2
# or later
#

import dbus
import sys
from collections import defaultdict

func_map = defaultdict(lambda: None)

def ciu_decorator(fn):
    def wrapper(*args, **kwargs):
        endpoint = fn()

        if func_map[endpoint] is None:
            try:
                bus = dbus.SystemBus()

                ciu_service = bus.get_object(
                       'com.github.davesteele.comitup',
                       '/com/github/davesteele/comitup'
                    )

                func_map[endpoint] = ciu_service.get_dbus_method(
                       endpoint,
                       'com.github.davesteele.comitup'
                    )
            except dbus.exceptions.DBusException:
                print("Error connecting to the comitup D-Bus service")
                sys.exit(1)

        return func_map[endpoint](*args, **kwargs)

    return wrapper


@ciu_decorator
def ciu_state():
    return 'state'

@ciu_decorator
def ciu_points():
    return 'access_points'

@ciu_decorator
def ciu_delete():
    return 'delete_connection'

@ciu_decorator
def ciu_connect():
    return 'connect'

@ciu_decorator
def ciu_ifo():
    return 'get_info'
