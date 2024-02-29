#!/usr/bin/python3
# Copyright (c) 2017-2019 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE


import logging
import os
import re
import subprocess
import textwrap
from collections import namedtuple
from typing import List, Optional, Tuple

log = logging.getLogger("comitup")


class DevInfo(object):
    def __init__(self, primary_dev: str = ""):
        self.dev_list: List[Tuple[str, str]] = []
        for dev in os.listdir("/sys/class/net"):
            try:
                path = "/sys/class/net/{}/phy80211/name".format(dev)
                with open(path, "r") as fp:
                    phy = fp.read().strip()

                if dev == primary_dev:
                    self.dev_list.insert(0, (dev, phy))
                else:
                    self.dev_list.append((dev, phy))
            except (NotADirectoryError, FileNotFoundError):
                pass

    def get_devs(self) -> List[str]:
        return [x[0] for x in self.dev_list]

    def get_phy(self, dev: str) -> str:
        return [x[1] for x in self.dev_list if x[0] == dev][0]


dev_info: DevInfo = DevInfo()


def device_present() -> Optional[str]:
    if dev_info.get_devs():
        return None
    else:
        # Fail without comment
        return ""


def device_supports_ap() -> Optional[str]:
    dev: str

    for dev in dev_info.get_devs():
        phy: str = dev_info.get_phy(dev)

        try:
            cmd: str = "iw phy {} info".format(phy)
            deviceinfo: str = subprocess.check_output(cmd.split()).decode()
        except subprocess.CalledProcessError:
            return ""

        if "* AP\n" in deviceinfo:
            return None

    return ""


def device_nm_managed() -> Optional[str]:
    try:
        cmd: str = "nmcli device show"
        try:
            devsinfo: str = subprocess.check_output(
                cmd.split(), re.MULTILINE
            ).decode()
        except UnicodeDecodeError:
            # shouldn't happen, but it does. Move on
            return None

        for dev in dev_info.get_devs():
            if dev not in devsinfo:
                # Fail without comment
                return ""
    except subprocess.CalledProcessError:
        pass

    return None


testspec = namedtuple("testspec", ["testfn", "title", "description"])


testspecs = [
    testspec(
        device_present,
        "comitup-no-wifi - No wifi devices found",
        textwrap.dedent(
            """
            Comitup is a wifi device manager. 'sudo iw list' indicates that
            there are no devices to manage.
        """
        ),
    ),
    testspec(
        device_supports_ap,
        "comitup-no-ap - The Main wifi device doesn't support AP mode",
        textwrap.dedent(
            """
            Comitup uses the first wifi device to implement the comitup-<nnn>
            Access Point. For this to work, the device must include "AP" in
            list of "Supported interface modes" returned by "iw list".
        """
        ),
    ),
    testspec(
        device_nm_managed,
        "comitup-no-nm - Wifi device is not managed by NetworkManager",
        textwrap.dedent(
            """
            Comitup uses NetworkManager to manage the wifi devices, but the
            required devices are not listed. This usually means that the
            devices are listed in /etc/network/interfaces, and are therefore
            being managed elsewhere. Remove the references to wifi devices
            from that file.
        """
        ),
    ),
]


def run_checks(logit=True, printit=True, verbose=True, primary_dev="") -> bool:
    global dev_info

    dev_info = DevInfo(primary_dev)

    for testspec in testspecs:
        testresult = testspec.testfn()
        if testresult is not None:
            if logit:
                log.error(testspec.title)
                if testresult:
                    log.error("    " + testresult)

            if printit:
                print(testspec.title)
                if testresult:
                    print("    " + testresult)
                if verbose:
                    print(testspec.description)
            return True

    return False


if __name__ == "__main__":
    run_checks(logit=False)
