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

# Update tracker list from https://newtrackon.com
trackers = [
    'udp://tracker1.wasabii.com.tw:6969/announce',
    'udp://tracker.vanitycore.co:6969/announce',
    'http://tracker.sktorrent.net:6969/announce',
]


mag = [
    (1000000000.0, 'G'),
    (1000000.0, 'M'),
    (1000.0, 'K'),
]

fmt = [
    (1000, ".0f"),
    (9.9, ".1f"),
]


def numsum(num, base2=True):

    if base2:
        num = num / 1024. * 1000

    letter = ""
    for lim, sym in mag:
        if num >= lim:
            num /= lim
            letter = sym

    formatstr = ""
    for lim, fmtstr in fmt:
        if num < lim:
            formatstr = fmtstr

    derived_format = "{{0:{1}}} {2}".format(num, formatstr, letter)
    result = derived_format.format(num, formatstr, letter)

    return result

if os.path.exists(zip_path):
    os.unlink(zip_path)

zipf = zipfile.ZipFile(zip_path, compression=zipfile.ZIP_DEFLATED, mode='x')

curdir = os.getcwd()
os.chdir(img_dir)
zipf.write(img_name)
zipf.close()
os.chdir(curdir)

sha = hashlib.sha1()
with open(zip_path, 'rb') as fp:
    for chunk in iter(lambda: fp.read(1048576), b''):
        sha.update(chunk)

with open("./torrent/{}.sha1.txt".format(zip_name), 'w') as fp:
    fp.write("{0} {1}".format(sha.hexdigest(), zip_name))

os.system("gpg -a --detach-sign {}".format(zip_path))
os.rename(zip_path + ".asc", "./torrent/" + zip_name + ".asc.txt")

cmd = "transmission-create -o ./torrent/{0}.torrent".format(zip_name)
for tracker in trackers:
    cmd += " -t " + tracker
cmd += " " + zip_path
os.system(cmd)

os.system('transmission-show -m ./torrent/{0}.torrent >./torrent/{0}.magnet'.format(zip_name))

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
imginfo['magnet'] = open('./torrent/{}.magnet'.format(zip_name), 'r').read()

with open('imgs.json', 'r') as fp:
    imgsinfo = json.load(fp)

imgsinfo[imgname] = imginfo

with open('imgs.json', 'w') as fp:
	json.dump(imgsinfo, fp, indent=4, sort_keys=True)


