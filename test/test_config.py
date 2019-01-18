
# Copyright (c) 2017-2019 David Steele <dsteele@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later
# License-Filename: LICENSE
import pytest
import textwrap
import os

from comitup import config


@pytest.fixture()
def conf_fxt(tmpdir):
    path = os.path.join(tmpdir.__str__(), "conf.conf")

    with open(path, 'w') as fp:
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


@pytest.mark.parametrize("idx", ('1', '2', '3'))
def test_conf_vals(idx, conf_fxt):
    assert eval('conf_fxt.tag{0} == "val{0}"'.format(idx))


def test_conf_miss(conf_fxt):
    with pytest.raises(AttributeError):
        conf_fxt.tag4
