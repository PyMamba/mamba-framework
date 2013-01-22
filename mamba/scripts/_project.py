# -*- test-case-name: mamba.scripts.test.test_mamba_admin -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

from __future__ import print_function

import sys
import getpass
import functools
from string import Template

from twisted.python import usage, filepath

from mamba import copyright
from commons import Interaction
from mamba.utils.output import (
    blue, brown, darkred, darkgreen, resetColor as reset
)

__version__ = '0.1.0'


class ApplicationOptions(usage.Options):
    """Application Options for mamba-admin tool
    """
    synopsis = '[options] <project name>'

    optFlags = [
        ['noquestions', 'n',
            'When this option is set, mamba will NOT ask anything to the user '
            'that means it will delete any previous application with the same '
            'name in the current path and will accept any options that are '
            'passed to it.'
            'Use with caution']
    ]

    optParameters = [
        ['description', 'd', 'A new Mamba application',
            'mamba application description', str],
        ['app-version', 'v', '1.0', 'mamba application version', str],
        ['configfile', 'f', 'application.json',
            'mamba application JSON config file', str],
        ['logfile', 'l', None,
            'log file (mamba already logs to twistd.log file in the root of '
            'the application directory. If you set a value to this parameter, '
            'mamba will log all the activity as daily rotations to that file '
            'as well)'],
        ['port', 'p', 1936, 'mamba application listening port', int]
    ]

    def opt_version(self):
        """Print version information and exist
        """
        print('Mamba Application Configurator v{}'.format(__version__))
        print('{}'.format(copyright.copyright))

    def parseArgs(self, name):
        """Parse command arguments
        """

        self['name'] = name

    def postOptions(self):
        """Post options processing
        """
        if not self['configfile'].endswith('.json'):
            self['configfile'] = '{}.json'.format(self['configfile'])

        if self['logfile'] is not None:
            if not self['logfile'].endswith('.log'):
                self['logfile'] = '{}.log'.format(self['logfile'])


