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

# Fast Fix for PyPy incompatibilities with Storm cextesions
if '__pypy__' in sys.modules:
    # we are running on PyPy interpreter make sure we don't use the
    # Storm C extensions that make PyPy cpyext crash
    import os
    os.environ.update({'STORM_CEXTENSIONS': '0'})

del sys

# setup version
from _version import version
__version__ = version.short()

from .application import Mamba, ApplicationError
from .application import AppStyles
from .application import Controller, ControllerManager
from .application import Model
from .enterprise import Database
from plugin import ExtensionPoint


__all__ = [
    'Mamba', 'ApplicationError', 'AppStyles',
    'Controller', 'ControllerManager',
    'ExtensionPoint',
    'Model',
    'Database'
]
