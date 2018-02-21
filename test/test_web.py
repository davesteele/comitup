
# Copyright (c) 2018 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2+
# License-Filename: LICENSE

import pytest
import urllib

from mock import patch, call, Mock

from web import comitupweb

ssid_list = [
    'simple',
    'simple+',
    'simplé',
    'simple 2',
]


@pytest.fixture
def app():
    app = comitupweb.create_app()
    app.debug = True
    app.testing = True
    return app


@pytest.mark.parametrize('ssid', ssid_list)
def test_webapp_null(app, ssid):
    assert 'simpl' in ssid


@pytest.mark.parametrize('ssid', ssid_list)
def test_webapp_index(app, ssid, monkeypatch):
    point = {
        'ssid': ssid,
    }
    points_mock = Mock(return_value = [point])
    monkeypatch.setattr('web.comitupweb.ciu.ciu_points', points_mock)

    response = app.test_client().get('/')
    index_text = response.get_data().decode()

    assert ssid + "</a>" in index_text
    assert "ssid=" + urllib.parse.quote(ssid) in index_text


@pytest.mark.parametrize('ssid', ssid_list)
def test_webapp_confirm(app, ssid, monkeypatch):
    quoted_ssid = urllib.parse.quote(ssid)
    url = "confirm?ssid={}&encrypted=encrypted".format(quoted_ssid)

    response = app.test_client().get(url)
    index_text = response.get_data().decode()

    assert "to " + ssid in index_text
    assert "value=\"" + urllib.parse.quote(ssid) in index_text



@pytest.mark.parametrize('ssid', ssid_list)
def test_webapp_confirm(app, ssid, monkeypatch):
    monkeypatch.setattr('web.comitupweb.Process', Mock())

    data = {
        'ssid': urllib.parse.quote(ssid),
        'password': urllib.parse.quote('password'),
    }
    response = app.test_client().post('connect', data=data)
    index_text = response.get_data().decode()

    assert "to " + ssid in index_text
