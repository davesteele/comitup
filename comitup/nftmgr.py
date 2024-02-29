# Copyright (c) 2017-2019 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE
#
# Copyright 2017 David Steele <steele@debian.org>
# This file is part of comitup
# Available under the terms of the GNU General Public License version 2
# or later
#

import logging
import subprocess
from typing import List, Optional

from comitup import modemgr, nm, routemgr

log: logging.Logger = logging.getLogger("comitup")


def start_hs_rules() -> None:
    # fmt: off
    start_cmds: List[str] = [
        "nft add table ip filter",
        "nft 'add chain ip filter COMITUP-OUT {{ type filter hook output priority 100 ; }}'",
        "nft 'add rule ip filter COMITUP-OUT icmp type destination-unreachable counter drop' ",
        "nft 'add rule ip filter COMITUP-OUT icmp code port-unreachable counter drop' ",
        "nft 'add rule ip filter COMITUP-OUT counter return'",
    ]
    # fmt: on

    ap_dev = nm.device_name(modemgr.get_ap_device())
    run_cmds(start_cmds, ap=ap_dev)


def stop_hs_rules() -> None:
    # fmt: off
    end_cmds: List[str] = [
        "nft flush chain ip filter COMITUP-OUT  >/dev/null 2>&1",
        "nft delete chain ip filter COMITUP-OUT > /dev/null 2>&1",
    ]
    # fmt: on

    run_cmds(end_cmds)


def start_router_rules() -> None:
    # fmt: off
    appliance_cmds: List[str] = [
        "nft add table ip nat",
        "nft 'add chain nat COMITUP-FWD {{ type nat hook postrouting priority 100 ; }}'",
        "nft 'add rule ip nat COMITUP-FWD oifname {link} counter masquerade'",
        "nft 'add rule ip nat COMITUP-FWD counter return'",
        "echo 1 > /proc/sys/net/ipv4/ip_forward",
    ]
    # fmt: on

    link_dev = nm.device_name(modemgr.get_link_device())
    run_cmds(appliance_cmds, link=link_dev)


def stop_router_rules() -> None:
    # fmt: off
    appliance_clear: List[str] = [
        "nft flush chain ip nat COMITUP-FWD > /dev/null 2>&1",
        "nft delete chain ip nat COMITUP-FWD > /dev/null 2>&1",
    ]
    # fmt: on

    run_cmds(appliance_clear)


def run_cmds(cmds: List[str], **vars) -> None:
    linkdev = nm.device_name(modemgr.get_link_device())
    vars["link"] = linkdev
    apdev = nm.device_name(modemgr.get_ap_device())
    vars["ap"] = apdev
    for cmd in cmds:
        runcmd = cmd.format(**vars)
        log.debug(f'nftmgr - running "{runcmd}"')
        subprocess.call(runcmd, shell=True)


def state_callback(state: str, action: str) -> None:
    if (state, action) == ("HOTSPOT", "start"):
        log.debug("nftmgr - Running nft commands for HOTSPOT")

        stop_hs_rules()
        start_hs_rules()

        if modemgr.get_mode() == modemgr.MULTI_MODE:
            stop_router_rules()

        log.debug("nftmgr - Done with nft commands for HOTSPOT")

    elif (state, action) == ("CONNECTED", "start"):
        log.debug("nftmgr - Running nft commands for CONNECTED")
        stop_hs_rules()

        if modemgr.get_mode() == modemgr.MULTI_MODE:
            stop_router_rules()
            start_router_rules()

            defaultdev: Optional[str] = routemgr.defroute_dev()
            apdev: str = modemgr.get_ap_device().Interface
            if defaultdev and defaultdev != apdev:
                run_cmds(
                    [
                        f"nft 'insert rule ip nat COMITUP-FWD oifname \"{defaultdev}\" counter masquerade'"
                    ],
                )

        log.debug("nftmgr - Done with nft commands for CONNECTED")


def init_nftmgr() -> None:
    pass