def decorate_output(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            print('[{}]'.format(darkgreen('Ok')))
            return result
        except:
            print('[{}]'.format(darkred('Fail')))
            raise

    return wrapper


class Application(object):
    """
    Application configurator

    :param name: the application name
    :type name: str
    :param description: the application description
    :type description: str
    :param app-version: the application starting version
    :type app-version: float
    :param file: the application tac file
    :type file: str
    :param port: the application port
    :type port: int
    """

    def __init__(self, name, description, version, files, port, noask=False):
        self.name = name
        self.description = description
        self.version = version
        self.file = files[0]
        self.logfile = files[1]
        self.port = port
        self.noask = noask

        self.process()

    def process(self):
        """I process the project generation
        """

        if self.noask is False:
            print(
                'Welcome to the mamba application generator v{}\n'
                'You are going to genearate a new Mamba application on {} '
                'with the following options:\n'.format(
                    __version__,
                    filepath.abspath(filepath.os.getcwd())
                )
            )

            for key, value in self.__dict__.iteritems():
                if not key.startswith('_'):
                    print('{key}: {value}'.format(
                        key=blue(key.ljust(12)),
                        value='{}{}'.format(reset(), str(value)),
                    ))

            if Interaction.userquery(
                    'Would you like to generate this application?') == 'No':
                print('\nQuitting.')
                sys.exit(0)

        return self.generate_application()

    def generate_application(self):
        """Generates the application on the file system
        """

        self.app_dir = self.name.lower().replace(' ', '_')
        # create directory
        self._generate_application_directory()
        # create application directories
        self._generate_application_directories()
        # write page plugin
        self._write_plugin()
        # write factory
        self._write_factory()
        # write config file
        self._write_config()

    @decorate_output
    def _generate_application_directory(self):
        """Generates the application directory in the current path
        """

        try:
            # create project directory
            directory = filepath.FilePath(
                '{}/{}'.format(filepath.os.getcwd(), self.app_dir))
            if directory.exists() and self.noask is False:
                print(
                    'Seems like an application named {} already exists in '
                    'your current path.'.format(directory.basename())
                )

                query = 'Would you like to rename it? (Ctrl+c to abort)'
                if Interaction.userquery(query) == 'Yes':
                    rnd = str(filepath.random.randrange(1, 10000))
                    filepath.os.rename(
                        directory.path, '{}{}'.format(directory.path, rnd)
                    )

                    print('The old dircectory has been saved as {}'.format(
                        brown('{}{}'.format(directory.path, rnd))
                    ))
                else:
                    query = 'The {} directory is going to be {}, Are you sure?'
                    query = query.format(
                        directory.basename(), darkred('deleted')
                    )
                    if Interaction.userquery(query) == 'Yes':
                        print('Deleting {}...'.format(directory.basename()))
                        directory.remove()
                    else:
                        print('Quitting.')
                        sys.exit(0)
            elif directory.exists() and self.noask is True:
                directory.remove()

            print('Creating {} directory...'.format(
                directory.basename()).ljust(73), end=''
            )
            directory.createDirectory()
        except OSError, error:
            print(darkred(error))
            sys.exit(-1)

    def _generate_application_directories(self):
        """Generates the application needed directories
        """

        try:
            self._generate_directory_helper('application/')
            self._generate_directory_helper('application/controller')
            self._generate_directory_helper('application/model')
            self._generate_directory_helper('application/view')
            self._generate_directory_helper('twisted')
            self._generate_directory_helper('twisted/plugins')
            self._generate_directory_helper('static')
            self._generate_directory_helper('config')
        except OSError, error:
            print(darkred(error))
            sys.exit(-1)

    @decorate_output
    def _generate_directory_helper(self, directory):
        """I am a helper function to avoid code repetition
        """

        print('Generating {} directory...'.format(directory).ljust(73), end='')
        fp = filepath.FilePath('{}/{}'.format(self.app_dir, directory))
        fp.createDirectory()

    def _load_template_from_mamba(self, template):
        """
        Load a template from the installed mamba directory

        :param template: the template name
        :type template: str
        """

        return Template(
            filepath.FilePath('{}/templates/{}'.format(
                '/'.join(filepath.dirname(__file__).split('/')[:-1]),
                template if template.endswith('.tpl') else '{}.tpl'.format(
                    template
                )
            )).open().read()
        )

    @decorate_output
    def _write_plugin(self):
        """Write the plugin template to the file system
        """

        print('Writting Twisted plugin...'.ljust(73), end='')
        plugin_file = filepath.FilePath('{}/twisted/plugins/{}'.format(
            self.app_dir, '{}_plugin.py'.format(self.name.lower())
        ))

        plugin_template = self._load_template_from_mamba('plugin')
        args = {
            'application': self.name,
            'file': self.file
        }

        plugin_file.open('w').write(plugin_template.safe_substitute(**args))

    @decorate_output
    def _write_factory(self):
        """Write the factory template to the file system
        """

        print('Writting plugin factory...'.ljust(73), end='')
        factory_file = filepath.FilePath('{}/{}.py'.format(
            self.app_dir, self.name.lower()
        ))

        factory_template = self._load_template_from_mamba('factory')
        args = {
            'application': self.name,
            'platforms': 'Unix, Windows',
            'synopsis': self.description,
            'author': getpass.getuser(),
            'author_email': '{}@localhost'.format(getpass.getuser())
        }

        factory_file.open('w').write(factory_template.safe_substitute(**args))

    @decorate_output
    def _write_config(self):
        """Write config file template to the file system
        """

        print('Writting configuration file...'.ljust(73), end='')
        config_file = filepath.FilePath(
            '{}/config/{}'.format(self.app_dir, self.file))
        config_template = self._load_template_from_mamba('application.json')
        args = {
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'port': self.port,
            'logfile': self.logfile if self.logfile is not None else 'null'
        }

        config_file.open('w').write(config_template.safe_substitute(**args))
