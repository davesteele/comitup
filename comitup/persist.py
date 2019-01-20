
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

import os
import json
from functools import wraps


class persist(dict):
    """A JSON-file backed persistent dictionary"""

    def __init__(self, path, *args, **kwargs):
        """Initialize with backing file path, and optional dict defaults"""

        super(persist, self).__init__(*args, **kwargs)

        self.__dict__['path'] = path

        if os.path.exists(self.path):
            self.load()

        self.save()

    def save(self):
        with open(self.path, 'w') as fp:
            json.dump(self, fp, indent=2)

    def load(self):
        with open(self.path, 'r') as fp:
            dict = json.load(fp)

        self.update(dict)

    def addsave(fn):
        @wraps(fn)
        def wrapper(inst, *args, **kwargs):
            # give wrapped function a chance to validate arguments
            fn(inst, *args, **kwargs)

            super_method = getattr(inst.__class__.__bases__[0], fn.__name__)
            retval = super_method(inst, *args, **kwargs)
            inst.save()
            return retval
        return wrapper

    @addsave
    def __setitem__(self, key, value, super_ret=None):
        pass

    @addsave
    def update(self, *args, **kwargs):
        pass

    @addsave
    def setdefault(self, *args, **kwargs):
        pass

    def __setattr__(self, name, value):
        if name in self.__dict__:
            self.__dict__[name] = value
        else:
            self.__setitem__(name, value)

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            return self.__getitem__(name)
