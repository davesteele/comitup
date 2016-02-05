

import pytest
from mock import Mock, patch
from comitup import nmmon


@pytest.fixture()
def nmmon_con_fxt(request):

    def fin():
        nmmon.nm_dev_connect = nmmon.null_fn
        nmmon.nm_dev_fail = nmmon.null_fn

    request.addfinalizer(fin)


def test_nmmon_null_init():
    nmmon.nm_dev_connect()
    nmmon.nm_dev_fail()
    nmmon.null_fn()


def test_nmmon_set_callbacks(nmmon_con_fxt):
    nmmon.set_device_callbacks(1, 2)

    assert nmmon.nm_dev_connect == 1
    assert nmmon.nm_dev_fail == 2


@pytest.mark.parametrize("state, pass_called, fail_called", (
                             (90,  False, False),
                             (100, True,  False),
                             (120, False, True),
                         ))
@patch('comitup.nmmon.nm_dev_connect')
@patch('comitup.nmmon.nm_dev_fail')
def test_nmmon_dev_change(fail_fn, connect_fn,
                          state, pass_called, fail_called):

    nmmon.nm_device_change(state)

    assert connect_fn.called == pass_called
    assert fail_fn.called == fail_called


@pytest.fixture()
def bus_fxt(request):
    bus_save = nmmon.bus
    nmmon.bus = Mock()

    def fin():
        nmmon.bus = bus_save

    request.addfinalizer(fin)

    return nmmon.bus.add_signal_receiver


def test_nmmon_set_listener(bus_fxt):
    nmmon.set_device_listener('apath')

    assert bus_fxt.called


def test_nmmon_check_listener(bus_fxt, devpath_fxt):
    nmmon.check_device_listener()

    assert bus_fxt.called


@pytest.fixture()
def devpath_fxt(request):
    dev_save = nmmon.device_path

    def fin():
        nmmon.device_path = dev_save

    request.addfinalizer(fin)


@pytest.mark.parametrize('state, called', ((0, False,), (100, True)))
def test_nmmon_state_change(bus_fxt, devpath_fxt, state, called):
    nmmon.nm_state_change(state)

    assert bus_fxt.called == called


def test_nmmon_set_nm_listeners(bus_fxt):
    nmmon.set_nm_listeners()

    assert bus_fxt.called


def test_nmmon_init(bus_fxt):
    nmmon.init_nmmon()

    assert bus_fxt.called
