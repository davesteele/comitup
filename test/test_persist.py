

from comitup.persist import persist

import pytest
import os


@pytest.fixture()
def jsonpath(tmpdir):
    return os.path.join(tmpdir.__str__(), "persist.json")


def test_persist_is_dict(jsonpath):
    dict = persist(jsonpath)
    dict['a'] = 'b'
    assert dict['a'] == 'b'


def test_persist_default(jsonpath):
    dict = persist(jsonpath, {'a': 'b'})
    assert dict['a'] == 'b'


def test_persist_default_persists(jsonpath):
    persist(jsonpath, {'a': 'b'})
    new = persist(jsonpath)
    assert new['a'] == 'b'


def test_persist_override_default(jsonpath):
    persist(jsonpath, {'a': 'b'})
    new = persist(jsonpath, {'a': 'c'})
    assert new['a'] == 'b'


def test_persist_override_default2(jsonpath):
    dict = persist(jsonpath, {'a': 'a'})
    dict['a'] = 'b'
    new = persist(jsonpath, {'a': 'c'})
    assert new['a'] == 'b'


def test_persist_update(jsonpath):
    dict = persist(jsonpath, {'a': 'a'})
    dict.update({'a': 'b'})
    new = persist(jsonpath, {'a': 'c'})
    assert new['a'] == 'b'


def test_persist_setdefault(jsonpath):
    dict = persist(jsonpath)
    dict.setdefault('a', 'b')
    new = persist(jsonpath, {'a': 'c'})
    assert new['a'] == 'b'
