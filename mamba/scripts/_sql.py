# -*- test-case-name: mamba.scripts.test.test_mamba_admin -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

from __future__ import print_function

from twisted.python import usage

from mamba import copyright

__version__ = '0.1.0'


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
        ['cascade', None, 'If present, mamba will use CASCADE in drops']
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
        ['hostname', 'h', None, 'Hostname (this is optional)', str],
        ['port', 'p', None, 'Port (this is optional)', int],
        ['username', 'U', None,
            'Username which connect to (this is optional)', str],
        ['password', 'p', None, 'Password to connect (this is optional)', str],
        ['backend', 'b', 'sqlite',
            'SQL backend to use. Should be one of [sqlite|mysql|postgres] '
            '(this is optional but should be present if no URI is being to be '
            'used)', str],
        ['database', 'd', None,
            'database (this is optional but should be suply if not using '
            'URI type configuration)', str]
    ]

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

        if self['max-threads'] <= 4 or self['max-threads'] >= 1024:
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
            print(self['uri'])

    def _generate_uri(self):
        """Generate an URI string through --hostname and friends options
        """

        slash = self['backend'] if self['backend'] == 'sqlite' else ''
        password = self['password'] if self['password'] is not None else ''

        uri = (
            '{b}:{slash}{user}{colon}{password}{at}{host}{port_colon}{port}/'
            '{database_name}'.format(
                b=self['backend'],
                slash=slash,
                user=self['username'] if self['username'] is not None else '',
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

    def parseArgs(self, file):
        """Parse command arguments
        """

        self['file'] = file


class SqlDumpOptions(usage.Options):
    pass


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
        ['reset', None, usage.Options,
            'Reset the application database (this means all the data should '
            'be deleted. Use with caution)']

    ]

    def opt_version(self):
        """Print version information and exist
        """
        print('Mamba Sql Tools v{}'.format(__version__))
        print('{}'.format(copyright.copyright))
        self['version'] = 1


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
        else:
            if not self.options.subOptions.opts['version']:
                print(self.options)

    def _handle_configure_command(self):
        """Take care of SQL configuration to generate config/database.json file
        """


