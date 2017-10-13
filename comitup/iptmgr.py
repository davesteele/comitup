
#
# Copyright 2017 David Steele <steele@debian.org>
# This file is part of comitup
# Available under the terms of the GNU General Public License version 2
# or later
#

import logging
import subprocess
import modemgr
import nm


start_cmds = [
    # HOTSPOT rules
    "iptables -w -N COMITUP-OUT",
    "iptables -w -A COMITUP-OUT "
      "-p icmp --icmp-type destination-unreachable -j DROP",  # noqa
    "iptables -w -A COMITUP-OUT "
      "-p icmp --icmp-type port-unreachable -j DROP",  # noqa
    "iptables -w -A COMITUP-OUT -j RETURN",
    "iptables -w -I OUTPUT -j COMITUP-OUT",
]

end_cmds = [
    # Clear HOTSPOT rules
    "iptables -w -D OUTPUT -j COMITUP-OUT >/dev/null 2>&1",
    "iptables -w -D COMITUP-OUT "
        "-p icmp --icmp-type destination-unreachable "        # noqa
        "-j DROP >/dev/null 2>&1",                            # noqa
    "iptables -w -D COMITUP-OUT "
        "-p icmp --icmp-type port-unreachable "        # noqa
        "-j DROP >/dev/null 2>&1",                            # noqa
    "iptables -w -D COMITUP-OUT -j RETURN >/dev/null 2>&1",
    "iptables -w -X COMITUP-OUT >/dev/null 2>&1",
]

appliance_cmds = [
    "iptables -w -t nat -N COMITUP-FWD",
    "iptables -w -t nat -A COMITUP-FWD -o {} -j MASQUERADE",
    "iptables -w -t nat -A COMITUP-FWD -j RETURN",
    "iptables -w -t nat -A POSTROUTING -j COMITUP-FWD",
    "echo 1 > /proc/sys/net/ipv4/ip_forward",
]

appliance_clear = [
    "iptables -w -t nat -D POSTROUTING -j COMITUP-FWD >/dev/null 2>&1",
    "iptables -w -t nat -D COMITUP-FWD -o {} -j MASQUERADE >/dev/null 2>&1",
    "iptables -w -t nat -D COMITUP-FWD -j RETURN >/dev/null 2>&1",
    "iptables -w -t nat -X COMITUP-FWD >/dev/null 2>&1",
]


log = logging.getLogger('comitup')


def run_cmds(cmds):
    outdev = nm.device_name(modemgr.get_link_device())
    for cmd in cmds:
        subprocess.call(cmd.format(outdev), shell=True)


def state_callback(state, action):
    if (state, action) == ('HOTSPOT', 'start'):
        log.debug("Running iptables commands for HOTSPOT")

        run_cmds(end_cmds)
        run_cmds(start_cmds)

        if modemgr.get_mode() == 'router':
            run_cmds(appliance_clear)

        log.debug("Done with iptables commands for HOTSPOT")

    elif (state, action) == ('CONNECTED', 'start'):
        log.debug("Running iptables commands for CONNECTING")
        run_cmds(end_cmds)

        if modemgr.get_mode() == 'router':
            run_cmds(appliance_clear)
            run_cmds(appliance_cmds)

        log.debug("Done with iptables commands for CONNECTING")


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
