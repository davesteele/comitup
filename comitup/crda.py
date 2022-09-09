# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE
#
# Copyright 2022 David Steele <steele@debian.org>
# This file is part of comitup
# Available under the terms of the GNU General Public License version 2
# or later

import re
from pathlib import Path

CRDA_FILE_PATH = "/etc/default/crda"


def crda_get(path=CRDA_FILE_PATH) -> str:
    try:
        crda_text = Path(path).read_text()
    except FileNotFoundError:
        return ""

    m = re.search(r"^REGDOMAIN\s*=\s*(.+?)\s*$", crda_text, flags=re.MULTILINE)

    if m:
        return m.group(1)
    else:
        return ""


def crda_put(val: str, path=CRDA_FILE_PATH) -> None:
    crda_path = Path(path)

    try:
        crda_text = crda_path.read_text()
    except FileNotFoundError:
        return None

    if re.search(r"^REGDOMAIN\s*=.*", crda_text, flags=re.MULTILINE):
        new_text = re.sub(
            r"^REGDOMAIN\s*=.*$",
            f"REGDOMAIN={val}",
            crda_text,
            flags=re.MULTILINE,
        )
        crda_path.write_text(new_text)
    else:
        crda_text += f"\nREGDOMAIN={val}\n"
        crda_path.write_text(crda_text)
