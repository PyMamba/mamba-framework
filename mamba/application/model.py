# -*- test-case-name: mamba.test.test_model -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: model
    :platform: Linux
    :synopsis: Models for web projects that encapsulates Storm objects.

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

import inspect
from os.path import normpath
from collections import OrderedDict

from storm.uri import URI
from twisted.python import log
from storm.expr import Desc, Undef
from storm.twisted.transact import Transactor
from storm.properties import PropertyPublisherMeta, PropertyColumn

from mamba import plugin
from mamba.utils import config
from mamba.core import interfaces, module
from mamba.enterprise.database import Database, AdapterFactory, transact


class MambaStorm(PropertyPublisherMeta, plugin.ExtensionPoint):
    """Metaclass for solve conflicts when using Storm base classes

    If you need to inherit your models from :class:`storm.base.Storm`
    class in order to use references before the referenced object had
    been created in the local scope, you need to set your class
    __metaclass__ as model.MambaStorm to prevent metaclasses inheritance
    problems. For example::

        class Foo(model.Model, Storm):

            __metaclass__ = model.MambaStorm

    warning::

        Mamba support for database dump and SQL Schema generation through
        Storm classes is possible because a monkeypatching and hack of
        regular Storm behaviour, if you are not using Storm base classes
        for your Reference's and ReferenceSet's you may experience weird
        behaviours like not all the object columns being displayed in your
        generated schema.

        You should use mamba.application.model.MambaStorm metaclass
        and storm.base.Storm classes in order to fix it
    """
    pass


class ModelError(Exception):
    """Base class for Model Exceptions
    """


class InvalidModelSchema(ModelError):
    """Fired when an invalid scheme is detected
    """


class ModelProvider:
    """Mount point for plugins which refer to Models for our applications
    """

    __metaclass__ = plugin.ExtensionPoint


