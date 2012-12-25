# -*- test-case-name: mamba.test.test_mamba -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: model
    :platform: Linux
    :synopsis: Models for web projects that encapsulates Storm objects.

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

from zope.component import provideUtility, getUtility
import transaction
from storm.zope.interfaces import IZStorm
from storm.zope.zstorm import global_zstorm
from storm.twisted.transact import Transactor, transact


class Model(object):
    """
    All the models in the application should inherit from this class.

    We use the new :class:`storm.twisted.transact.Transactor` present in
    the 0.19 version of Storm to run transactions that will block the
    reactor using a :class:`twsited.python.threadpool.ThreadPool` to
    execute them in different threads so our reactor will not be blocked.

    You must take care of don't return any **Storm** object from the
    methods that interacts with the :class:`storm.Store` underlying API
    because those ones are created in a different thread and cannot be
    used outside.

    We don't care about the instantiation of the **Storm**
    :class:`~storm.locals.Store` because we use :class:`zope.transaction`
    through :class:`storm.zope.zstorm.ZStorm` that will take care of create
    different instances of :class:`~storm.locals.Store` per thread for us.
    """

    pass
