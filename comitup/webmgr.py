

import logging

log = logging.getLogger('comitup')


COMITUP_SERVICE = 'comitup-web'

web_service = ""
port = "80"


def start_service(service):
    log.debug("starting %s web service", service)
    pass


def stop_service(service):
    log.debug("stopping %s web service", service)
    pass


callmatrix = {
    ('HOTSPOT',    'start'): (lambda: stop_service, lambda: web_service),
    ('HOTSPOT',     'pass'): (lambda: start_service, lambda: COMITUP_SERVICE),
    ('CONNECTING', 'start'): (lambda: stop_service, lambda: COMITUP_SERVICE),
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


def init_webmgr(web_service, port):
    pass
