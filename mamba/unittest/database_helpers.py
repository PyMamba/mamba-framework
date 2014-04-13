# -*- test-case-name: mamba.test.test_unittest -*-
# Copyright (c) 2012 ~ 2014 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: database_helpers
    :platform: Unix, Windows
    :synopsis: Helper to make unit testing easier

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

import os
import tempfile
from sqlite3 import sqlite_version_info

from storm.zope.interfaces import IZStorm
from storm.zope.zstorm import global_zstorm
from zope.component import provideUtility, getUtility
from twisted.python.constants import NamedConstant, Names

from mamba.utils import config
from mamba.application.model import Model
from mamba.enterprise.database import Database
from mamba.test.test_model import DummyThreadPool


class ENGINE(Names):
    """Constants representing different ENGINE options
    """

    NATIVE = NamedConstant()        # what is configured
    INMEMORY = NamedConstant()      # in memory SQLite
    PERSISTENT = NamedConstant()    # persistent SQLite


class TestableDatabase(Database):
    """Testable database object
    """

    pool = DummyThreadPool()

    def __init__(self, engine=ENGINE.NATIVE):
        super(TestableDatabase, self).__init__(testing=True)
        self.engine = engine
        self.tmp_file = None
        self._initialize()

    def __del__(self):
        if self.tmp_file is not None:
            os.unlink(self.tmp_file)
            self.tmp_file = None

    def _initialize(self):
        """Initialize the object with the right database configuration
        """

        provideUtility(global_zstorm, IZStorm)
        zstorm = getUtility(IZStorm)
        zstorm._reset()  # make sure we are not using an old configuration
        if self.engine == ENGINE.NATIVE:
            if self.backend == 'sqlite' and sqlite_version_info >= (3, 6, 19):
                uri = '{}?foreign_keys=1'.format(config.Database().uri)
            else:
                uri = config.Database().uri
        elif self.engine == ENGINE.INMEMORY:
            if sqlite_version_info >= (3, 6, 19):
                uri = 'sqlite:?foreign_keys=1'
            else:
                uri = 'sqlite:'
        else:
            tmpfile = tempfile.NamedTemporaryFile(delete=False)
            self.tmp_file = tmpfile.name
            if sqlite_version_info >= (3, 6, 19):
                uri = 'sqlite:{}?foreign_keys=1'.format(tmpfile.name)
            else:
                uri = 'sqlite:{}'.format(tmpfile.name)
            tmpfile.close()

        zstorm.set_default_uri('mamba', uri)
        self.started = True

    def start(self):
        """Stub method that mimic Database.start
        """

        if not self.started:
            self.started = True

    def stop(self):
        """Stub method that mimic Database.stop
        """

        if self.started:
            self.started = False


def prepare_model_for_test(model, engine=ENGINE.INMEMORY):
    """Prepare the given model to be testable

    :param model: the model to make testable
    :type model: :class:`~mamba.application.model.Model`
    """

    testable_database = TestableDatabase(engine)
    if isinstance(model, type) and (
        model.__name__ == 'Model'
            or 'Model' in [base.__class__.__name__ for base in model.__bases__]
            or model.__base__.__name__ == 'Model'):
        model.database = testable_database
    elif isinstance(model, Model):
        model.__class__.database = testable_database
        model.transactor._threadpool = model.database.pool
    else:
        raise RuntimeError(
            'prepare_model_for_test expects a Model object or instance, '
            'get {} instead'.format(type(model))
        )
