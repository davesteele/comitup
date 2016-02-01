#!/usr/bin/python

import argparse
import textwrap
import jinja2
import ConfigParser


def set_avahi_param(section, parameter, value, conf='/etc/avahi/avahi-daemon.conf'):

    out = []
    with open(conf, 'r') as fp:
        for line in fp.readlines():
            if parameter not in line:
                out.append(line)

            if '[' + section + ']' in line:
                out.append(parameter + "=" + value + "\n")

    with open(conf, 'w') as fp:
        for line in out:
            fp.write(line)


def init_mdns(conf='/etc/avahi/avahi-daemon.conf'):
    set_avahi_param('publish', 'publish-addresses', 'no')


def update_entry(name, addr=None, file='/etc/avahi/hosts'):

    with open(file, 'r+') as fp:

        if isinstance(name, basestring):
            name = [name]

        lines = [x for x in fp.readlines()]
        for host in name:
            lines = [x for x in lines if not host in x]
            if addr:
                lines.append("{0} {1}\n".format(addr, host))

        fp.seek(0)
        for line in lines:
            fp.write(line)
        fp.truncate()


def rm_entry(name, file='/etc/avahi/hosts'):
    update_entry(name, None, file)


xml_template = textwrap.dedent(
"""    <?xml version="1.0" standalone='no'?>
    <!DOCTYPE service-group SYSTEM "avahi-service.dtd">
    <service-group>
        <name replace-wildcards="yes">{{ service_name }}</name>
    {%- for service in services -%}
    {% for host in hosts %}
        <service>
            <host-name>{{ host }}</host-name>
            <type>{{ service.type }}</type>
            <port>{{ service.port }}</port>
        </service>
    {%- endfor -%}
    {% endfor %}
    </service-group>
    """
)

def mk_service_file(data, path="/etc/avahi/services/comitup.service"):
    template = jinja2.Template(xml_template)

    with open(path, 'w') as fp:
        fp.write(template.render(data))


def publish_comitup_hosts(hosts, addr):
    data = {
        'service_name': "comitup on %h",
        'hosts': hosts,
        'services': [
            {
                'type': '_workstation._tcp',
                'port': 9,
            },
        ],
    }

    update_entry(hosts, addr)

    mk_service_file(data)


def parse_args():
    prog = 'mdns'
    parser = argparse.ArgumentParser(
        prog=prog,
        description="Add an mdns (Zeroconf) entry for a .local address",
        epilog="After entry, the host can be accessed by e.g. "
               "'ping <host>.local'",
    )

    parser.add_argument(
        'host',
        help="host name (e.g. \"comitup.local\")",
    )

    parser.add_argument(
        'address',
        help="IP address",
    )

    args = parser.parse_args()

    return args


def main():
    args = parse_args()

    host = args.host
    if '.local' not in host:
        host += ".local"

    init_mdns()

    publish_comitup_hosts([host], args.address)


if __name__ == '__main__':
    main()
