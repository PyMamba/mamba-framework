===============
Mamba Framework
===============

Mamba is a high-level Web Applications framework based on Twisted, Storm and Jinja2.

<table>
  <tr>
    <td align="center"><strong>Author:</strong></td><td>Oscar Campos &lt;<a href="mailto:oscar.campos@member.fsf.org">oscar.campos@member.fsf.org</a>&gt;</td>
  </tr>
</table>

[![Build Status](https://travis-ci.org/PyMamba/mamba-framework.svg?branch=master)](https://travis-ci.org/PyMamba/mamba-framework) [![Downloads](https://pypip.in/d/mamba-framework/badge.png)](https://crate.io/packages/mamba-framework/)

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
    <td>Mamba's Storm</td><td></td><td><a href="https://github.com/PyMamba/mamba-storm" target="_blank">https://github.com/PyMamba/mamba-storm</a></td>
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

Mamba uses [Travis CI](https://travis-ci.org) as CI solution. We offered a custom Buildbot solution but recently we run into problems to maintain it's infrastrcuture so we move our architecture to a more comfortable 3rd party hosted service as Travis CI is.

Known platforms where Mamba runs
--------------------------------
Mamba has been hardly tested on GNU/Linux and OS X. It is maintained as most compatible as we can with the following operating systems:

  * GNU/Linux
  * FreeBSD
  * OS X
  * Windows

Altough is untested, mamba will probably work in also in other BSDs and Plan 9.

Known Python implementations where Mamba runs
---------------------------------------------

Mamba can also run in the following Python implementations, please take care of the note in the list

  * CPython
  * PyPy
  * Stackless Python

When running in PyPy psycopg2ct has to be installed to make PostgreSQL work, you can experience random crashes of the PyPy interpreter under MySQL and PostgreSQL big loads, SQLite seems to work fine.

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
