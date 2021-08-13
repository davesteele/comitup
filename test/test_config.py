# Copyright (c) 2017-2019 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE
import os
import textwrap
from collections import namedtuple

import pytest

from comitup import config


@pytest.fixture()
def conf_fxt(tmpdir):
    path = os.path.join(tmpdir.__str__(), "conf.conf")

    with open(path, "w") as fp:
        fp.write(
            textwrap.dedent(
                """
                #
                # comment
                #
                tag1=val1
                tag2: val2
                tag3 = val3
                # tag4 = val4
                """
            )
        )

    return config.Config(path)


@pytest.mark.parametrize("idx", ("1", "2", "3"))
def test_conf_vals(idx, conf_fxt):
    assert eval('conf_fxt.tag{0} == "val{0}"'.format(idx))


def test_conf_miss(conf_fxt):
    with pytest.raises(AttributeError):
        conf_fxt.tag4


Case = namedtuple("Case", ["data", "result"])
BoolFixt = namedtuple("BoolFixt", ["config", "result"])


@pytest.fixture(
    params=[
        Case("0", False),
        Case("1", True),
        Case("yes", True),
        Case("Yes", True),
        Case("no", False),
        Case("y", True),
        Case("n", False),
        Case("true", True),
        Case("True", True),
        Case("TRUE", True),
        Case("false", False),
        Case("on", True),
        Case("off", False),
    ]
)
def bool_fixt(tmpdir, request):
    path = os.path.join(tmpdir.__str__(), "conf.conf")

    with open(path, "w") as fp:
        fp.write("tag = {}".format(request.param.data))

    return BoolFixt(config.Config(path), request.param.result)


def test_conf_bool(bool_fixt):
    assert bool_fixt.config.getboolean("tag") == bool_fixt.result
