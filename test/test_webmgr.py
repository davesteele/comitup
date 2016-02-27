

import pytest

from mock import patch, call

from comitup import webmgr


def test_webmgr_callback_target():
    assert webmgr.callback_target() == webmgr.state_callback


@pytest.fixture()
def websvc_fxt(request):
    web_svc = webmgr.web_service

    def fin():
        webmgr.web_service = web_svc

    request.addfinalizer(fin)


@pytest.mark.parametrize("state, action, fn_fact, arg_fact", (
    ('HOTSPOT',    'start', lambda: webmgr.stop_service,
                            lambda: webmgr.web_service),        # noqa
    ('HOTSPOT',     'pass', lambda: webmgr.start_service,
                            lambda: webmgr.COMITUP_SERVICE),
    ('CONNECTING', 'start', lambda: webmgr.stop_service,
                            lambda: webmgr.COMITUP_SERVICE),
    ('CONNECTED',  'start', lambda: webmgr.start_service,
                            lambda: webmgr.web_service),
))
@pytest.mark.parametrize("svc", ("", "foo"))
@patch('comitup.webmgr.start_service')
@patch('comitup.webmgr.stop_service')
def test_webmgr_callback(stop_svc, start_svc, svc, state, action,
                         fn_fact, arg_fact, websvc_fxt):
    webmgr.web_service = svc
    webmgr.state_callback(state, action)

    if arg_fact():
        assert fn_fact().called
        assert fn_fact().called_with(call(arg_fact()))
    else:
        assert not fn_fact().called

    if svc:
        assert fn_fact().called
