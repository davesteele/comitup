

import pytest
import string

from web import stringify as sfy


@pytest.mark.parametrize(
                "test_str",
                ("", "hello", ''.join('a' for i in range(999)))
             )
def test_web_stringify_encrypt(test_str):
    assert test_str == sfy.decrypt(sfy.encrypt(test_str))


@pytest.mark.parametrize('tst', ('len', 'pass', 'fail'))
def test_web_stringify_chk(tst):
    orig = 'a'
    chked = sfy.add_chk(orig)

    if tst == 'len':
        assert len(chked) > len(orig)
    elif tst == 'pass':
        assert sfy.chk_chk(chked) == orig
    elif tst == 'fail':
        with pytest.raises(sfy.SfyException):
            sfy.chk_chk(chked + 'a')
    else:
        assert False


@pytest.mark.parametrize("var", (1, "string", {'a': 1, 'b': 2}))
@pytest.mark.parametrize("tst", ("encode", "decode", "iv"))
def test_web_stringify(tst, var):
    encoded = sfy.encode(var)

    if tst == "encode":
        assert all(x in string.hexdigits for x in encoded)
    elif tst == "decode":
        assert sfy.decode(encoded) == var
    elif tst == "iv":
        assert encoded != sfy.encode(var)
    else:
        assert False
