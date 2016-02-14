
from comitup import states
import pytest
from mock import Mock, patch


@pytest.fixture()
def state_fxt(monkeypatch):
    monkeypatch.setattr('comitup.states.mdns.clear_entries', Mock())
    monkeypatch.setattr('comitup.states.mdns.add_hosts', Mock())

    monkeypatch.setattr('comitup.states.nm.activate_connection_by_ssid',
                        Mock())
    monkeypatch.setattr('comitup.states.nm.get_candidate_connections',
                        Mock(return_value=['c1', 'c2']))
    monkeypatch.setattr('comitup.states.nm.get_active_ip',
                        Mock(return_value='1.2.3.4'))
    monkeypatch.setattr('comitup.states.nm.get_active_ssid', Mock())

    monkeypatch.setattr('comitup.states.nmmon.init_nmmon', Mock())
    monkeypatch.setattr('comitup.states.nmmon.set_device_callbacks', Mock())

    monkeypatch.setattr('comitup.states.gobject.timeout_add', Mock())

    monkeypatch.setattr('comitup.states.nm.get_points_ext',
                        Mock(return_value=[]))

    monkeypatch.setattr('comitup.states.nm.deactivate_connection',
                        Mock())

    monkeypatch.setattr('comitup.states.time.sleep', Mock())

    states.set_hosts('hs', 'hs-1111')


@pytest.mark.parametrize(
    "state, action, end_state, conn, conn_list",
    (
        ('hotspot',       'pass',    'HOTSPOT', 'hs', []),
        ('hotspot',       'fail',    'HOTSPOT', 'hs', []),
        ('hotspot',    'timeout', 'CONNECTING', 'c1', ['c2']),
        ('connecting',    'pass',  'CONNECTED', 'c1', []),
        ('connecting',    'fail', 'CONNECTING', 'c2', []),
        ('connecting', 'timeout', 'CONNECTING', 'c2', []),
        # note - the null connection is a test side-effect
        ('connected',     'pass',  'CONNECTED', '',   []),
        ('connected',     'fail',    'HOTSPOT', 'hs', []),
        ('connected',  'timeout',    'HOTSPOT', 'hs', []),
    )
)
@pytest.mark.parametrize("thetest", ('end_state', 'conn', 'conn_list'))
def test_state_transition(thetest, state, action, end_state,
                          conn, conn_list, state_fxt):
    action_fn = states.__getattribute__(state + "_" + action)

    states.connection = ''

    if state == 'connecting':
        states.set_state(state.upper(), ['c1', 'c2'])
    else:
        states.set_state(state.upper())

    if action == 'timeout':
        action_fn(states.state_id)
    else:
        action_fn()

    if thetest == 'end_state':
        assert states.com_state == end_state
    elif thetest == 'conn':
        assert states.connection == conn
    elif thetest == 'conn_list':
        assert states.conn_list == conn_list


def test_state_transition_cleanup(state_fxt):
    states.connection = 'c1'

    states.set_state('CONNECTING', ['c1'])
    states.connecting_fail()

    assert states.com_state == 'HOTSPOT'


def test_state_transition_no_connections(state_fxt):
    states.connection = 'hs'

    states.set_state('CONNECTING', [])
#    states.connecting_fail()

    assert states.com_state == 'HOTSPOT'


@pytest.mark.parametrize("offset, match", ((-1, False), (0, True), (1, False)))
def test_state_timeout_wrapper(offset, match):

    themock = Mock()

    @states.timeout
    def timeout_fn():
        themock()

    assert timeout_fn(states.state_id + offset) == match
    assert themock.called == match


@pytest.mark.parametrize("times, called", (((1, 1000), True), ((2, 3), False)))
@patch('comitup.states.time.time')
def test_state_timeout_activity(tmmock, times, called):
    themock = Mock()

    @states.timeout
    def timeout_fn():
        themock()

    tmmock.side_effect = times

    states.set_activity()
    timeout_fn(states.state_id)

    assert states.last_activity == times[0]
    assert themock.called == called


def test_state_set_hosts():
    states.set_hosts('a', 'b')
    assert states.dns_names == ('a', 'b')


@patch('comitup.states.nmmon.init_nmmon')
def test_state_init_states(init_nmmon):
    states.init_states('c', 'd')
    assert states.dns_names == ('c', 'd')


@pytest.mark.parametrize("hostin, hostout", (('host', 'host'), ('host.local', 'host')))
def test_state_dns_to_conn(hostin, hostout):
    assert states.dns_to_conn(hostin) == hostout
