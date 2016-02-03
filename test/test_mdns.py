import pytest

from comitup import mdns
from mock import Mock, patch


@pytest.fixture()
def avahi_fxt(monkeypatch):
    monkeypatch.setattr("comitup.mdns.dbus.Interface", Mock())
    monkeypatch.setattr('comitup.mdns.dbus.SystemBus', Mock())
    monkeypatch.setattr('comitup.mdns.log', Mock())

    return None


def test_avahi_null(avahi_fxt):
    pass


def test_avahi_establish_group(avahi_fxt):
    assert not mdns.server
    assert not mdns.group

    mdns.establish_group()

    assert mdns.server
    assert mdns.group


def test_avahi_make_a_record(avahi_fxt):
    mdns.make_a_record('host', '1.2.3.4')
    assert mdns.group.AddRecord.called


def test_avahi_add_service(avahi_fxt):
    mdns.add_service('host')
    assert mdns.group.AddService.called


@patch('comitup.mdns.establish_group', Mock())
def test_avahi_clear_entries(avahi_fxt):
    isempty = Mock(return_value=False)
    mdns.group = Mock()
    mdns.group.IsEmpty = isempty

    mdns.clear_entries()

    assert isempty.called
    assert mdns.group.Reset.called
    assert mdns.establish_group.called
    assert not mdns.log.called


def test_avahi_add_hosts(avahi_fxt):
    mdns.add_hosts(['host1', 'host2'], '1.2.3.4')

    assert mdns.group.Commit.called
