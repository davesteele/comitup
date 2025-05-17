---
layout: default
---

[back](index.html)

### Using the comitup repository

Here is how to add comitup to apt repository resources for your system, letting you install and
automatically upgrade with standard tools. 
Note that <a href="https://github.com/davesteele/comitup/wiki/Installing-Comitup">additional steps</a> may be needed.
<br><br>

Be sure to see the [Installing Comitup](https://github.com/davesteele/comitup/wiki/Installing-Comitup) wiki page for possible issues when installing the package directly.

Get the latest <a href="deb/davesteele-comitup-apt-source_1.3_all.deb">davesteele-comitup-apt-source deb</a> file from the <a href="archive.html">archive</a>.
<br><br>
Install the deb:<br><br>
<pre>
$sudo dpkg -i davesteele-comitup-apt-source*.deb
</pre>

Install the packages with :<br><br>
<pre>
$ sudo apt-get update
$ sudo apt-get install comitup
</pre>

The packages will be updated with every 'apt-get upgrade'.<br><br>
