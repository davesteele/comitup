# Copyright (c) 2022 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE
#

import textwrap
from unittest.mock import Mock

import pytest

from comitup import routemgr

routetxt = textwrap.dedent(
    """
        default via 192.168.200.1 dev ethn proto dhcp src 192.168.200.27
        default via 192.168.200.1 dev wlan1 proto dhcp src 192.168.200.177
        10.41.0.0/24 dev wlan0 proto kernel scope link src 10.41.0.1
        169.254.0.0/16 dev wlan0 scope link src 169.254.30.217 metric 303
        192.168.200.0/24 dev eth0 proto dhcp scope link src 192.168.200.27
        192.168.200.0/24 dev wlan1 proto dhcp scope link src 192.168.200.177
    """
).strip()


@pytest.fixture
def defroute(monkeypatch):
    cp = Mock()
    cp.stdout = routetxt
    runmethod = Mock(return_value=cp)
    monkeypatch.setattr("comitup.routemgr.subprocess.run", runmethod)


def test_defroute_fixture(defroute):
    cp = routemgr.subprocess.run(
        "ip route",
        stdout=routemgr.subprocess.PIPE,
        shell=True,
        encoding="utf-8",
    )
    assert "ethn" in cp.stdout


def test_default_dev(defroute):
    assert routemgr.defroute_dev() == "ethn"
