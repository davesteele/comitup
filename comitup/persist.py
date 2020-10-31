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

import json
import os
from functools import wraps


def persist_decorator(klass):
    """Add a save behavior to methods that update dict data"""
    for method in ["__setitem__", "__delitem__", "update", "setdefault"]:
        setattr(klass, method, klass.addsave(getattr(klass, method)))

    return klass


@persist_decorator
class persist(dict):
    """A JSON-file backed persistent dictionary"""

    def __init__(self, path, *args, **kwargs):
        """Initialize with backing file path, and optional dict defaults"""

        super(persist, self).__init__(*args, **kwargs)

        self._path = path

        if os.path.exists(self._path):
            self.load()

        self.save()

    def save(self):
        with open(self._path, "w") as fp:
            json.dump(self, fp, indent=2)

    def load(self):
        with open(self._path, "r") as fp:
            dct = json.load(fp)

        super().update(dct)

    def addsave(fn):
        """Decorator to add save behavior to methods"""

        @wraps(fn)
        def wrapper(self, *args, **kwargs):
            retval = fn(self, *args, **kwargs)
            self.save()
            return retval

        return wrapper

    def __setattr__(self, name, value):
        if name in self.__dict__ or name.startswith("_"):
            self.__dict__[name] = value
        else:
            self.__setitem__(name, value)

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            return self.__getitem__(name)
