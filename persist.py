
import os
import json


class persist(dict):
    """A JSON-file backed persistent dictionary"""

    def __init__(self, path, *args, **kwargs):
        """Initialize with backing file path, and optional dict defaults"""

        super(persist, self).__init__(*args, **kwargs)

        self.path = path

        if os.path.exists(self.path):
            self.load()

        self.save()

    def __setitem__(self, key, value):
        super(persist, self).__setitem__(key, value)
        self.save()

    def save(self):
        with open(self.path, 'w') as fp:
            json.dump(self, fp, indent=2)

    def load(self):
        with open(self.path, 'r') as fp:
            dict = json.load(fp)

        self.update(dict)

    def update(self, *args, **kwargs):
        super(persist, self).update(*args, **kwargs)
        self.save()

    def setdefault(self, *args, **kwargs):
        retvalue = super(persist, self).setdefault(*args, **kwargs)
        self.save()
        return retvalue
