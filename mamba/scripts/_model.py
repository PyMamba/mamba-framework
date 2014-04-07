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
from mamba.utils.camelcase import CamelCase

# This is an auto-generated property. Do not edit it.
version = versions.Version('model', 0, 2, 2)


def show_version():
    print('Mamba Model tools v{}'.format(version.short()))
    print(copyright.copyright)


def mamba_services_not_found():
    print(
        'error: make sure you are inside a mamba application root '
        'directory and then run this command again'
    )
    sys.exit(-1)


class ModelOptions(usage.Options):
    """Model Configuration options for mamba-admin tool
    """
    synopsis = '[options] name table'

    optFlags = [
        ['dump', 'd', 'Dump the configuration to the standard output'],
        ['noschema', 's',
            'Set this if you don\'t want Mamba manaing this at schema-level'],
        ['noquestions', 'n',
            'When this option is set, mamba will NOT ask anything to the user '
            'that means ot will overwrite any other version of the model file '
            'that already exists on the file system. Use with caution.']
    ]

    optParameters = [
        ['description', None, None, 'Model\'s description'],
        ['author', None, None, 'Model\'s author'],
        ['email', None, None, 'Author\'s email'],
        ['classname', None, None,
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

    def parseArgs(self, name=None, table=None):
        """Parse command arguments
        """

        if name is None or table is None:
            self['name'] = None
            self['table'] = None
            return

        regex = re.compile(r'[^._a-zA-Z0-9]')
        name = regex.sub('', name)
        path, name = commons.process_path_name(name)

        self['filename'] = filepath.joinpath(path.lower(), name.lower())
        self['name'] = CamelCase(name.replace('_', ' ')).camelize(True)
        self['model_table'] = table

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
        self.model_properties = 'id = Int(primary=True, unsigned=True)\n'

        self.process()

    def process(self):
        """I process the Model commands
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
            self._dump_model()
            sys.exit(0)

        self._write_model()
        sys.exit(0)

    def _dump_model(self):
        """Dump the model to the standard output
        """

        print('\n')
        print(self._process_template())

    @commons.decorate_output
    def _write_model(self):
        """Write the model to a file in the file system
        """

        model_file = filepath.FilePath(
            'application/model/{}.py'.format(
                self.options.subOptions.opts['filename'])
        )

        if model_file.exists():
            if commons.Interaction.userquery(
                '{} file already exists in the file system.'
                'Are you really sure do you want to overwrite it?.'.format(
                    model_file.path
                )
            ) == 'No':
                return

        print('Writing the model...'.ljust(73), end='')
        try:
            model_file.open('w').write(self._process_template())
        except IOError:
            # package directory doesn't exists yet
            commons.generate_sub_packages(model_file)
            model_file.open('w').write(self._process_template())

    def _process_template(self):
        """Prepare the template to write/dump
        """

        sep = filepath.os.sep  # windows needs '\\' as separator
        model_template = Template(
            filepath.FilePath('{}/templates/model.tpl'.format(
                '/'.join(filepath.dirname(__file__).split(sep)[:-1])
            )).open('r').read()
        )

        if self.options.subOptions.opts['classname'] is None:
            classname = self.options.subOptions.opts['name']
        else:
            classname = self.options.subOptions.opts['classname']

        if self.options.subOptions.opts['noschema'] != 0:
            class_properties = '__mamba_schema__ = False\n'
        else:
            class_properties = ''

        args = {
            'model_table': self.options.subOptions.opts['model_table'],
            'model_properties': self.model_properties,
            'class_properties': class_properties,
            'year': datetime.datetime.now().year,
            'model_name': self.options.subOptions.opts['name'],
            'platforms': self.options.subOptions.opts['platforms'],
            'synopsis': self.options.subOptions.opts['description'],
            'author': self.options.subOptions.opts['author'],
            'author_email': self.options.subOptions.opts['email'],
            'synopsis': self.options.subOptions.opts['description'],
            'model_class': classname,
        }

        return model_template.safe_substitute(**args)
