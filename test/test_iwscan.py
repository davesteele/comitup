import pytest
from typing import NamedTuple

from comitup.iwscan import decode_x


class Case(NamedTuple):
    instr: str
    outstr: str


@pytest.mark.parametrize(
    "case",
    [
        Case("but", "but"),
        Case("b\xc3\xbct", "büt"),
    ],
)
def test_decode_x(case):
    assert decode_x(case.instr) == case.outstr
