import pytest

from comitup import mdns
from mock import Mock, patch


@pytest.fixture()
def avahi_fxt(monkeypatch, request):
    monkeypatch.setattr("comitup.mdns.dbus.Interface", Mock())
    monkeypatch.setattr('comitup.mdns.dbus.SystemBus', Mock())
    monkeypatch.setattr('comitup.mdns.log', Mock())

    save_group = mdns.group
    mdns.group = Mock()

    def fin():
        mdns.group = save_group

    request.addfinalizer(fin)

    return None


def test_avahi_null(avahi_fxt):
    pass


def test_avahi_establish_group(avahi_fxt):
    old_group = mdns.group
    mdns.establish_group()
    assert mdns.group != old_group


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


@pytest.mark.parametrize("dns_in, dns_out", (
    ("a.b.c", "a.b.c"),
    ("A.B.C", "A.B.C"),
    ("a..b", "a.b"),
    ("a.b.", "a.b"),
))
def test_avahi_encode_dns(dns_in, dns_out):
    assert dns_out == mdns.encode_dns(dns_in)


@patch('comitup.mdns.log.warn')
def test_avahi_clear_fail(warn, avahi_fxt):
    mdns.group = None
    mdns.clear_entries()
    assert warn.called
