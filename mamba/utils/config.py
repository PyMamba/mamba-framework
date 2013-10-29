# -*- test-case-name: mamba.test.test_config -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: configuration
    :platform: Unix, Windows
    :synopsis: JSON Configuration parser

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

import os
import json

from twisted.python import filepath

from mamba.utils import borg, output


class BaseConfig(borg.Borg):
    """
    Base Configuration object
    """

    def __init__(self):
        super(BaseConfig, self).__init__()
        if not hasattr(self, 'loaded'):
            self.loaded = False

    def load(self, config_file=''):
        file_desc = filepath.FilePath(config_file)
        try:
            with file_desc.open('r') as fd:
                try:
                    for key, value in json.loads(fd.read()).iteritems():
                        setattr(self, key.lower(), value)
                    self.loaded = True
                except ValueError:
                    self._defaults()
                    if self.loaded:
                        self.loaded = False

                    print(
                        output.red(
                            '{}: Invalid config file {}, falling back to '
                            'default settings {}'.format(
                                self.__class__.__name__, config_file, self
                            )
                        )
                    )
        except IOError:
            if not self.loaded or config_file in ['clean', 'default']:
                self._defaults()
                if self.loaded:
                    self.loaded = False


class Database(BaseConfig):
    """
    Database configuration object

    This object load and parses the configuration details for the database
    access using a JSON configuration file with this format:

     .. sourcecode:: javascript

        {
            'uri': 'sqlite:',
            'min_threads': 5,
            'max_threads': 20,
            'auto_adjust_pool_size': false,
            'create_table_behaviours': {
                'create_table_if_not_exists': true,
                'drop_table': false
            },
            'drop_table_behaviours': {
                'drop_if_exists': true,
                'restrict': true,
                'cascade': false
            }
        }

    Where uri is the Storm URI format for create ZStores and min, max threads
    are the minimum and maximum threads in the thread pool for operate with
    the database. If auto_adjust_pool_size is True, the size of the thread
    pool should be adjust dynamically.

    For *create_table_bevaviour* possible values are:

        *create_if_not_exists*
            this is the default behaviour and it should add 'IF DONT EXISTS'
            to the table creation scripts

        *drop_table*
            this behaviour will always drop a table before try to create it.
            Be carefull with this behaviour because you can lose all your
            data if you dont take care of it


    If no config_file or invalid config_file is given at first load attempt,
    then a fallback default settings with a SQLite in memory table are
    returned back.

    If you loaded a valid config file and you instance the database config
    again with an invalid JSON format file, then a fallback default settings
    with SQLite in memory URI is returned back in order to preserve your
    data (if we don't fallback to a default configuration you can overwrite
    important data in your previous well configured environment).

    If you loaded a valid config file and pass a non existent or a void
    file in the constructor you get back your previous config so you can
    use it like a singleton instance::

        config.Database('path/to/my_valid/config.json')
        ...
        cfg = config.Database()


    If you want to clear your config and return it back to a default
    state you should pass 'clean' or 'default' as parameter::

        config.Database('default')

    :param config_file: the file to load the configuration from, it can (and
                        should) be empty to get back the previous configured
                        data
    :type config_file: str
    """

    def __init__(self, config_file='config/database.json'):
        super(Database, self).__init__()
        self.load(config_file)

    def _defaults(self):
        """Set default data to config"""
        self.uri = 'sqlite:'
        self.min_threads = 5
        self.max_threads = 20
        self.auto_adjust_pool_size = False
        self.create_table_behaviours = {
            'create_table_if_not_exists': True,
            'drop_table': False
        }
        self.drop_table_behaviours = {
            'drop_if_exists': True,
            'restrict': True,
            'cascade': False
        }

    @staticmethod
    def write(options):
        """
        Write options to the configuration file

        :param options: the options from the mamba-admin commands tool
        :type options: dict
        """

        config_file = filepath.FilePath(
            '{}/config/database.json'.format(filepath.abspath('.'))
        )
        config_file.open('w').write(json.dumps(options, indent=4))

    def __repr__(self):
        return 'config.Database(%s)' % (
            ', '.join(map(repr, [
                self.uri, self.min_threads, self.max_threads,
                self.auto_adjust_pool_size, self.create_table_behaviours,
                self.drop_table_behaviours]))
        )


class NoSQL(BaseConfig):
    """
    """

    def __init__(self, config_file=''):
        super(NoSQL, self).__init__()
        self.load(config_file)

    def _defaults(self):
        self.uri = ''


class Application(BaseConfig):
    """
    Application configuration object

    This object loads and parses the Mamba application configuration options
    using a JSON file with the following format:

    .. sourcecode:: json

        {
            "name": "Mamba Application",
            "description": "Mamba application description",
            "version": 1.0
            "port": 8080,
            "doctype": "html",
            "content_type": "text/html",
            "description": "My cool application",
            "language": "en",
            "description": "This is my cool application",
            "favicon": "favicon.ico",
            "platform_debug": false,
            "development": true,
            "debug": false
        }

    If we want to force the mamba application to run under some specific
    twisted reactor, we can add the `"reactor"` option to the configuration
    file to enforce mamba to use the configured reactor.

    .. warning:

        The configured reactor must be installed and be usable in the platform

    :param config_file: the JSON file to load
    :type config_file: str
    """

    def __init__(self, config_file=''):
        super(Application, self).__init__()

        self.language = os.environ.get('LANG', 'en_EN').split('_')[0]

        self.load(config_file)

    def _defaults(self):
        """Set dedault data to config
        """

        self.log_file = None
        self.name = None
        self.port = None
        self.debug = False
        self.doctype = 'html'
        self.content_type = 'text/html'
        self.description = None
        self.favicon = 'favicon.ico'
        self.lessjs = False
        self.platform_debug = False
        self.development = False
        self.auto_select_reactor = False


class InstalledPackages(BaseConfig):
    """
    Instaleld Packages configuration object

    This object loads and parses configuration that indicates to the Mamba
    framework that this application have to import and register the indicated
    shared packages.

    The JSON file must follow this format:

    .. sourcecode:: json

        {
            "packages": {
                "package_one": {"autoimport": true, "use_scripts": true},
                "package_two": {"autoimport": true, "use_scripts": false},
                "package_three": {"autoimport": false, "use_scripts": true}
            }
        }

    The packages *must* be installed already in the system

    :param config_file: the JSON file to load
    :type config_file: str
    """

    def __init__(self, config_file=''):
        super(InstalledPackages, self).__init__()

        self.load(config_file)

    def _defaults(self):
        """Set default data to config
        """

        self.packages = {}


__all__ = ['Database', 'Application']
