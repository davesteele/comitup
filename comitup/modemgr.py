#!/usr/bin/python3
# Copyright (c) 2017-2019 David Steele <dsteele@gmail.com>
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

conf = None


def get_conf():
    global conf

    if not conf:
        conf = config.Config(
                CONF_PATH,
                defaults={
                    'enable_appliance_mode': 'true',
                    'primary_wifi_device': '',
                    }
                )

    return conf


def dual_enabled():
    return get_conf().enable_appliance_mode == 'true'


def get_mode():
    if len(nm.get_wifi_devices()) > 1 and dual_enabled():
        return MULTI_MODE
    else:
        return SINGLE_MODE


def get_ap_device():
    devs = nm.get_wifi_devices()
    spec = get_conf().primary_wifi_device

    if spec:
        for dev in devs:
            if dev.Interface == spec:
                return dev

    return devs[0]


def get_link_device():
    devs = nm.get_wifi_devices()
    ap = get_ap_device()

    if dual_enabled:
        for dev in devs:
            if dev.Interface != ap.Interface:
                return dev

    return ap


def get_state_device(state):
    if state == 'HOTSPOT':
        return get_ap_device()
    else:
        return get_link_device()
