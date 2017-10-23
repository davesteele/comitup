#!/usr/bin/python3

import zipfile
import sys
import os
import hashlib
import gnupg
import json


img_path = sys.argv[1]
img_name = os.path.split(img_path)[-1]
img_dir = os.path.dirname(img_path)
zip_name = img_name + ".zip"
zip_path = img_path + ".zip"

trackers = [
    'udp://bt.xxx-tracker.com:2710/announce',
    'http://t.nyaatracker.com:80/announce',
    'https://open.kickasstracker.com:443/announce',
]

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

os.system("gpg -a --detach-sign {}".format(zip_path)
os.rename(zip_path + ".asc", "./torrent")

cmd = "transmission-create -o ./torrent/{0}.torrent".format(zip_name)
for tracker in trackers:
    cmd += " -t " + tracker
cmd += " " + zip_path
os.system(cmd)

os.system('transmission-show -m {0}.torrent >./torrent/{0}.magnet'.format(zip_name)

imginfo = {}
if 'lite' in img_name:
    imginfo['name'] = 'Lite'
    imgname = 'lite'
else:
    imginfo['name'] = ''
    imgname = 'full'

imginfo['filename'] = zip_name
imginfo['uncompressed'] = os.stat(img_path).st_size
imginfo['compressed'] = os.stat(zip_path).st_size
imginfo['uncompressedstr'] = numsum(imginfo['uncompressed'])
imginfo['compressedstr'] = numsum(imginfo['compressed'])
imginfo['magnet'] = open('./torrent/{}.magnet', 'r').read()

imgsinfo = json.load('imgs.json')

imgsinfo[imgname] = imginfo

with open('imgs.json', 'w') as fp:
	json.dump(fp, imgsinfo, indent=4, sort_keys=True)


