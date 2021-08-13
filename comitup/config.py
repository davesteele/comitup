# Copyright (c) 2017-2021 David Steele <dsteele@gmail.com>
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
from typing import Optional, Tuple

from comitup import persist

PERSIST_PATH: str = "/var/lib/comitup/comitup.json"
CONF_PATH: str = "/etc/comitup.conf"
BOOT_CONF_PATH: str = "/boot/comitup.conf"
SECTION: str = "DEFAULT"

data_cache: Optional[Tuple["Config", persist.persist]] = None


class MyConfigParser(configparser.ConfigParser):
    def getboolean(self, *args, **kwargs):
        mappings = {"y": True, "n": False}

        try:
            val = mappings[self.get(*args, **kwargs).lower()]
        except KeyError:
            val = super().getboolean(*args, **kwargs)

        return val


class Config(object):
    def __init__(self, filename: str, section: str = SECTION, defaults={}):
        self._section: str = section

        self._config = MyConfigParser(defaults=defaults)
        try:
            with open(filename, "r") as fp:
                conf_str = "[%s]\n" % self._section + fp.read()
            conf_fp = io.StringIO(conf_str)
            self._config.read_file(conf_fp)
        except FileNotFoundError:
            pass

    def getboolean(self, tag: str) -> bool:
        return self._config.getboolean(SECTION, tag)

    def __getattr__(self, tag):
        try:
            return self._config.get(self._section, tag)
        except configparser.NoOptionError:
            raise AttributeError


def load_data() -> Tuple[Config, persist.persist]:
    global data_cache

    if not data_cache:
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
                "ap_name": "comitup-<nnn>",
                "ap_password": "",
                "web_service": "",
                "service_name": "comitup",
                "external_callback": "/usr/local/bin/comitup-callback",
                "verbose": "0",
                "enable_appliance_mode": "1",
                "primary_wifi_device": "",
                "enable_nuke": "0",
                "ipv6_link_local": 1,
            },
        )

        data = persist.persist(
            PERSIST_PATH,
            {"id": str(random.randrange(1000, 9999))},
        )

        data_cache = (conf, data)

    return data_cache
