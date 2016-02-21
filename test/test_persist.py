

from comitup.persist import persist

import pytest
import os


@pytest.fixture()
def jsonpath(tmpdir):
    return os.path.join(tmpdir.__str__(), "persist.json")


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
