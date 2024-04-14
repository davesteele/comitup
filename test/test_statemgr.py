# Copyright (c) 2017-2019 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE

import importlib
from collections import namedtuple
from unittest.mock import Mock

import dbus.service
import pytest


def nullwrapper(*args, **kwargs):
    def _nullwrapper(fn):
        def wrapper(*wargs, **wkwargs):
            return fn(*wargs, **wkwargs)

        return wrapper

    return _nullwrapper


dbus.service.method = nullwrapper

sm = importlib.import_module("comitup.statemgr")


@pytest.fixture()
def statemgr_fxt(monkeypatch, request):
    monkeypatch.setattr("dbus.service.BusName", Mock())
    monkeypatch.setattr("dbus.service.Object", Mock())
    monkeypatch.setattr("dbus.service.Object", Mock())

    save_state = sm.states.com_state
    save_conn = sm.states.connection

    def fin():
        sm.states.com_state = save_state
        sm.states.connection = save_conn

    request.addfinalizer(fin)

    sm.states.com_state = "CONNECTED"
    sm.states.connection = "connection"


def test_sm_none(statemgr_fxt):
    pass


def test_sm_state(statemgr_fxt):
    obj = sm.Comitup()
    assert obj.state() == ["CONNECTED", "connection"]


@pytest.fixture()
def ap_name_fxt(monkeypatch):
    monkeypatch.setattr("socket.gethostname", Mock(return_value="host"))

    return None


Case = namedtuple("Case", ["input", "out"])


@pytest.mark.parametrize(
    "case",
    [
        Case("comitup-<nnn>", "comitup-123"),
        Case("<n>", "1"),
        Case("<nn>", "12"),
        Case("<nnn>", "123"),
        Case("<nnnn>", "1234"),
        Case("<nnnnn>", "<nnnnn>"),
        Case("A<n>", "A1"),
        Case("<n>A", "1A"),
        Case("<hostname>", "host"),
        Case("<hostname>-<n>", "host-1"),
        Case("<bogus>", "<bogus>"),
    ],
)
def test_expand_ap(ap_name_fxt, case):
    assert sm.expand_ap(case.input, "1234") == case.out
