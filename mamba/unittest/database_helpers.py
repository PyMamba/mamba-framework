# -*- test-case-name: mamba.test.test_unittest -*-
# Copyright (c) 2013 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: database_helpers
    :platform: Unix, Windows
    :synopsis: Helper to make unit testing easier

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

from twisted.python.constants import NamedConstant, Names

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
        super(TestableDatabase, self).__init__()
        self.engine = engine


def prepare_model_for_test(model):
    """Prepare the given model to be testable

    :param model: the model to make testable
    :type model: :class:`~mamba.application.model.Model`
    """

    if isinstance(model, type) and model.__name__ == 'Model':
        model.database = TestableDatabase()
    elif isinstance(model, Model):
        model.__class__.database = TestableDatabase()
    else:
        raise RuntimeError(
            'prepare_model_for_test expects a Model object or instance, '
            'get {} instead'.format(type(model))
        )
