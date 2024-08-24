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

#### The Better Way

Get the latest <a href="deb/{{ latest["davesteele-comitup-apt-source"] }}">davesteele-comitup-apt-source deb</a> file from the <a href="archive.html">archive</a>.
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

#### The Old Way

First, add a reference to the comitup repository to your <code>/etc/apt/sources.list</code> file (as root):<br><br>
<pre>
deb http://davesteele.github.io/comitup/repo comitup main</pre>
Add the repository key to your apt key ring:<br><br>
<pre>
$ wget https://davesteele.github.io/key-366150CE.pub.txt
$ sudo apt-key add key-366150CE.pub.txt
</pre>
Install the packages with :<br><br>
<pre>
$ sudo apt-get update
$ sudo apt-get install comitup
</pre>
The packages will be updated with every 'apt-get upgrade'.<br><br>
