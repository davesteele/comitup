
#
# Copyright 2017 David Steele <steele@debian.org>
# This file is part of comitup
# Available under the terms of the GNU General Public License version 2
# or later
#

import logging
import subprocess


start_cmds = [
    "iptables -N COMITUP-OUT",
    "iptables -A COMITUP-OUT "
      "-p icmp --icmp-type destination-unreachable -j DROP", # noqa
    "iptables -A COMITUP-OUT -j RETURN",
    "iptables -I OUTPUT -j COMITUP-OUT",
]

end_cmds = [
    "iptables -D OUTPUT -j COMITUP-OUT",
    "iptables -D COMITUP-OUT "
        "-p icmp --icmp-type destination-unreachable -j DROP", #noqa
    "iptables -D COMITUP-OUT -j RETURN",
    "iptables -X COMITUP-OUT",
]

log = logging.getLogger('comitup')


def run_cmds(cmds):
    [subprocess.call(cmd.split()) for cmd in cmds]


def state_callback(state, action):
    if (state, action) == ('HOTSPOT', 'start'):
        run_cmds(start_cmds)
    elif (state, action) == ('CONNECTING', 'start'):
        run_cmds(end_cmds)


def init_iptmgr():
    pass


def main():
    import six

    print("applying rules")
    run_cmds(start_cmds)

    six.input("Press Enter to continue...")

    run_cmds(end_cmds)


if __name__ == '__main__':
    main()
