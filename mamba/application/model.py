# -*- test-case-name: mamba.test.test_model -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: model
    :platform: Linux
    :synopsis: Models for web projects that encapsulates Storm objects.

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

from storm.uri import URI
from storm.twisted.transact import Transactor, transact

from mamba.utils import config
from mamba.core import interfaces
from mamba.enterprise.database import Database, AdapterFactory


class ModelError(Exception):
    """Base class for Model Exceptions
    """


class InvalidModelSchema(ModelError):
    """Fired when an invalid scheme is detected
    """


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

    database = Database()

    def __init__(self):
        super(Model, self).__init__()

        if not self.database.started:
            self.database.start()

        self.transactor = Transactor(self.database.pool)

    @property
    def uri(self):
        """Returns the database URI for this model
        """

        if hasattr(self, '__uri__'):
            return self.__uri__

        return None

    @transact
    def create(self):
        """Create a new register in the database
        """

        store = self.database.store(self)
        store.add(self)
        store.commit()

    @transact
    def read(self, id):
        """
        Read a register from the database. The give key (usually ID) should
        be a primery key.

        :param id: the ID to get from the database
        :type id: int
        """

        store = self.database.store(self)
        data = store.get(self.__class__, id)
        data.transactor = self.transactor

        return data

    @transact
    def update(self):
        """Update a register in the database
        """

        store = self.database.store(self)
        store.commit()

    @transact
    def delete(self):
        """Delete a register from the database
        """

        store = self.database.store(self)
        store.remove(self)

    @transact
    def create_table(self):
        """Create the table for this model in the underlying database system
        """

        store = self.database.store(self)
        store.execute(self.dump_table())

    @transact
    def drop_table(self):
        """Delete the table for this model in the underlying database system
        """

        adapter = self.get_adapter()
        store = self.database.store(self)
        store.execute(adapter.drop_table())

    def dump_table(self):
        """
        Dumps the SQL command used for create a table with this model

        :param schema: the SQL schema, SQLite by default
        :type schema: str
        """

        adapter = self.get_adapter()
        return adapter.create_table()

    def get_uri(self):
        """Return an URI instance using the uri config for this model
        """

        if self.uri is not None:
            uri = URI(self.uri)
        else:
            uri = URI(config.Database().uri)

        return uri

    def get_adapter(self):
        """Get a valid adapter for this model
        """

        uri = self.get_uri()

        try:
            adapter = interfaces.IMambaSQL(
                AdapterFactory(uri.scheme, self).produce()
            )
        except TypeError as error:
            raise InvalidModelSchema(
                'Invalid Model Schema {}, aborting table dumping for '
                'model {}. Error:'.format(
                    uri.scheme,
                    self.__class__.__name__,
                    error
                )
            )

        return adapter
