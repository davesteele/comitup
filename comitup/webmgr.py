

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


def state_callback(state, action):
    if (state, action) == ('HOTSPOT', 'start'):
        if web_service:
            stop_service(web_service)
    elif (state, action) == ('HOTSPOT', 'pass'):
        start_service(COMITUP_SERVICE)
    elif (state, action) == ('CONNECTING', 'start'):
        stop_service(COMITUP_SERVICE)
    elif (state, action) == ('CONNECTED', 'start'):
        if web_service:
            start_service(web_service)


def callback_target():
    return state_callback


def init_webmgr(web_service, port):
    pass
