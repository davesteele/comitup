
import os
import json
from functools import wraps


class persist(dict):
    """A JSON-file backed persistent dictionary"""

    def __init__(self, path, *args, **kwargs):
        """Initialize with backing file path, and optional dict defaults"""

        super(persist, self).__init__(*args, **kwargs)

        self.path = path

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

    def justaddsave(fn):
        @wraps(fn)
        def wrapper(inst, *args, **kwargs):
            super_method = getattr(dict, fn.__name__)
            retval = super_method(inst, *args, **kwargs)
            fn(inst, *args, **kwargs)
            inst.save()
            return retval
        return wrapper

    @justaddsave
    def __setitem__(self, key, value):
        pass

    @justaddsave
    def update(self, *args, **kwargs):
        pass

    @justaddsave
    def setdefault(self, *args, **kwargs):
        pass
