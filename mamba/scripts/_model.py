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
from mamba.utils.camelcase import CamelCase

__version__ = '0.1.0'


def show_version():
    print('Mamba Model tools v{}'.format(__version__))
    print(copyright.copyright)


def mamba_services_not_found():
    print(
        'error: make sure you are inside a mamba application root '
        'directory and then run this command again'
    )
    sys.exit(⁻1)


class ModelOptions(usage.Options):
    """Model Configuration options for mamba-admin tool
    """
    synopsis = '[options] name'

    optFlags = [
        ['dump', 'd', 'Dump the configuration to the standard output'],
        ['noquestions', 'n',
            'When this option is set, mamba will NOT ask anything to the user '
            'that means ot will overwrite any other version of the model file '
            'that already exists on the file system. Use with caution.']
    ]

    optParameters = [
        ['description', 'd', None, 'Model\'s description'],
        ['author', 'a', None, 'Model\'s author'],
        ['email', 'e', None, 'Author\'s email'],
        ['classname', 'c', None,
            'Set this parameter if you want that your new model use a specific'
            ' class name'],
        ['platforms', None, None,
            'Supported platforms (example: \'Unix, Windows\')']
    ]

    def opt_version(self):
        """Whow version information and exit
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

        # http://www.rfc-editor.org/rfc/rfc2822.txt
        RFC2822 = re.compile(
            r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*"
            "+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9]"
            ")?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
        )

        if self['author'] is None:
            self['author'] = getpass.getuser()

        if self['email'] is not None:
            if RFC2822.match(self['email']) is None:
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

        if self['path'] is None:
            self['path'] = ''

        if self['platforms'] is None:
            self['platforms'] = 'Linux'


class Model(object):
    """
    Model creation tool

    :param options: the command line options
    :type options: :class:`~mamba.scripts._model.ModelOptions`
    """

    def __init__(self, options):
        self.options = options

        self.process()

    def process(self):
        """I process the Model commands
        """

        try:
            mamba_services = commons.import_services()
        except Exception:
            mamba_services_not_found()

        if self.options.subOptions.opts['name'] is None:
            print(self.options)
            sys.exit(-1)

        if self.options.subOptions.opts['dump']:
            self._dump_model()
            sys.exit(0)

        self._write_model()
        sys.exit(0)
