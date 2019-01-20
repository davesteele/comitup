
# Copyright (c) 2017-2019 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE

import pytest
from mock import Mock
import importlib

import dbus.service


def nullwrapper(*args, **kwargs):
    def _nullwrapper(fn):
        def wrapper(*wargs, **wkwargs):
            return fn(*wargs, **wkwargs)

        return wrapper
    return _nullwrapper


dbus.service.method = nullwrapper

sm = importlib.import_module('comitup.statemgr')


@pytest.fixture()
def statemgr_fxt(monkeypatch, request):
    monkeypatch.setattr('dbus.service.BusName', Mock())
    monkeypatch.setattr('dbus.service.Object', Mock())
    monkeypatch.setattr('dbus.service.Object', Mock())

    save_state = sm.states.com_state
    save_conn = sm.states.connection

    def fin():
        sm.states.com_state = save_state
        sm.states.connection = save_conn

    request.addfinalizer(fin)

    sm.states.com_state = "CONNECTED"
    sm.states.connection = 'connection'


def test_sm_none(statemgr_fxt):
    pass


def test_sm_state(statemgr_fxt):
    obj = sm.Comitup()
    assert obj.state() == ['CONNECTED', 'connection']
