
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
from typing import Tuple

from comitup import persist

PERSIST_PATH = "/var/lib/comitup/comitup.json"
CONF_PATH = "/etc/comitup.conf"
BOOT_CONF_PATH = "/boot/comitup.conf"


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


def load_data() -> Tuple[Config, persist.persist]:
    if os.path.isfile(BOOT_CONF_PATH):
        try:
            dest = shutil.copyfile(BOOT_CONF_PATH, CONF_PATH)
            print("Boot config file copied:", dest)
            os.remove(BOOT_CONF_PATH)
        except Exception:
            print("Error occurred while copying file.")

    conf = Config(
                CONF_PATH,
                defaults={
                    'ap_name': 'comitup-<nnn>',
                    'ap_password': '',
                    'web_service': '',
                    'service_name': 'comitup',
                    'external_callback': '/usr/local/bin/comitup-callback',
                },
             )

    data = persist.persist(
                PERSIST_PATH,
                {'id': str(random.randrange(1000, 9999))},
           )

    return (conf, data)
