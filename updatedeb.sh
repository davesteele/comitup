#!/bin/sh

git checkout debian -- debian/changelog
if (head -1 debian/changelog | grep UNRELEASED ); then
  echo "Latest changelog is UNRELEASED"
  exit 1
fi
rm debian/changelog
rmdir debian
git rm debian/changelog

cp ../comitup*deb deb/
cp ../davesteele-comitup-apt-source*deb deb/
cp ../python3-networkmanager*deb deb/

cd deb
echo MD5Sum >checksums.txt
md5sum *deb >>checksums.txt
echo "\nSHA1" >>checksums.txt
sha1sum *deb >>checksums.txt
echo "\nSHA256" >>checksums.txt
sha256sum *deb >>checksums.txt
echo  >>checksums.txt

gpg --clearsign checksums.txt
rm checksums.txt
mv checksums.txt.asc checksums.txt

cd ..

./mkjson

cd man
./makeman
cd ..

./updaterepo.py

./makesite
