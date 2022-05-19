#!/usr/bin/python3

import zipfile
import sys
import os
import hashlib
import json
from pathlib import Path

from jinja2 import Template


zip_path = sys.argv[1]
zip_name = os.path.split(zip_path)[-1]
zip_dir = os.path.dirname(zip_path)

info_name = zip_name[6:-4] + ".info"
info_path = os.path.join(zip_dir, info_name)

if ".zip" not in zip_name:
    print("argument must be the zipped image")
    sys.exit(1)

mag = [
    (1000000000.0, "G"),
    (1000000.0, "M"),
    (1000.0, "K"),
]

fmt = [
    (1000, ".0f"),
    (9.9, ".1f"),
]


def numsum(num, base2=True):

    if base2:
        num = num / 1024.0 * 1000

    letter = ""
    for lim, sym in mag:
        if num >= lim:
            num /= lim
            letter = sym

    formatstr = ""
    for lim, fmtstr in fmt:
        if num < lim:
            formatstr = fmtstr

    derived_format = "{{0:{1}}} {2}".format(num, formatstr, letter)  # noqa
    result = derived_format.format(num, formatstr, letter)

    return result


sha = hashlib.sha1()
with open(zip_path, "rb") as fp:
    for chunk in iter(lambda: fp.read(1048576), b""):
        sha.update(chunk)

torrent_path = Path("./torrent")
if not torrent_path.exists():
    torrent_path.mkdir()

with open("./torrent/{}.sha1.txt".format(zip_name), "w") as fp:
    fp.write("{0} {1}".format(sha.hexdigest(), zip_name))

os.system("gpg -a --detach-sign {}".format(zip_path))
os.rename(zip_path + ".asc", "./torrent/" + zip_name + ".asc.txt")

imginfo = {}
if "lite" in zip_name:
    imginfo["name"] = "Lite"
    imgname = "lite"
    imginfo["latestname"] = "comitup-lite"
else:
    imginfo["name"] = ""
    imgname = "full"
    imginfo["latestname"] = "comitup"

latestpath = "latest/{}-img-latest.html".format(imginfo["latestname"])

imginfo["filename"] = zip_name
zf = zipfile.ZipFile(zip_path)
imginfo["uncompressed"] = zf.infolist()[0].file_size
zf.close()
imginfo["compressed"] = os.stat(zip_path).st_size
imginfo["uncompressedstr"] = numsum(imginfo["uncompressed"])
imginfo["compressedstr"] = numsum(imginfo["compressed"])
imginfo["infoname"] = info_name


with open("imgs.json", "r") as fp:
    imgsinfo = json.load(fp)

imgsinfo[imgname] = imginfo

with open("imgs.json", "w") as fp:
    json.dump(imgsinfo, fp, indent=4, sort_keys=True)

template = Template(open("templates/latest-img.tmpl").read())
output = template.render(img=zip_name)
with open(latestpath, "w") as fp:
    fp.write(output)

os.system(
    "otto upload {} {}".format(zip_path, info_path)
)

os.system("./makesite")
