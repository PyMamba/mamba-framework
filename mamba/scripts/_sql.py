# -*- test-case-name: mamba.scripts.test.test_mamba_admin -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

from __future__ import print_function

import re
import sys
import datetime
from cStringIO import StringIO

from storm.uri import URI
from twisted.python import usage

from mamba import copyright
from mamba.scripts import commons
from mamba.enterprise import database
from mamba.test.test_model import DummyThreadPool
from mamba.utils.output import darkred, darkgreen
from mamba.application.model import ModelManager, Model

__version__ = '0.1.0'


def show_version():
    print('Mamba Sql Tools v{}'.format(__version__))
    print('{}'.format(copyright.copyright))


def mamba_services_not_found():
    print(
        'error: make sure you are inside a mmaba application root '
        'directory and then run this command again'
    )
    sys.exit(-1)


class SqlConfigOptions(usage.Options):
    """Sql Configuration options for mamba-admin tool
    """
    synopsis = '[options]'

    optFlags = [
        ['autoadjust-pool', 'p', 'Auto adjust the database thread pool size?'],
        ['create-if-not-exists', None,
            'If present, when mamba try to create a new table adds an '
            '`IF EXISTS` clause to the SQL query'],
        ['drop-table', None, 'If present, mamba will drop any table (if '
            'exists) before to create it. Note this option is not compatible '
            'with `create-if-not-exists'],
        ['drop-if-exists', None,
            'If present, mamba will add an `IF EXISTS` clause to any intent '
            'to DROP a table'],
        ['non-restrict', None, 'If present, mamba will NOT use restrict drop'],
        ['cascade', None, 'If present, mamba will use CASCADE in drops'],
        ['noquestions', 'n',
            'When this option is set, mamba will NOT ask anything to the user '
            'that means it will delete any previous database configuration '
            'and will accept any options that are passed to it (even default '
            'ones).'
            'Use with caution']
    ]

    optParameters = [
        ['uri', 'U', 'sqlite',
            'The database connection URI as is used in Storm. Those are '
            'acceptable examples of format:\n\nbackend:database_name\n'
            'backend://hostname/database_name\n'
            'backend://hostname:port/database_name\n'
            'backend://username:password@hostname/database_name\n'
            'backend://hostname/database_name?option=value\n'
            'backend://username@/database_name\n\nWhere backend can be one of '
            ' sqlite, mysql or postgres. For example:\n\nsqlite:app_db\n'
            'slite:/tmp/tmp_database\nsqlite:db/my_app_db\n'
            'mysql://user:password@hostname/database_name\n'
            'postgres://user:password@hostname/database_name\n\nNote that you '
            'can also use --hostname --user and --password options instead of '
            'the URI syntax', str],
        ['min-threads', None, 5,
            'Minimum number of threads to use by the thread pool', int],
        ['max-threads', None, 20,
            'Maximum number of thread to use by the thread pool', int],
        ['hostname', None, None, 'Hostname (this is optional)', str],
        ['port', None, None, 'Port (this is optional)', int],
        ['username', None, None,
            'Username which connect to (this is optional)', str],
        ['password', None, None,
            'Password to connect (this is optional)', str],
        ['backend', None, 'sqlite',
            'SQL backend to use. Should be one of [sqlite|mysql|postgres] '
            '(this is optional but should be present if no URI is being to be '
            'used)', str],
        ['database', None, None,
            'database (this is optional but should be suply if not using '
            'URI type configuration)', str],
        ['path', None, None, 'database path (only for sqlite)'],
        ['option', None, None, 'SQLite additional option']
    ]

    def opt_version(self):
        """Show version information and exit
        """
        show_version()
        sys.exit(0)

    def postOptions(self):
        """Post options processing
        """
        if self['drop-table'] and self['create-if-not-exists']:
            raise usage.UsageError, (
                'you must choose between `create-if-not-exists` and '
                '`drop-table` behaviour for table creation'
            )

        if self['min-threads'] <= 0:
            raise usage.UsageError, (
                'min-threads should be a positive value greater than zero'
            )

        if self['max-threads'] <= 4 or self['max-threads'] > 1024:
            raise usage.UsageError, (
                'max-threads should be a positive number between 5 and 1024'
            )

        if self['username'] is not None or self['hostname'] is not None:
            if self['hostname'] is None:
                self['hostname'] = 'localhost'

            if self['backend'] not in ('sqlite', 'mysql', 'postgres'):
                raise usage.UsageError, (
                    'backend must be one of sqlite, mysql or postgres'
                )

            if self['database'] is None:
                raise usage.UsageError, (
                    'you should suply a database to connect'
                )

            self['uri'] = self._generate_uri()

    def _generate_uri(self):
        """Generate an URI string through --hostname and friends options
        """

        if self['backend'] == 'sqlite':
            uri = 'sqlite:{path}{option}'.format(
                path=self['path'] if self['path'] is not None else '',
                option='?' + self['option'] if self['option'] else ''
            )
        else:
            password = self['password'] if self['password'] is not None else ''

            uri = (
                '{b}://{user}{colon}{password}{at}{host}{port_colon}{port}/'
                '{database_name}'.format(
                    b=self['backend'],
                    user=self['username'] if self['username'] else '',
                    colon=':' if self['password'] is not None else '',
                    password=password,
                    at='@' if self['username'] is not None else '',
                    host=self['hostname'],
                    port_colon=':' if self['port'] is not None else '',
                    port=self['port'] if self['port'] is not None else '',
                    database_name=self['database']
                )
            )

        return uri


