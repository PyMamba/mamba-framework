# -*- test-case-name: mamba.test.test_mamba -*-

# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
Mamba is a high-level RAD Web Applications framework based on Twisted Web
with lot of steroids. You can use ExtJS4 or Sencha2 as frontend for your
web applications. HTML output is available too using the Jinja2 Templating
System.

To get detailed documentation visit: http://mamba.deliriumcoder.com
"""

import sys

if not hasattr(sys, "version_info") or sys.version_info < (2, 7):
    raise RuntimeError("Mamba requires Python 2.7 or later.")
del sys

# setup version
from _version import version
__version__ = version.short()
