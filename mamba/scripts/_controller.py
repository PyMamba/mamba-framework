# -*- test-case-name: mamba.scripts.test.test_mamba_admin -*-
# Copyright (c) 2012 - 2013 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

from __future__ import print_function

import re
import sys
import getpass
import datetime
from string import Template

from twisted.python import usage, filepath

from mamba import copyright
from mamba.scripts import commons
from mamba._version import versions
from mamba.utils.checkers import Checkers
from mamba.utils.camelcase import CamelCase

# This is an auto-generated property. Do not edit it.
version = versions.Version('controller', 0, 1, 8)


def show_version():
    print('Mamba Controller Tools v{}'.format(version.short()))
    print(format(copyright.copyright))


def mamba_services_not_found():
    print(
        'error: make sure you are inside a mamba application root '
        'directory and then run this command again'
    )
    sys.exit(-1)


class ControllerOptions(usage.Options):
    """Controller Configuration options for mamba-admin tool
    """
    synopsis = '[options] name'

    optFlags = [
        ['dump', 'd', 'Dump to the standard output'],
        ['noquestions', 'n',
            'When this option is set, mamba will NOT ask anything to the user '
            'that means it will overwrite any other version of the controller '
            'file that already exists in the file system. Use with caution']
    ]

    optParameters = [
        ['description', None, None, 'Controller\'s description'],
        ['author', None, None, 'Controller\'s author'],
        ['email', None, None, 'Author\'s email'],
        ['route', None, None, 'Controller\'s register route (if any)'],
        ['classname', None, None,
            'Set this parameter if you want that your new controller use a '
            'specific class name'],
        ['platforms', None, None,
            'Supported platforms (example: \'Unix, Windows\')']
    ]

    def opt_version(self):
        """Show version information and exit
        """
        show_version()
        sys.exit(0)

    def parseArgs(self, name=None):
        """Parse command arguments
        """

        if name is None:
            self['name'] = name
            return

        regex = re.compile(r'[\W]')
        name = regex.sub('', name)

        self['filename'] = name.lower()
        self['name'] = CamelCase(name.replace('_', ' ')).camelize(True)

    def postOptions(self):
        """Post options processing
        """

        if self['author'] is None:
            self['author'] = getpass.getuser()

        if self['email'] is not None:
            if not Checkers.check_email(self['email']):
                print(
                    'error: the given email address {} is not a valid RFC2822 '
                    'email address, '
                    'check http://www.rfc-editor.org/rfc/rfc2822.txt for '
                    'very extended details'.format(self['email'])
                )
                sys.exit(-1)
        else:
            # just set an invalid RFC2822 email address (thats what irony mean)
            self['email'] = '{}@localhost'.format(self['author'])

        if self['route'] is None:
            self['route'] = ''

        if self['platforms'] is None:
            self['platforms'] = 'Linux'


class Controller(object):
    """
    Controller creation tool

    :param options: the command line options
    :type options: :class:`~mamba.scripts._controller.ControllerOptions`
    """

    def __init__(self, options):
        self.options = options

        self.process()

    def process(self):
        """I process the Controller commands
        """

        try:
            mamba_services = commons.import_services()
            del mamba_services
        except Exception:
            mamba_services_not_found()

        if self.options.subOptions.opts['name'] is None:
            print(self.options.subOptions)
            sys.exit(-1)

        if self.options.subOptions.opts['dump']:
            self._dump_controller()
            sys.exit(0)

        self._write_controller()
        sys.exit(0)

    def _dump_controller(self):
        """Dump the controller to the standard output
        """

        print('\n')
        print(self._process_template())

    @commons.decorate_output
    def _write_controller(self):
        """Write the controller to a file in the file system
        """

        controller_file = filepath.FilePath(
            'application/controller/{}.py'.format(
                self.options.subOptions.opts['filename'])
        )

        if controller_file.exists():
            if commons.Interaction.userquery(
                '{} file already exists in the file system.'
                'Are you really sure do you want to overwrite it?'.format(
                    controller_file.path
                )
            ) == 'No':
                return

        print('Writing the controller...'.ljust(73), end='')
        controller_file.open('w').write(self._process_template())

    def _process_template(self):
        """Prepare the template to write/dump
        """

        sep = filepath.os.sep  # windows needs '\\' as separator
        controller_template = Template(
            filepath.FilePath('{}/templates/controller.tpl'.format(
                '/'.join(filepath.dirname(__file__).split(sep)[:-1])
            )).open('r').read()
        )

        if self.options.subOptions.opts['classname'] is None:
            classname = self.options.subOptions.opts['name']
        else:
            classname = self.options.subOptions.opts['classname']

        args = {
            'year': datetime.datetime.now().year,
            'controller_name': self.options.subOptions.opts['name'],
            'platforms': self.options.subOptions.opts['platforms'],
            'synopsis': self.options.subOptions.opts['description'],
            'author': self.options.subOptions.opts['author'],
            'author_email': self.options.subOptions.opts['email'],
            'synopsis': self.options.subOptions.opts['description'],
            'controller_class': classname,
            'register_path': self.options.subOptions.opts['route']
        }

        return controller_template.safe_substitute(**args)
