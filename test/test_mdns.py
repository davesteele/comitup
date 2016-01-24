import pytest

import mdns
import textwrap


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


def test_rm_entry(avahi_conf):
    mdns.rm_entry('comitup.local', avahi_conf.strpath)

    with open(avahi_conf.strpath, 'r') as fp:
        new = fp.read()

    assert "header" in new
    assert "1.2.3.4" in new
    assert "5.6.7.8" in new
    assert "comitup.local" not in new
