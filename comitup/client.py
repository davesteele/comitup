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
import sys


class CiuClient(object):

    # Make the dbus functions late binding, to facilitate testing.

    # These are the methods supported, with the corresponding dbus
    # endpoint name.
    methods = {
        'ciu_info': 'get_info',
        'ciu_state': 'state',
        'ciu_points': 'access_points',
        'ciu_connect': 'connect',
        'ciu_delete': 'delete_connection',
    }

    def __init__(self):
        self.service = None

    def __getattr__(self, name):
        if name not in self.methods:
            raise AttributeError("Attribute {} not found".format(name))

        try:
            if not self.service:
                bus = dbus.SystemBus()
                self.service = bus.get_object('com.github.davesteele.comitup',
                                              '/com/github/davesteele/comitup')
            func = self.service.get_dbus_method(
                    self.methods[name],
                    'com.github.davesteele.comitup'
                    )
        except dbus.exceptions.DBusException:
            sys.exit(1)

        # connect as an unbound function
        self.__setattr__(name, func)
        return func
