#!/usr/bin/python
# Copyright (c) 2017 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2+
# License-Filename: LICENSE


from collections import namedtuple
import textwrap
import logging
import subprocess
import re


log = logging.getLogger('comitup')


def device_present():
    if subprocess.check_output("iw list".split()) == "":
        # Fail without comment
        return ""
    return None


def device_supports_ap():
    devicesinfo = subprocess.check_output("iw list".split())

    phy = devicesinfo.split()[1]

    cmd = "iw phy {} info".format(phy.decode())
    deviceinfo = subprocess.check_output(cmd.split()).decode()

    if "* AP\n" not in deviceinfo:
        return phy

    return None


def device_nm_managed():
    devicesinfo = subprocess.check_output("nmcli device show".split(), re.MULTILINE).decode()

    if not re.search("GENERAL.TYPE\W+wifi", devicesinfo):
        # Fail without comment
        return ""

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
            Comitup uses the first wifi device to implement the comitup-<nnnn>
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
