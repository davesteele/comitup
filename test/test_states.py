
from comitup import states
import pytest
from mock import Mock


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

    states.sethosts('hs', 'hs-1111')


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


@pytest.mark.parametrize("match", (False, True))
def test_state_timeout_wrapper(match):

    @states.timeout
    def timeout_fn():
        pass

    if match:
        assert timeout_fn(states.state_id) == match
    else:
        assert timeout_fn(states.state_id + 1) == match
