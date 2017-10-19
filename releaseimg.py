#!/usr/bin/python3

import zipfile
import sys
import os
import hashlib
import gnupg


img_path = sys.argv[1]
img_name = os.path.split(img_path)[-1]
zip_name = img_name + ".zip"
zip_path = img_path + ".zip"

if os.path.exists(zip_path):
    os.unlink(zip_path)
zipf = zipfile.ZipFile(zip_path, mode='x')
zipf.write(img_path)
zipf.close()

sha = hashlib.sha1()
with open(zip_path, 'rb') as fp:
    for chunk in iter(lambda: fp.read(1048576), b''):
        sha.update(chunk)

with open("./torrent/{}.sha1".format(zip_name), 'w') as fp:
    fp.write("{0} {1}".format(sha.hexdigest(), zip_name))
