# Copyright (c) 2018-2019 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE

import pathlib
import urllib

import pytest
from mock import Mock

from web import comitupweb

ssid_list = [
    "simple",
    "simple+",
    "simplé",
    "simple 2",
    "simplE",
]


@pytest.fixture(params=ssid_list)
def ssid(request):
    return request.param


@pytest.fixture
def app(monkeypatch):
    templatedir = pathlib.Path(__file__).parent.parent / "web/templates"
    monkeypatch.setattr("web.comitupweb.TEMPLATE_PATH", str(templatedir))

    app = comitupweb.create_app(Mock())
    app.debug = True
    app.testing = True
    return app


def test_webapp_null(app, ssid):
    assert "simpl" in ssid


def test_webapp_index(app, ssid):
    point = {
        "ssid": ssid,
    }
    client_mock = Mock()
    client_mock.ciu_points.return_value = [point]
    comitupweb.ciu_client = client_mock

    response = app.test_client().get("/")
    index_text = response.get_data().decode()

    assert ssid + "</button>" in index_text
    assert "ssid=" + urllib.parse.quote(ssid) in index_text


def test_webapp_connect(app, ssid, monkeypatch):
    monkeypatch.setattr("web.comitupweb.Process", Mock())

    data = {
        "ssid": urllib.parse.quote(ssid),
        "password": urllib.parse.quote("password"),
    }
    response = app.test_client().post("connect", data=data)
    index_text = response.get_data().decode()

    assert "to " + ssid in index_text
