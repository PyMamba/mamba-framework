# -*- test-case-name: mamba.test.test_database -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. plugin:: storm
    :platform: Unix, Windows
    :synopsis: Storm ORM Database Acces implementation for Mamba.

.. pluginauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

from zope.componenet import provideUtility, getUtility
import transaction

from storm.uri import URI
from storm.zope.interfaces import IZStorm
from storm.zope.zstorm import global_zstorm
from storm.twisted.transact import Transactor, transact
from storm.database import create_database, register_scheme

from mamba.enterprise.database import DatabaseProvider


class Storm(DatabaseProvider):
    """
    Storm ORM database provider for Mamba.
    """

    def __init__(self):
        provideUtility(global_zstorm, IZStorm)
        self.zstorm = getUtility(IZStorm)