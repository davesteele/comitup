import pytest

from comitup import mdns
import textwrap

from xml.etree import ElementTree as ET

import os


@pytest.fixture()
def avahi_conf(tmpdir):
    path = tmpdir.join(u'hosts')

    with open(path.strpath, 'w') as fp:
        fp.write(textwrap.dedent(
                """
                # header
                1.2.3.4 host1.local
                9.8.7.6 comitup.local
                5.6.7.8 host2.local
                """
            )
        )

    return path


@pytest.fixture()
def service_path(tmpdir):
    return tmpdir.join(u'comitup.service')


@pytest.fixture()
def service_data(service_path):
    data = {
        'service_name': "comitup on %h",
        'hosts': ['host1', 'host2'],
        'services': [
            {
                'type': '_http._tcp',
                'port': 80,
            },
        ],
    }

    return data


def test_avahi_fxt(avahi_conf):
    with open(avahi_conf.strpath, 'r') as fp:
        old = fp.read()

    assert "9.8.7.6 comitup.local\n" in old
    assert "header" in old


def test_update_entry(avahi_conf):
    mdns.update_entry('comitup.local', '10.11.12.13', avahi_conf.strpath)

    with open(avahi_conf.strpath, 'r') as fp:
        new = fp.read()

    assert "10.11.12.13 comitup.local\n" in new

    assert "header" in new
    assert "1.2.3.4" in new
    assert "5.6.7.8" in new
    assert "9.8.7.6 comitup.local\n" not in new


@pytest.mark.parametrize("hosts", (
        ('comitup.local', 'comitup-8675.local'),
        ('comitup-8675.local', 'comitup.local'),
    )
)
def test_update_entries(avahi_conf, hosts):
    mdns.update_entry(
        hosts,
        '10.11.12.13',
        avahi_conf.strpath
    )

    with open(avahi_conf.strpath, 'r') as fp:
        new = fp.read()

    assert "10.11.12.13 comitup.local\n" in new
    assert "10.11.12.13 comitup-8675.local\n" in new

    assert "header" in new
    assert "1.2.3.4" in new
    assert "5.6.7.8" in new
    assert "9.8.7.6 comitup.local\n" not in new


def test_rm_entry(avahi_conf):
    mdns.rm_entry('comitup.local', avahi_conf.strpath)

    with open(avahi_conf.strpath, 'r') as fp:
        new = fp.read()

    assert "header" in new
    assert "1.2.3.4" in new
    assert "5.6.7.8" in new
    assert "comitup.local" not in new


def test_avahi_service_exist(service_path, service_data):
    mdns.mk_service_file(service_data, service_path.strpath)
    assert os.path.exists(service_path.strpath)


def test_avahi_service_parses(service_path, service_data):
    mdns.mk_service_file(service_data, service_path.strpath)
    ET.parse(service_path.strpath)


def test_avahi_service_content(service_path, service_data):
    mdns.mk_service_file(service_data, service_path.strpath)
    tree = ET.parse(service_path.strpath)
    root = tree.getroot()

    assert(root.tag == 'service-group')
    assert(root[0].tag == 'name')
    assert('comitup' in root[0].text)
    assert(root[1].tag == 'service')
    assert(root[1][0].text == 'host1')
    assert(root[2][0].text == 'host2')
