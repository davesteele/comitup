
#
# Copyright 2017 David Steele <steele@debian.org>
# This file is part of comitup
# Available under the terms of the GNU General Public License version 2
# or later
#

import logging
import subprocess
import modemgr


start_cmds = [
    # HOTSPOT rules
    "iptables -N COMITUP-OUT",
    "iptables -A COMITUP-OUT "
      "-p icmp --icmp-type destination-unreachable -j DROP", # noqa
    "iptables -A COMITUP-OUT -j RETURN",
    "iptables -I OUTPUT -j COMITUP-OUT",
]

end_cmds = [
    # Clear HOTSPOT rules
    "iptables -D OUTPUT -j COMITUP-OUT",
    "iptables -D COMITUP-OUT "
        "-p icmp --icmp-type destination-unreachable -j DROP", #noqa
    "iptables -D COMITUP-OUT -j RETURN",
    "iptables -X COMITUP-OUT",
]

appliance_cmds = [
    "iptables -t nat -N COMITUP-FWD",
    "iptables -t nat -A COMITUP-FWD -o wlan1 -j MASQUERADE",
    "iptables -t nat -A COMITUP-FWD -j RETURN",
    "iptables -t nat -A POSTROUTING -j COMITUP-FWD",
    "echo 1 > /proc/sys/net/ipv4/ip_forward",
]

appliance_clear = [
    "iptables -t nat -D POSTROUTING -j COMITUP-FWD",
    "iptables -t nat -D COMITUP-FWD -o wlan1 -j MASQUERADE",
    "iptables -t nat -D COMITUP-FWD -j RETURN",
    "iptables -t nat -X COMITUP-FWD",
]


log = logging.getLogger('comitup')


def run_cmds(cmds):
    [subprocess.call(cmd, shell=True) for cmd in cmds]


def state_callback(state, action):
    if (state, action) == ('HOTSPOT', 'start'):
        run_cmds(end_cmds)
        run_cmds(start_cmds)

        if modemgr.get_mode() == 'router':
            run_cmds(appliance_clear)

    elif (state, action) == ('CONNECTING', 'start'):
        run_cmds(end_cmds)

        if modemgr.get_mode() == 'router':
            run_cmds(appliance_clear)
            run_cmds(appliance_cmds)


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
