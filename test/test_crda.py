# Copyright (c) 2022 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE
#

from pathlib import Path
from typing import NamedTuple

import pytest

from comitup.crda import crda_get, crda_put


class TestCase(NamedTuple):
    teststr: str
    result: str


read_cases = [
    TestCase("", ""),
    TestCase("REGDOMAIN=", ""),
    TestCase("REGDOMAIN=US", "US"),
    TestCase("REGDOMAIN = US", "US"),
    TestCase("REGDOMAIN=US ", "US"),
    TestCase("foo\nREGDOMAIN=US\nfoo", "US"),
]


@pytest.fixture(params=read_cases)
def crda_env(request, tmp_path):
    case = request.param
    crda_path = tmp_path / "crda"
    crda_path.write_text(case.teststr)

    class CrdaFixtureCase(NamedTuple):
        path: Path
        result: str

    return CrdaFixtureCase(crda_path, case.result)


def test_crda_null():
    pass


def test_crda_get(crda_env):
    assert crda_get(str(crda_env.path)) == crda_env.result


def test_crda_put(crda_env):
    crda_put("CA", path=str(crda_env.path))

    assert crda_get(path=str(crda_env.path)) == "CA"


def test_crda_nofile_put(crda_env):
    crda_put("CA", path=str(crda_env.path.parent / "bogus"))


def test_crda_nofile_get(crda_env):
    crda_get(path=str(crda_env.path.parent / "bogus"))
