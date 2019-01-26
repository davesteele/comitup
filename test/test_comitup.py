
# Copyright (c) 2017-2019 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE

import pytest
from mock import Mock
import textwrap
import os

from comitup import comitup as ciu


@pytest.fixture()
def conf_fxt(tmpdir, monkeypatch):
    path = os.path.join(tmpdir.__str__(), 'conffile')

    open(path, 'w').write(textwrap.dedent(
        """
        ap_name: test
        """
    ))

    monkeypatch.setattr('comitup.comitup.CONF_PATH', path)

    return path


@pytest.fixture()
def persist_fxt(tmpdir, monkeypatch):
    path = os.path.join(tmpdir.__str__(), 'persistfile')

    monkeypatch.setattr('comitup.comitup.PERSIST_PATH', path)
    monkeypatch.setattr(
                    'comitup.comitup.random.randrange',
                    Mock(return_value=1234)
                )

    return path


@pytest.fixture()
def log_fxt(tmpdir, monkeypatch):
    path = os.path.join(tmpdir.__str__(), 'logfile')

    monkeypatch.setattr('comitup.comitup.LOG_PATH', path)

    return path


def test_ciu_deflog(log_fxt):
    log = ciu.deflog()

    log.info('foo')

    txt = open(log_fxt, 'r').read()

    assert 'INFO' in txt
    assert 'foo' in txt
    assert int(txt[:4])


def test_ciu_loadconf(conf_fxt, persist_fxt):
    (conf, data) = ciu.load_data()
    assert conf.ap_name == 'test'
    assert os.path.isfile(persist_fxt)


@pytest.fixture()
def loop_fxt(monkeypatch):
    loop = Mock()

    monkeypatch.setattr(
                    'comitup.comitup.MainLoop',
                    Mock(return_value=loop)
                )

    return loop
