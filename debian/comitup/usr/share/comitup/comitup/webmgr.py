
# Copyright (c) 2017-2018 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2+
# License-Filename: LICENSE
#
# Copyright 2016-2017 David Steele <steele@debian.org>
# This file is part of comitup
# Available under the terms of the GNU General Public License version 2
# or later
#

import logging
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

log = logging.getLogger('comitup')


COMITUP_SERVICE = 'comitup-web.service'

web_service = ""


def start_service(service):
    log.debug("starting %s web service", service)
    sd_start_unit(service, 'replace')


def stop_service(service):
    log.debug("stopping %s web service", service)
    sd_stop_unit(service, 'replace')


callmatrix = {
    ('HOTSPOT',    'start'): (lambda: stop_service, lambda: web_service),
    ('HOTSPOT',     'pass'): (lambda: start_service, lambda: COMITUP_SERVICE),
    ('CONNECTING',  'pass'): (lambda: stop_service, lambda: COMITUP_SERVICE),
    ('CONNECTED',  'start'): (lambda: start_service, lambda: web_service),
}


def state_callback(state, action):
    try:
        (fn_fact, svc_fact) = callmatrix[(state, action)]
    except KeyError:
        return

    if svc_fact():
        fn_fact()(svc_fact())


def callback_target():
    return state_callback


def init_webmgr(web_svc):
    global web_service

    web_service = web_svc
