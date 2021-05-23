#!/usr/bin/python3

# Copyright (c) 2021 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE

import re
import subprocess
from typing import Optional


def defroute_dev() -> Optional[str]:
    """Return the name of the interface holding the default route."""

    cp = subprocess.run(
        "ip route".split(), stdout=subprocess.PIPE, encoding="utf-8"
    )
    fstline = cp.stdout.split("\n")[0]
    match = re.search("^default.+dev ([^ ]+)", fstline)

    if match:
        return match.group(1)

    return None


if __name__ == "__main__":
    print("Default route device is", defroute_dev())
