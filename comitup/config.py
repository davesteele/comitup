
# Copyright (c) 2017-2019 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE
#
# Copyright 2016-2017 David Steele <steele@debian.org>
# This file is part of comitup
# Available under the terms of the GNU General Public License version 2
# or later
#

import configparser
import io
import os
import random
import shutil
import re
import logging
import subprocess

from comitup import persist

log = logging.getLogger('comitup')

PERSIST_PATH = "/var/lib/comitup/comitup.json"
CONF_PATH = "/etc/comitup.conf"
BOOT_CONF_PATH = "/boot/comitup.conf"
DEFAULT_AP = "comitup-<nnn>"

# ap_name regex patterns
REGEX_APNAME_ID = r'<(?<=\<)([n]{1,4}|[M]{1,12}|[s]{1,16})(?=\>)>'
# matches '<#...>' where # is M... MAC address, 1-12 characters
#                             s... RPi serial number, 1-16 characters
#                             n... randomly generated number
# ID spec may appear anywhere in the apname, with/without a '-' separator
# Valid match examples: <nn>-myname, p1125-<nnn>, <ss>-<hostname>,
#                       <hostname>-<MMMM>, first<MMM>second


class Config(object):
    def __init__(self, filename, section='DEFAULT', defaults={}):
        self._section = section

        self._config = configparser.ConfigParser(defaults=defaults)
        try:
            with open(filename, 'r') as fp:
                conf_str = '[%s]\n' % self._section + fp.read()
            conf_fp = io.StringIO(conf_str)
            self._config.read_file(conf_fp)
        except FileNotFoundError:
            pass

    def __getattr__(self, tag):
        try:
            return self._config.get(self._section, tag)
        except configparser.NoOptionError:
            raise AttributeError


def _getserial():
    # Extract serial from cpuinfo file
    cpuserial = "0000000000000000"
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line.startswith('Serial'):  # Serial		: 10000000082acda8
                    cpuserial = line.split(':')[-1].strip()
                    break

    except Exception as e:
        log.error("Failed to parse /proc/cpuinfo for serial number")
        log.error(e)
        cpuserial = "ERROR000000000"

    return cpuserial


def _get_mac():
    mac = "000000000000"
    cmd = "nmcli -f GENERAL.HWADDR device show wlan0".split(' ')
    try:
        mac_info = subprocess.check_output(cmd).decode("utf-8")
        # from: GENERAL.HWADDR:                         DC:A6:32:2B:6D:37
        # to  : DCA6322B6D37
        mac = mac_info.replace('GENERAL.HWADDR:', '').replace(':', '').strip()

    except Exception as e:
        log.error(e)

    return mac


def load_data():
    if os.path.isfile(BOOT_CONF_PATH):
        try:
            dest = shutil.copyfile(BOOT_CONF_PATH, CONF_PATH)
            print("Boot config file copied:", dest)
            log.info("Boot config file copied: {}".format(dest))
            os.remove(BOOT_CONF_PATH)
        except Exception:
            print("Error occurred while copying file.")
            log.error("Error occurred while copying file.")

    conf = Config(
                CONF_PATH,
                defaults={
                    'ap_name': DEFAULT_AP,
                    'ap_password': '',
                    'web_service': '',
                    'service_name': 'comitup',
                    'external_callback': '/usr/local/bin/comitup-callback',
                    'manage_wired_device': False,
                },
             )

    data = persist.persist(
                PERSIST_PATH,
                {'id': str(random.randrange(1000, 9999))},
           )

    spec = re.search(REGEX_APNAME_ID, conf.ap_name)
    if spec is not None:
        # if spec is '<nnn...' data already includes 'id' random number
        # get MAC or SerialNumber if required
        if spec.group().startswith('<M'):
            data['mac'] = _get_mac()

        if spec.group().startswith('<s'):
            data['sn']: _getserial()

    log.info("MGAG load_data manage_wired_device {}".format(conf.manage_wired_device))
    return (conf, data)
