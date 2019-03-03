
# Copyright (c) 2019 David Steele <dsteele@gmail.com>
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

bus = dbus.SystemBus()
systemd_service = bus.get_object(
    'org.freedesktop.systemd1',
    '/org/freedesktop/systemd1',
)

sd_start_unit = systemd_service.get_dbus_method(
    'StartUnit',
    'org.freedesktop.systemd1.Manager',
)

sd_stop_unit = systemd_service.get_dbus_method(
    'StopUnit',
    'org.freedesktop.systemd1.Manager',
)

sd_unit_state = systemd_service.get_dbus_method(
    'GetUnitFileState',
    'org.freedesktop.systemd1.Manager',
)

if __name__ == "__main__":
    print(sd_unit_state("NetworkManager.service"))
