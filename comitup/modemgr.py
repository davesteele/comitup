#!/usr/bin/python3
# Copyright (c) 2017-2018 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE

#
# Copyright 2017 David Steele <steele@debian.org>
# This file is part of comitup
# Available under the terms of the GNU General Public License version 2
# or later
#

from comitup import nm
from comitup import config


SINGLE_MODE = "single"
MULTI_MODE = "router"

CONF_PATH = "/etc/comitup.conf"


def dual_enabled():
    conf = config.Config(CONF_PATH, defaults={'enable_appliance_mode': 'true'})
    return conf.enable_appliance_mode == 'true'


def get_mode():
    if len(nm.get_wifi_devices()) > 1 and dual_enabled():
        return MULTI_MODE
    else:
        return SINGLE_MODE


def get_ap_device():
    return nm.get_wifi_device(0)


def get_link_device():
    second_device = nm.get_wifi_device(1)

    if second_device and dual_enabled():
        return second_device
    else:
        return nm.get_wifi_device(0)


def get_state_device(state):
    if state == 'HOTSPOT':
        return get_ap_device()
    else:
        return get_link_device()
