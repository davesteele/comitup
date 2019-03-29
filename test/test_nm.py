import pytest
# Copyright (c) 2017-2019 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE
from mock import Mock, patch

from comitup import nm


@pytest.fixture()
def no_device_fxt(monkeypatch):
    monkeypatch.setattr("comitup.nm.nm.NetworkManager.GetDevices",
                        Mock(return_value=[]))
    return None


@pytest.fixture()
def device_no_conn_fxt(monkeypatch):
    device = Mock()
    device.ActiveConnection = None
    monkeypatch.setattr("comitup.nm.nm.NetworkManager.GetDevices",
                        Mock(return_value=[device]))
    return None


@pytest.fixture()
def device_fxt(monkeypatch):
    device = Mock()
    device.DeviceType = 2
    device.ActiveConnection.Connection.GetSettings.return_value = {
        '802-11-wireless': {
            'ssid': "myssid",
        }
    }
    device.Ip4Config.Addresses = [['1.2.3.4', '5.6.7.8', '1.2.3.1']]

    point = Mock()
    point.Ssid = "myssid"
    point.Strength = 100
    getAllAccessPoints = Mock()
    getAllAccessPoints.GetAllAccessPoints.return_value = [point]
    device.SpecificDevice.return_value = getAllAccessPoints

    monkeypatch.setattr("comitup.nm.nm.NetworkManager.GetDevices",
                        Mock(return_value=[device]))

    return None


@pytest.fixture()
def no_connections_fxt(monkeypatch):
    monkeypatch.setattr("comitup.nm.nm.Settings.ListConnections",
                        Mock(return_value=[]))
    return None


@pytest.fixture()
def connections_fxt(monkeypatch):
    connection = Mock()
    connection.GetSettings.return_value = {
        '802-11-wireless': {
            'ssid': "myssid",
        }
    }

    monkeypatch.setattr("comitup.nm.nm.Settings.ListConnections",
                        Mock(return_value=[connection]))

    return connection


def test_get_active_ssid(device_fxt):
    assert nm.get_active_ssid(nm.get_wifi_device()) == "myssid"


def test_get_active_ip(device_fxt):
    assert nm.get_active_ip(nm.get_wifi_device()) == '1.2.3.4'


def test_no_conn(no_connections_fxt):
    assert nm.get_connection_by_ssid('ssid') is None


def test_get_connection_by_ssid(connections_fxt):
    assert nm.get_connection_by_ssid("myssid")
    assert not nm.get_connection_by_ssid("bogusssid")


def test_del_connection_by_ssid(connections_fxt):
    nm.del_connection_by_ssid("myssid")
    assert connections_fxt.Delete.called


@patch('comitup.nm.get_wifi_device')
def test_activate_connection_by_id(get_dev, monkeypatch, connections_fxt):
    activate = Mock()
    monkeypatch.setattr("comitup.nm.nm.NetworkManager.ActivateConnection",
                        activate)

    nm.activate_connection_by_ssid("myssid", nm.get_wifi_device())
    assert activate.called


def test_make_hotspot(monkeypatch):
    addconnection = Mock()
    monkeypatch.setattr("comitup.nm.nm.Settings.AddConnection", addconnection)

    nm.make_hotspot()

    assert addconnection.called


def test_make_connection_for(monkeypatch):

    addconnection = Mock()
    monkeypatch.setattr("comitup.nm.nm.Settings.AddConnection", addconnection)

    nm.make_connection_for("anssid", "password")

    assert addconnection.called


def test_do_listaccess(device_fxt):
    nm.do_listaccess(None)
