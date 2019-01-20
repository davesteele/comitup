
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
