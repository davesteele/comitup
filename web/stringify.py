#!/usr/bin/python

from binascii import hexlify, unhexlify
from zlib import compress, decompress
from pickle import dumps, loads
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Hash import SHA256

crand = Random.new()
key = crand.read(AES.block_size)


class SfyException(Exception):
     def __init__(self, value):
         self.value = value
     def __str__(self):
         return repr(self.value)


def encrypt(str):
    iv = crand.read(16)
    crypt_alg = AES.new(key, AES.MODE_CFB, iv, segment_size=8)
    return iv + crypt_alg.encrypt(str)


def decrypt(ctext):
    crypt_alg = AES.new(key, AES.MODE_CFB, crand.read(16), segment_size=8)
    return crypt_alg.decrypt(ctext)[16:]


def calc_chk(text, key):
    h = SHA256.new()
    h.update(text)
    h.update(key)
    return h.hexdigest()


def add_chk(text):
    return text + calc_chk(text, key)


def chk_chk(text):
    (data, chk) = (text[:-64], text[-64:])

    if chk != calc_chk(data, key):
        raise SfyException("Checksum error")

    return data


def encode(obj):
    return add_chk(hexlify(encrypt(compress(dumps(obj)))))


def decode(hexstr):
    return loads(decompress(decrypt(unhexlify(chk_chk(hexstr)))))
