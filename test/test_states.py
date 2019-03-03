# Copyright (c) 2017-2019 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE

import pytest
from mock import Mock, call

from comitup import states


@pytest.fixture()
def state_globals(request):
    callbacks = states.state_callbacks

    def fin():
        states.state_callbacks = callbacks

    request.addfinalizer(fin)


@pytest.fixture()
def state_fxt(monkeypatch, state_globals):
    monkeypatches = (
        ('comitup.states.mdns.clear_entries',             None),
        ('comitup.states.mdns.add_hosts',                 None),

        ('comitup.states.nm.activate_connection_by_ssid', None),
        ('comitup.states.nm.get_candidate_connections',   ['c1', 'c2']),
        ('comitup.states.nm.get_active_ip',               '1.2.3.4'),
        ('comitup.states.nm.get_active_ssid',             None),
        ('comitup.states.nm.deactivate_connection',       None),

        ('comitup.states.nmmon.init_nmmon',               None),
        ('comitup.states.nmmon.set_device_callbacks',     None),

        ('comitup.states.timeout_add',                    None),

        ('comitup.states.time.sleep',                     None),
    )

    for path, return_val in monkeypatches:
        if return_val:
            monkeypatch.setattr(path, Mock(return_value=return_val))
        else:
            monkeypatch.setattr(path, Mock())

    monkeypatch.setattr('comitup.states.iwscan.ap_conn_count',
                        Mock(return_value=0))

    monkeypatch.setattr('comitup.states.modemgr.CONF_PATH', '/dev/null')

    states.set_hosts('hs', 'hs-1111')


@pytest.fixture()
def points_fxt(monkeypatch):
    pt = {
        'nmpath': '/',
        'ssid': 'ssid',
    }

    monkeypatch.setattr(
        'comitup.states.nm.get_points_ext',
        Mock(return_value=[pt])
    )

    return None


@pytest.mark.parametrize("offset, match", ((-1, False), (0, True), (1, False)))
def test_state_timeout_wrapper(offset, match):

    themock = Mock()

    @states.timeout
    def timeout_fn():
        themock()

    assert timeout_fn(states.state_id + offset) == match
    assert themock.called == match


def test_state_timeout_activity():
    themock = Mock()

    @states.timeout
    def timeout_fn():
        themock()

    timeout_fn(states.state_id)

    assert themock.called


def test_state_set_hosts():
    states.set_hosts('a', 'b')
    assert states.dns_names == ('a', 'b')


@pytest.mark.parametrize(
                "hostin, hostout",
                (('host', 'host'), ('host.local', 'host'))
             )
def test_state_dns_to_conn(hostin, hostout):
    assert states.dns_to_conn(hostin) == hostout


def test_state_callback_decorator(state_globals):
    callback = Mock()

    @states.state_callback
    def foo_bar():
        pass

    states.add_state_callback(callback)

    foo_bar()

    assert callback.call_args == call('FOO', 'bar')


def test_state_matrix():
    assert states.state_matrix('HOTSPOT').pass_fn == states.hotspot_pass


@pytest.mark.parametrize("path, good", (
    ("states.state_matrix('HOTSPOT').bogus_fn", False),
    ("states.state_matrix('HOTSPOT').bogus",    False),
    ("states.state_matrix('HOTSPOT').pass_fn",  True),))
def test_state_matrix_miss(path, good):
    if good:
        eval(path)
    else:
        with pytest.raises(AttributeError):
            eval(path)
