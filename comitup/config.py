
#
# Copyright 2016-2017 David Steele <steele@debian.org>
# This file is part of comitup
# Available under the terms of the GNU General Public License version 2
# or later
#

import ConfigParser
import StringIO


class Config(object):
    def __init__(self, filename, section='DEFAULT', defaults={}):
        self._section = section

        self._config = ConfigParser.SafeConfigParser(defaults=defaults)
        conf_str = '[%s]\n' % self._section + open(filename, 'r').read()
        conf_fp = StringIO.StringIO(conf_str)
        self._config.readfp(conf_fp)

    def __getattr__(self, tag):
        try:
            return self._config.get(self._section, tag)
        except ConfigParser.NoOptionError:
            raise AttributeError
