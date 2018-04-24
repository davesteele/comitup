#!/usr/bin/python3

import subprocess
import re


def get_country_code():
    out = subprocess.check_output("iw reg get".split()).decode()

    match = re.search("country (..):", out, re.MULTILINE)

    if match:
        return match.group(1)

    return None


def set_country_code(code):
    cmd = "iw reg set " + code
    out = subprocess.check_output(cmd.split())

    crda = "/etc/default/crda"

    with open(crda, 'r') as fp:
        crdatext = fp.read()

    crdatext = re.sub("REGDOMAIN=.*", "REGDOMAIN=%s" % code,
                      crdatext, re.MULTILINE)

    with open(crda, 'w') as fp:
        fp.write(crdatext)


if __name__ == '__main__':
    country = get_country_code()

    print(country)

    set_country_code("US")
