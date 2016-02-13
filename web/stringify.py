#!/usr/bin/python

import binascii
import zlib
import pickle
from Crypto.Cipher import AES
from Crypto import Random


crand = Random.new()
key = crand.read(AES.block_size)


def encrypt(str):
    iv = crand.read(16)
    crypt_alg = AES.new(key, AES.MODE_CFB, iv, segment_size=8)
    return iv + crypt_alg.encrypt(str)


def decrypt(ctext):
    crypt_alg = AES.new(key, AES.MODE_CFB, crand.read(16), segment_size=8)

    return crypt_alg.decrypt(ctext)[16:]


def encode(obj):
    jobj = pickle.dumps(obj)
    cobj = zlib.compress(jobj)
    xobj = encrypt(cobj)
    hobj = binascii.hexlify(xobj)

    return hobj


def decode(hexstr):
    cobj = binascii.unhexlify(hexstr)
    xobj = decrypt(cobj)
    jobj = zlib.decompress(xobj)
    obj = pickle.loads(jobj)

    return obj