class Model(ModelProvider):
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
        self.__mamba_async__ = getattr(self, '__mamba_async__', True)

        if not self.database.started:
            self.database.start()

        self.transactor = Transactor(self.database.pool)

    def __new__(cls, *args, **kwargs):
        """This method is remembering the fields in the order that
        they were declared in the model. This is used to maintain
        declared order in the generated SQL schema. It uses some
        inspection to determine what fields should put on the ordered
        list. It, then, replaces cls._storm_columns with the ordered
        one, in order to maintain full interface compatibility.
        """
        columns = inspect.getmembers(
            cls, lambda o: isinstance(o, PropertyColumn)
        )

        creation_order = sorted(
            columns, key=lambda i: i[1]._creation_order
        )

        ordered_columns = OrderedDict()

        for _, ordered_property in creation_order:
            for column, property_ in cls._storm_columns.iteritems():
                if ordered_property is property_:
                    ordered_columns[column] = property_
                    break

        cls._storm_columns = ordered_columns
        return ModelProvider.__new__(cls, *args, **kwargs)

    @property
    def uri(self):
        """Returns the database URI for this model
        """

        if hasattr(self, '__uri__'):
            return self.__uri__

        return None

    def copy(self, orig):
        """Copy this object properties and return it
        """

        for column in self._storm_columns.keys():
            name = column._detect_attr_name(self.__class__)
            setattr(self, name, getattr(orig, name))

        return self

    def _set_empty_properties_to_none(self):
        """If a property is does not allow none and there is
        no default value for it, Storm itself will raise a NoneError
        when we set it to None.
        """
        for column, property_ in self._storm_columns.items():
            variable = property_.variable_factory()
            has_default = not variable._value is Undef
            value = getattr(
                self, column._detect_attr_name(self.__class__), None
            )
            if not variable._allow_none and not has_default and value is None:
                variable.set(None)

    def __storm_pre_flush__(self):
        """
        Storm calls this method before commiting a store.

        This is used right now to go through all the columns and setting
        them as None where the column is NOT NULL and there is no default
        value. If we don't do this, storm proceeds by inserting a 0, 0.0
        or '' (empty string), what is clearly wrong.
        """
        self._set_empty_properties_to_none()

    @transact
    def create(self):
        """Create a new register in the database
        """

        store = self.database.store()
        store.add(self)
        store.commit()

    @classmethod
    @transact
    def read(klass, id, copy=False):
        """
        Read a register from the database. The give key (usually ID) should
        be a primary key.

        .. warning:

        :param id: the ID to get from the database
        :type id: int
        """

        try:
            obj = klass()
        except TypeError:
            log.err(
                'Mamba cannot instantiate an object for class {}, please '
                'define default parameters on it\'s constructor'.format(
                    klass.__name__, klass.__name__)
            )
            raise

        store = obj.database.store()
        data = store.get(klass, id)

        if data is not None:
            if copy is True:
                data = obj.copy(data)
            data.transactor = obj.transactor

        return data

    @transact
    def update(self):
        """Update a register in the database
        """

        store = self.database.store()
        primary_key = self.get_primary_key()
        if primary_key is None:
            raise InvalidModelSchema(
                '{model} model does not define a primary key'.format(
                    model=self
                )
            )

        if type(primary_key) is tuple:
            args = []
            for key in primary_key:
                args.append(getattr(self.__class__, key) == getattr(self, key))
            copy = store.find(self.__class__, *args).one()
        else:
            value = getattr(self, primary_key)
            copy = store.find(
                self.__class__,
                getattr(self.__class__, primary_key) == value
            ).one()

        for column in self._storm_columns.values():
            setattr(copy, column.name, getattr(self, column.name))

        store.commit()

    @transact
    def delete(self):
        """Delete a register from the database
        """

        store = self.database.store()
        store.remove(self)

    @classmethod
    def find(klass, *args, **kwargs):
        """Find an object in the underlying database

        Some examples:

            model.find(Customer.name == u"John")
            model.find(name=u"John")
            model.find((Customer, City), Customer.city_id == City.id)

        .. versionadded:: 0.3.6
        """

        obj = klass
        if len(args) > 0 and (type(args[0]) == tuple or type(args[0]) == list):
            obj = args[0]

        return Transactor(klass.database.pool).run(
            klass.database.store().find, obj, *args, **kwargs
        )

    @classmethod
    def all(klass, order_by=None, desc=False, *args, **kwargs):
        """Return back all the rows in the database for this model

        :param order_by: order the resultset by the given field/property
        :type order_by: model property
        :param desc: if True, order the resultset by descending order
        :type desc: bool

        .. versionadded:: 0.3.6
        """

        def inner_transaction():
            store = klass.database.store()
            data = store.find(klass)
            if order_by is not None:
                data.order_by(Desc(order_by) if desc else order_by)

            return data

        return Transactor(
            klass.database.pool).run(inner_transaction, *args, **kwargs)

    @transact
    def create_table(self):
        """Create the table for this model in the underlying database system
        """

        store = self.database.store()
        store.execute(self.dump_table())

    @transact
    def drop_table(self):
        """Delete the table for this model in the underlying database system
        """

        adapter = self.get_adapter()
        store = self.database.store()
        store.execute(adapter.drop_table())

    def dump_table(self):
        """
        Dumps the SQL command used for create a table with this model

        :param schema: the SQL schema, SQLite by default
        :type schema: str
        """

        adapter = self.get_adapter()
        return adapter.create_table()

    def dump_data(self):
        """Dumps the SQL data
        """

        adapter = self.get_adapter()
        return adapter.insert_data()

    def dump_references(self):
        """Dump SQL references (used by PostgreSQL)
        """

        adapter = self.get_adapter()
        return adapter.parse_references()

    def dump_indexes(self):
        """Dump SQL indexes (used by PostgreSQL and SQLite)
        """

        adapter = self.get_adapter()
        return adapter.parse_indexes()

    def get_uri(self):
        """Return an URI instance using the uri config for this model
        """

        if self.uri is not None:
            uri = URI(self.uri)
        else:
            uri = URI(config.Database().uri)

        return uri

    def on_schema(self):
        """Checks if Mamba should take care of this model.
        """
        return getattr(self, '__mamba_schema__', True)

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
                'model {}. Error: {}'.format(
                    uri.scheme,
                    self.__class__.__name__,
                    error
                )
            )

        return adapter

    def get_primary_key(self):
        """Return back the model primary key (or keys if it's compound)
        """

        if not hasattr(self, '__storm_primary__'):
            for column in self._storm_columns.values():
                if column.primary == 1:
                    return column.name
        else:
            return self.__storm_primary__


class ModelManager(module.ModuleManager):
    """
    Uses a ModelProvider to load, store and reload Mamba Models.

    :attr:`_model_store` A private attribute that sets the prefix
    path for the models store
    :param store: if is not None it sets the _module_store attr
    """

    def __init__(self, store=None, package=None):
        """Initialize
        """

        self._module_store = 'application/model' if not store else store
        self._package = package
        super(ModelManager, self).__init__()

    def get_models(self):
        """Return the models pool
        """

        return self._modules

    def is_valid_file(self, file_path):
        """
        Check if a file is a Mamba model file

        :param file_path: the file path of the file to check
        :type file_path: str
        """

        if type(file_path) is not str:
            return self._valid_file(
                normpath('{}/{}'.format(
                    self._module_store, file_path.basename())
                ),
                'mamba-model'
            )

        return self._valid_file(
            normpath('{}/{}'.format(self._module_store, file_path)),
            'mamba-model'
        )
