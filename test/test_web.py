# Copyright (c) 2018-2019 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE

import pathlib
import urllib
from unittest.mock import Mock

import pytest

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


def test_webapp_index(app, ssid, monkeypatch):
    comitupweb.ttl_cache.clear()

    point = {
        "ssid": ssid,
    }
    client_mock = Mock()
    client_mock.ciu_points.return_value = [point]
    monkeypatch.setattr("web.comitupweb.ciu_client", client_mock)
    # comitupweb.ciu_client = client_mock

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


@pytest.mark.parametrize("canblink", [True, False])
@pytest.mark.parametrize("path", ["/confirm"])
def test_webapp_blink_confirm(app, canblink, monkeypatch, path):
    monkeypatch.setattr("web.comitupweb.ciu.can_blink", lambda: canblink)
    monkeypatch.setattr("web.comitupweb.ciu.blink", Mock())
    monkeypatch.setattr("comitup.blink.set_trigger", Mock())
    monkeypatch.setattr("web.comitupweb.ciu_client", Mock())
    monkeypatch.setattr(
        "web.comitupweb.ciu_client.ciu_info",
        Mock(return_value={"imode": "single"}),
    )
    monkeypatch.setattr(
        "web.comitupweb.ciu_client.ciu_points", Mock(return_value=[])
    )

    response = app.test_client().get(path)
    blinktext = response.get_data().decode()

    assert canblink == ("Locate" in blinktext)


def test_webapp_blink(app, monkeypatch):
    monkeypatch.setattr("comitup.blink.set_trigger", Mock())
    monkeypatch.setattr("web.comitupweb.ciu.blink", Mock())
    response = app.test_client().get("/blink")

    assert response.status_code == 200
