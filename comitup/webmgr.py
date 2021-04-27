
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

import logging
from typing import Callable

from .sysd import sd_start_unit, sd_stop_unit

log: logging.Logger = logging.getLogger('comitup')

COMITUP_SERVICE: str = 'comitup-web.service'

web_service: str = ""


def start_service(service: str) -> None:
    log.debug("starting %s web service", service)
    sd_start_unit(service, 'replace')


def stop_service(service: str) -> None:
    log.debug("stopping %s web service", service)
    sd_stop_unit(service, 'replace')


callmatrix = {
    ('HOTSPOT',    'start'): (lambda: stop_service, lambda: web_service),
    ('HOTSPOT',     'pass'): (lambda: start_service, lambda: COMITUP_SERVICE),
    ('CONNECTING', 'start'): (lambda: stop_service, lambda: COMITUP_SERVICE),
    ('CONNECTED',  'start'): (lambda: start_service, lambda: web_service),
}


def state_callback(state: str, action: str) -> None:
    try:
        (fn_fact, svc_fact) = callmatrix[(state, action)]
    except KeyError:
        return

    if svc_fact():
        fn_fact()(svc_fact())


def callback_target() -> Callable[[str, str], None]:
    return state_callback


def init_webmgr(web_svc: str) -> None:
    global web_service

    stop_service(COMITUP_SERVICE)

    web_service = web_svc

    log.debug("web service is %s" % web_service)
