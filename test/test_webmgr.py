# Copyright (c) 2017-2019 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE

from unittest.mock import patch

import pytest

from comitup import webmgr


@pytest.fixture()
def websvc_fxt(request):
    web_svc = webmgr.web_service

    def fin():
        webmgr.web_service = web_svc

    request.addfinalizer(fin)


@pytest.mark.parametrize(
    "state, action, fn_fact, arg_fact",
    (
        (
            "HOTSPOT",
            "start",
            lambda: webmgr.stop_service,
            lambda: webmgr.web_service,
        ),  # noqa
        (
            "HOTSPOT",
            "pass",
            lambda: webmgr.start_service,
            lambda: webmgr.COMITUP_SERVICE,
        ),  # noqa
        (
            "CONNECTING",
            "start",
            lambda: webmgr.stop_service,
            lambda: webmgr.COMITUP_SERVICE,
        ),  # noqa
        (
            "CONNECTED",
            "start",
            lambda: webmgr.start_service,
            lambda: webmgr.web_service,
        ),  # noqa
    ),
)  # noqa
@pytest.mark.parametrize("svc", ("", "foo"))
@patch("comitup.webmgr.start_service")
@patch("comitup.webmgr.stop_service")
def test_webmgr_callback(
    stop_svc, start_svc, svc, state, action, fn_fact, arg_fact, websvc_fxt
):
    webmgr.web_service = svc
    webmgr.state_callback(state, action)

    if arg_fact():
        assert fn_fact().called
    else:
        assert not fn_fact().called

    if svc:
        assert fn_fact().called


others = [
    (x, y)
    for x in ("HOTSPOT", "CONNECTING", "CONNECTED")
    for y in ("fail", "timeout")
]  # noqa


@pytest.mark.parametrize(
    "state, action",
    [
        ("CONNECTING", "pass"),
        ("CONNECTED", "pass"),
    ]
    + others,
)
@patch("comitup.webmgr.start_service")
@patch("comitup.webmgr.stop_service")
def test_webmgr_no_callback(stop_svc, start_svc, state, action, websvc_fxt):
    webmgr.web_service = "foo"
    webmgr.state_callback(state, action)

    assert not stop_svc.called
    assert not start_svc.called
