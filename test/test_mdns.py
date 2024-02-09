import pytest
from mock import Mock, patch

from comitup import mdns

# Copyright (c) 2017-2019 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE


@pytest.fixture()
def avahi_fxt(monkeypatch, request):
    monkeypatch.setattr("comitup.mdns.dbus.Interface", Mock())
    monkeypatch.setattr("comitup.mdns.dbus.SystemBus", Mock())
    monkeypatch.setattr("comitup.mdns.log", Mock())
    monkeypatch.setattr("comitup.mdns.config.persist", Mock())

    save_group = mdns.group
    mdns.group = Mock()

    yield None

    mdns.group = save_group


def test_avahi_null(avahi_fxt):
    pass


def test_avahi_establish_group(avahi_fxt):
    old_group = mdns.group
    mdns.group = None
    mdns.establish_group()
    assert mdns.group is not None
    mdns.group = old_group


def test_avahi_make_a_record(avahi_fxt):
    mdns.make_a_record("host", 1, "1.2.3.4")
    assert mdns.group.AddRecord.called  # type: ignore


def test_avahi_add_service(avahi_fxt):
    mdns.add_service("host", 1, "1.2.3.4", "::1")
    assert mdns.group.AddService.called  # type: ignore


@patch("comitup.mdns.establish_group", Mock())
def test_avahi_clear_entries(avahi_fxt):
    isempty = Mock(return_value=False)
    mdns.group = Mock()
    mdns.group.IsEmpty = isempty

    oldgroup = mdns.group

    mdns.clear_entries()

    assert isempty.called
    assert oldgroup.Reset.called
    assert not mdns.log.called  # type: ignore


@pytest.mark.parametrize(
    "dns_in, dns_out",
    (
        ("a.b.c", "a.b.c".encode()),
        ("A.B.C", "A.B.C".encode()),
        ("a..b", "a.b".encode()),
        ("a.b.", "a.b".encode()),
    ),
)
def test_avahi_encode_dns(dns_in, dns_out):
    assert dns_out == mdns.encode_dns(dns_in)


@patch("comitup.mdns.log.warn")
def test_avahi_clear_fail(warn, avahi_fxt):
    mdns.group = None
    mdns.clear_entries()
