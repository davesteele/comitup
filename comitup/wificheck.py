#!/usr/bin/python3
# Copyright (c) 2017-2019 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE


from collections import namedtuple
import logging
import os
import re
import subprocess
import textwrap


log = logging.getLogger('comitup')


class DevInfo(object):
    def __init__(self):
        self.dev_list = []
        for dev in os.listdir("/sys/class/net"):
            try:
                path = "/sys/class/net/{}/phy80211/name".format(dev)
                with open(path, 'r') as fp:
                    phy = fp.read().strip()
                self.dev_list.append((dev, phy))
            except (NotADirectoryError, FileNotFoundError):
                pass

    def get_devs(self):
        return sorted([x[0] for x in self.dev_list])

    def get_phy(self, dev):
        return [x[1] for x in self.dev_list if x[0] == dev][0]


dev_info = DevInfo()


def device_present():
    if dev_info.get_devs():
        return None
    else:
        # Fail without comment
        return ""


def device_supports_ap():
    dev = dev_info.get_devs()[0]
    phy = dev_info.get_phy(dev)

    try:
        cmd = "iw phy {} info".format(phy)
        deviceinfo = subprocess.check_output(cmd.split()).decode()
    except subprocess.CalledProcessError:
        return ""

    if "* AP\n" not in deviceinfo:
        return phy

    return None


def device_nm_managed():
    try:
        cmd = "nmcli device show"
        devsinfo = subprocess.check_output(cmd.split(), re.MULTILINE).decode()

        for dev in dev_info.get_devs():
            if dev not in devsinfo:
                # Fail without comment
                return ""
    except subprocess.CalledProcessError:
        pass

    return None


testspec = namedtuple('testspec', ['testfn', 'title', 'description'])


testspecs = [
    testspec(
        device_present,
        "comitup-no-wifi - No wifi devices found",
        textwrap.dedent("""
            Comitup is a wifi device manager. 'sudo iw list' indicates that
            there are no devices to manage.
        """),
    ),
    testspec(
        device_supports_ap,
        "comitup-no-ap - The Main wifi device doesn't support AP mode",
        textwrap.dedent("""
            Comitup uses the first wifi device to implement the comitup-<nn>
            Access Point. For this to work, the device must include "AP" in
            list of "Supported interface modes" returned by "iw list".
        """),
    ),
    testspec(
        device_nm_managed,
        "comitup-no-nm - Wifi device is not managed by NetworkManager",
        textwrap.dedent("""
            Comitup uses NetworkManager to manage the wifi devices, but the
            required devices are not listed. This usually means that the
            devices are listed in /etc/network/interfaces, and are therefore
            being managed elsewhere. Remove the references to wifi devices
            from that file.
        """),
    ),
]


def run_checks(logit=True, printit=True, verbose=True):
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

    return None


if __name__ == '__main__':
    run_checks(logit=False)
