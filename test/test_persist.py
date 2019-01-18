
# Copyright (c) 2017-2019 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE

from comitup.persist import persist

import pytest
import os
import tempfile
import shutil


@pytest.fixture(scope='module')
def dir_fxt(request):
    dir = tempfile.mkdtemp()

    def fin():
        shutil.rmtree(dir)

    request.addfinalizer(fin)

    return dir


count = 0


@pytest.fixture()
def jsonpath(request, dir_fxt):
    global count

    path = os.path.join(dir_fxt, 'persist%d.json' % count)
    count += 1

    return path


def test_persist_is_dict(jsonpath):
    mydict = persist(jsonpath)
    mydict['a'] = 'b'
    assert mydict['a'] == 'b'


def test_persist_default(jsonpath):
    mydict = persist(jsonpath, {'a': 'b'})
    assert mydict['a'] == 'b'


def test_persist_default_persists(jsonpath):
    persist(jsonpath, {'a': 'b'})
    new = persist(jsonpath)
    assert new['a'] == 'b'


def test_persist_override_default(jsonpath):
    persist(jsonpath, {'a': 'b'})
    new = persist(jsonpath, {'a': 'c'})
    assert new['a'] == 'b'


def test_persist_override_default2(jsonpath):
    mydict = persist(jsonpath, {'a': 'a'})
    mydict['a'] = 'b'
    new = persist(jsonpath, {'a': 'c'})
    assert new['a'] == 'b'


def test_persist_update(jsonpath):
    mydict = persist(jsonpath, {'a': 'a'})
    mydict.update({'a': 'b'})
    new = persist(jsonpath, {'a': 'c'})
    assert new['a'] == 'b'


def test_persist_setdefault(jsonpath):
    mydict = persist(jsonpath)
    mydict.setdefault('a', 'b')
    new = persist(jsonpath, {'a': 'c'})
    assert new['a'] == 'b'


def test_persist_setattr(jsonpath):
    mydict = persist(jsonpath)
    mydict.a = 'b'
    assert mydict['a'] == 'b'


def test_persist_getattr(jsonpath):
    mydict = persist(jsonpath)
    mydict['a'] = 'b'
    assert mydict.a == 'b'


def test_persist_persist_setattr(jsonpath):
    mydict = persist(jsonpath)
    mydict.a = 'b'
    new = persist(jsonpath)
    assert new['a'] == 'b'


def test_persist_persist_getattr(jsonpath):
    mydict = persist(jsonpath)
    mydict['a'] = 'b'
    new = persist(jsonpath)
    assert new.a == 'b'


def test_persist_file_format(jsonpath):
    mydict = persist(jsonpath)
    mydict['a'] = 'b'

    expected = '{\n  "a": "b"\n}'
    assert open(jsonpath, 'r').read() == expected


def test_persist_get_attr_dict(jsonpath):
    mydict = persist(jsonpath)

    assert mydict.path == jsonpath
    assert mydict.__getattr__('path') == jsonpath


def test_persist_set_attr_dict(jsonpath):
    mydict = persist(jsonpath)

    mydict.path = jsonpath