class SqlCreateOptions(usage.Options):
    """Sql Create options for mamba-admin tool
    """
    synopsis = '[options] <file>'

    optFlags = [
        ['dump', 'd', 'dump SQL scripts to standrad output'],
        ['live', 'l', 'live changes to the databse using database config file']
    ]

    def parseArgs(self, file=None):
        """Parse command arguments
        """

        if file is None:
            self['file'] = None
        else:
            self['file'] = file if file.endswith('.sql') else '{}.sql'.format(
                file)

    def opt_version(self):
        """Print version information and exit
        """
        show_version()
        sys.exit(0)

    def postOptions(self):
        """Post options processing
        """

        if self['file'] is None and not self['dump'] and not self['live']:
            print(self)

        if self['live'] and (self['dump'] or self['file'] is not None):
            if commons.Interaction.userchoice(
                'What do you want to do. Dump the script or execute it?',
                ('1', '2'), ('Dump it', 'Execute it')
            ) == '1':
                self['live'] = 0
            else:
                self['dump'] = 0
                self['file'] = None


class SqlDumpOptions(usage.Options):
    """Sql Dump options for mamba-admin tool
    """
    synopsis = '<file>'

    def parseArgs(self, file=None):
        """Parse command arguments
        """

        if file is None:
            self['file'] = None
        else:
            self['file'] = file if file.endswith('.sql') else '{}.sql'.format(
                file)

    def opt_version(self):
        """Print version information and exit
        """
        show_version()
        sys.exit(0)


class SqlResetOptions(usage.Options):
    """Sql Reset options for mamba-admin tool
    """
    synopsis = '[options]'

    def opt_version(self):
        """Show version information and exit
        """
        show_version()
        sys.exit(0)


class SqlOptions(usage.Options):
    """Sql options for mamba-admin tool
    """
    synopsis = '[options] command'

    optFlags = [
        ['version', 'V', 'display version information and exit']
    ]
    subCommands = [
        ['configure', None, SqlConfigOptions,
            'Configure the application database (generates .json file)'],
        ['create', None, SqlCreateOptions,
            'Create or dump SQL from the application model'],
        ['dump', None, SqlDumpOptions,
            'Dump a database to the local file system'],
        ['reset', None, SqlResetOptions,
            'Reset the application database (this means all the data should '
            'be deleted. Use with caution)']

    ]

    def opt_version(self):
        """Print version information and exit
        """
        show_version()
        sys.exit(0)


