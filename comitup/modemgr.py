#!/usr/bin/python

#
# Copyright 2017 David Steele <steele@debian.org>
# This file is part of comitup
# Available under the terms of the GNU General Public License version 2
# or later
#

import nm


SINGLE_MODE = "single"
MULTI_MODE = "router"


def get_mode():
    if len(nm.get_wifi_devices()) > 1:
        return MULTI_MODE
    else:
        return SINGLE_MODE


def get_ap_device():
    return nm.get_wifi_device(0)


def get_link_device():
    second_device = nm.get_wifi_device(1)

    if second_device:
        return second_device
    else:
        return nm.get_wifi_device(0)


def get_state_device(state):
    if state == 'HOTSPOT':
        return get_ap_device()
    else:
        return get_link_device()


