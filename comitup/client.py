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

bus = dbus.SystemBus()

try:
    ciu_service = bus.get_object(
                   'com.github.davesteele.comitup',
                   '/com/github/davesteele/comitup'
                  )
except dbus.exceptions.DBusException:
    print("Error connecting to the comitup D-Bus service")
    sys.exit(1)

ciu_state = ciu_service.get_dbus_method(
                'state',
                'com.github.davesteele.comitup'
            )
ciu_points = ciu_service.get_dbus_method(
                'access_points',
                'com.github.davesteele.comitup'
             )
ciu_delete = ciu_service.get_dbus_method(
                'delete_connection',
                'com.github.davesteele.comitup'
             )
ciu_connect = ciu_service.get_dbus_method(
                'connect',
                'com.github.davesteele.comitup'
             )
ciu_info = ciu_service.get_dbus_method(
                'get_info',
                'com.github.davesteele.comitup'
             )