class Sql(object):
    """
    Sql configuration and tools

    :param options: the command line options
    :type options: :class:`~mamba.scripts._sql.SqlOptions`
    """

    def __init__(self, options):
        self.options = options

        self.process()

    def process(self):
        """I process the Sql commands
        """

        if self.options.subCommand == 'configure':
            self._handle_configure_command()
        elif self.options.subCommand == 'create':
            self._handle_create_command()
        elif self.options.subCommand == 'dump':
            self._handle_dump_command()
        else:
            print(self.options)

    def _handle_configure_command(self):
        """Take care of SQL configuration to generate config/database.json file
        """

        try:
            mamba_services = commons.import_services()
        except Exception:
            mamba_services_not_found()

        if not self.options.subOptions.opts['noquestions']:
            query = (
                'You are going to generate (and possible overwrite) a '
                'database.json configuration file for your database. Are you '
                'sure do you want to do that? (Ctrl+c to abort)'
            )
            if commons.Interaction.userquery(query) == 'No':
                print('Skiping...')
                sys.exit(0)

        options = {
            'uri': self.options.subOptions.opts['uri'],
            'min_threads': self.options.subOptions.opts['min-threads'],
            'max_threads': self.options.subOptions.opts['max-threads'],
            'auto_adjust_pool_size': (True if (
                self.options.subOptions.opts['autoadjust-pool'])
                else False
            ),
            'create_table_behaviours': {
                'create_table_if_not_exists': (True if (
                    self.options.subOptions.opts['create-if-not-exists'])
                    else False
                ),
                'drop_table': (True if (
                    self.options.subOptions['drop-table']) else False
                )
            },
            'drop_table_behaviours': {
                'drop_if_exists': (True if(
                    self.options.subOptions.opts['drop-if-exists']) else False
                ),
                'restrict': (False if(
                    self.options.subOptions.opts['non-restrict']) else True
                ),
                'cascade': (True if(
                    self.options.subOptions.opts['cascade']) else False
                )
            }
        }

        try:
            print('Wriing databse config file...'.ljust(73), end='')
            mamba_services.config.Database.write(options)
            print('[{}]'.format(darkgreen('Ok')))
        except OSError:
            print('[{}]'.format(darkred('Fail')))
            raise
            sys.exit(-1)

    def _handle_create_command(self):
        """Take care of SQL creation scripts using the application model
        """

        try:
            mamba_services = commons.import_services()
        except Exception:
            mamba_services_not_found()

        # load database configuration
        mamba_services.config.Database('config/database.json')

        # this is needed to don't have a reactor waiting forever
        db = database.Database(DummyThreadPool())
        Model.database = db

        # headers and footer
        mamba_services.config.Application('config/application.json')

        stdout = sys.stdout
        capture = StringIO()
        sys.stdout = capture

        # generate script
        print(db.dump(ModelManager()))

        sys.stdout = stdout

        if self.options.subOptions.opts['file'] is not None:
            with open(self.options.subOptions.opts['file'], 'w') as dump_file:
                dump_file.write(capture.getvalue())

        if self.options.subOptions.opts['dump']:
            print(capture.getvalue())

        if self.options.subOptions.opts['live']:
            if mamba_services.config.Database().create_table_behaviours.get(
                'drop_table'
            ) is True:
                pattern = re.compile(r'((?<=:)[\w\d\$]+(?=@))')
                question = (
                    'You have `DROP TABLE` option set as True in your '
                    'creation tables configuration behaviour, this means '
                    'Mamba will perform a table drop before create any table '
                    'so you can lose important data if the table exists and '
                    'this is a production system\n\nAre you sure do you want '
                    'to run this query in the {} database?'
                ).format(
                    pattern.sub('*****', mamba_services.config.Database().uri)
                )

                if commons.Interaction.userquery(question) == 'Yes':
                    real_database = database.Database()
                    store = real_database.store()
                    if real_database.backend == 'sqlite':
                        # the pysqlite module does not allow us to use more
                        # than one operations per query
                        for operation in capture.getvalue().split(';'):
                            store.execute(operation)
                    else:
                        store.execute(capture.getvalue())
                    store.commit()

        sys.exit(0)

    def _handle_dump_command(self):
        """Take care of SQL dumping
        """

        try:
            mamba_services = commons.import_services()
        except Exception:
            mamba_services_not_found()

        # load database configuration
        mamba_services.config.Database('config/database.json')
        db = database.Database(DummyThreadPool())
        Model.database = db
        stdout = sys.stdout
        capture = StringIO()
        sys.stdout = capture

        print(db.dump(ModelManager(), True))

        sys.stdout = stdout

        if self.options.subOptions.opts['file'] is None:
            print(capture.getvalue())
        else:
            with open(self.options.subOptions.opts['file'], 'w') as dump_file:
                dump_file.write(capture.getvalue())

        sys.exit(0)
