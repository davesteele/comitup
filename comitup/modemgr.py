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

from typing import Optional, TYPE_CHECKING

from comitup import config, nm

if TYPE_CHECKING:
    import NetworkManager

SINGLE_MODE: str = "single"
MULTI_MODE: str = "router"

CONF_PATH: str = "/etc/comitup.conf"

conf: Optional[config.Config] = None

ap_device: Optional["NetworkManager.Device"] = None
link_device: Optional["NetworkManager.Device"] = None


def get_conf() -> config.Config:
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


def dual_enabled() -> bool:
    return get_conf().enable_appliance_mode == 'true'


def get_mode() -> str:
    if len(nm.get_wifi_devices()) > 1 and dual_enabled():
        return MULTI_MODE
    else:
        return SINGLE_MODE


def get_ap_device() -> "NetworkManager.Device":
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

    if ap_device:
        return ap_device
    else:
        raise


def get_link_device() -> "NetworkManager.Device":
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


def get_state_device(state: str) -> "NetworkManager.Device":
    if state == 'HOTSPOT':
        return get_ap_device()
    else:
        return get_link_device()
