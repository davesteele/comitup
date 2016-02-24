

import pytest

from mock import Mock, patch, call

from comitup import webmgr


def test_webmgr_callback_target():
    assert webmgr.callback_target() == webmgr.state_callback




@pytest.mark.parametrize("state, action, start_arg, stop_arg", (
    ('HOTSPOT',    'pass',  "comitup-web",      None),
    ('CONNECTING', 'start', None,               "comitup-web"),
))
@patch('comitup.webmgr.start_service')
@patch('comitup.webmgr.stop_service')
def test_webmgr_callback(stop_svc, start_svc, state, action, start_arg,
                           stop_arg):
    webmgr.state_callback(state, action)

    if start_arg is not None:
        assert start_svc.call_args == call(start_arg)

    if stop_arg is not None:
        assert stop_svc.call_args == call(stop_arg)


@pytest.fixture()
def websvc_fxt(request):
    web_svc = webmgr.web_service

    def fin():
        webmgr.web_service = web_svc

    request.addfinalizer(fin)


@pytest.mark.parametrize("state, action, start_arg, stop_arg", (
    ('HOTSPOT',    'start', None,               'foo'),
    ('CONNECTED',  'start', webmgr.web_service, None),
))
@pytest.mark.parametrize("svc", ("", "foo"))
@patch('comitup.webmgr.start_service')
@patch('comitup.webmgr.stop_service')
def test_webmgr_callback2(stop_svc, start_svc, state, action, start_arg,
                           stop_arg, websvc_fxt, svc):

    webmgr.web_service = svc
    webmgr.state_callback(state, action)


    if start_arg and svc:
        assert start_svc.call_args == call(start_arg)

    if start_arg and not svc:
        assert start_svc.call_args == None

    if stop_arg and svc:
        assert stop_svc.call_args == call(stop_arg)

    if stop_arg and not svc:
        assert stop_svc.call_args == None

