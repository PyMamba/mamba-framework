=====
Mamba
=====

Mamba is a high-level Web Applications framework based on Twisted, Storm and Jinja2.

<table>
  <tr>
    <td align="center"><strong>Author:</strong></td><td>Oscar Campos &lt;<a href="mailto:oscar.campos@member.fsf.org">oscar.campos@member.fsf.org</a>&gt;</td>
  </tr>
</table>

[![Downloads](https://pypip.in/d/mamba-framework/badge.png)](https://crate.io/packages/mamba-framework/)

Minimum Dependencies
====================
<table>
  <tr>
    <td>Library</td><td>Version</td><td>Web Site</td>
  </tr>
  <tr>
    <td>Python</td><td>2.7.x</td><td><a href="http://python.org" targte="_blank">http://python.org</a></td>
  </tr>
  <tr>
    <td>Twisted</td><td>>= 10.2.0</td><td><a href="http://www.twistedmatrix.com" target="_blank">http://www.twistedmatrix.com</a></td>
  </tr>
  <tr>
    <td>Storm</td><td>>= 0.19</td><td><a href="http://storm.canonical.com" target="_blank">http://storm.canonical.com</a></td>
  </tr>
  <tr>
    <td>Jinja2</td><td>>= 2.4</td><td><a href="http://jinja.pocoo.org/docs/#" target="_blank">http://jinja.pocoo.org/docs/</a></td>
  </tr>
  <tr>
    <td>singledispatch</td><td>>=3.4.0.1</td><td><a href="https://pypi.python.org/pypi/singledispatch" target="_blank">https://pypi.python.org/pypi/singledispatch</a></td>
  </tr>
</table>

There are other requirements in order to run the test suite or build the documentation, for more information, please check the [mamba main site](http://www.pymamba.com).


Build Status
============

Mamba uses [buildbot](http://buildbot.net/ "BuildBot") as CI solution. At the moment we provide build tests for the following systems and Python implementations:

Known platforms where Mamba runs
--------------------------------
There is no reason to believe that Mamba does not run under Microsoft Windows or Mac OS X operating systems but
this was not tested and we have no `buildbot slaves` under those operating systems to check it out (any contribution is welcome).

<table>
  <tr>
    <td></td>
    <td align="center">
      <strong>Ubuntu 12.04</strong>
    </td>
    <td align="center">
      <strong>Ubuntu 10.04</strong>
    </td>
    <td align="center">
      <strong>Gentoo 2013</strong>
    </td>
    <td align="center">
      <strong>FreeBSD 9.1</strong>
    </td>
    <td align="center">
      <strong>Windows7</strong>
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>CPython</strong>
    </td>
    <td align="center">
        <img align="center" src="http://buildbot.pymamba.com/png?builder=Ubuntu-12.04-python2.7.3&size=large" />
    </td>
    <td align="center">
        <img align="center" src="http://buildbot.pymamba.com/png?builder=Ubuntu-10.04-CPython2.7.4&size=large" />
    </td>
    <td align="center">
        <img align="center" src="http://buildbot.pymamba.com/png?builder=Gentoo-2013-Python2.7&size=large" />
    </td>
    <td align="center">
        <img align="center" src="http://buildbot.pymamba.com/png?builder=FreeBSD-9.1_amd64_python2.7&size=large" />
    </td>
    <td align="center">
        <img align="center" src="http://buildbot.pymamba.com/png?builder=Windows7-Python2.7&size=large" />
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>PyPy</strong>
    </td>
    <td align="center">
        <img src="http://buildbot.pymamba.com/png?builder=Ubuntu-12.04-pypy&size=large" />
    </td>
    <td align="center">
        <img src="http://buildbot.pymamba.com/png?builder=Ubuntu-10.04-pypy1.9&size=large" />
    </td>
    <td align="center">
        <img align="center" src="http://buildbot.pymamba.com/png?builder=Gentoo-2013-PyPy2.0&size=large" />
    </td>
    <td align="center">
        <img align="Center" src="http://buildbot.pymamba.com/png?builder=FreeBSD-9.1_amd64_pypy&size=large" />
    </td>
    <td align="center">
        <img align="center" src="http://buildbot.pymamba.com/png?builder=Windows7-PyPy&size=large" />
    </td>
  </tr>
  <tr>
    <td align="center"><strong>NOTES</strong></td>
    <td colspan="6">All the platforms listed here are supported by Mamba. We are looking for volunteers
    that want to contribute with a buildbot slave for all the 'unknown' listed platforms here and new operating systems.
  </tr>
</table>

If you want to know more about Mamba's buildbot you can check our [BuildBot Waterfall](http://buildbot.pymamba.com).

Project Documentation
=====================
All the project's documentation can be built using `Sphinx` and `make html` in the docs directory.
You can also refer to the [Mamba Web Site](http://www.pymamba.com) where you can find all the project's documentation.

Additional Notes
================
Mamba is under heavy development at this moment and there is no `stable release`. All the API's (internal or not) may (and should)
change without any previous warning until we release a first stable release.

=======
License
=======
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

Have a look at the [LICENSE](https://raw.github.com/DamnWidget/mamba/master/LICENSE) file to read the full license

======
Donate
======

[![PayPal](https://www.paypalobjects.com/en_US/i/btn/btn_donate_SM.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=KP7PAHR962UGG&lc=US&currency_code=EUR&bn=PP%2dDonationsBF%3abtn_donate_SM%2egif%3aNonHosted)
[<img src="https://api.flattr.com/button/flattr-badge-large.png" />][0]

[0]: http://flattr.com/thing/1765363/
