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

ap_device = None
link_device = None


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
    global ap_device

    if not ap_device:
        devs = nm.get_wifi_devices()
        spec = get_conf().primary_wifi_device

        if spec:
            for dev in devs:
                if dev.Interface == spec:
                    ap_device = dev

    if not ap_device:
        ap_device = devs[0]

    return ap_device


def get_link_device():
    global link_device

    if not link_device:
        devs = nm.get_wifi_devices()
        link_device = get_ap_device()

        if dual_enabled():
            for dev in devs:
                if dev.Interface != link_device.Interface:
                    link_device = dev
                    return link_device

    return link_device


def get_state_device(state):
    if state == 'HOTSPOT':
        return get_ap_device()
    else:
        return get_link_device()
