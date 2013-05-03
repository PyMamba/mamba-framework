# -*- test-case-name: mamba.scripts.test.test_mamba_admin -*-
# Copyright (c) 2012 - 2013 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

from __future__ import print_function

import re
import sys
import datetime
from string import Template

from twisted.python import usage, filepath

from mamba import copyright
from mamba.scripts import commons
from mamba._version import versions
from mamba.utils.camelcase import CamelCase
from mamba.scripts._sql import mamba_services_not_found

# This is an auto-generated property. Do not edit it.
version = versions.Version('view', 0, 1, 0)


def show_version():
    print('Mamba View Tools v{}'.format(version.short()))
    print('{}'.format(copyright.copyright))


class ViewOptions(usage.Options):
    """View  Configuration options for mamba-admin tool
    """
    synopsis = '[options] name <controller>'

    optFlags = [
        ['dump', 'd', 'Dumo to the standard output'],
        ['noquestions', 'n',
            'When this option is set, mamba will NOT ask anything to the user '
            'that means it will overwrite any other version of the view files '
            'that already exists in the file system. Use with caution']
    ]

    optParameters = [
        ['description', None, None, 'View\'s description'],
        ['author', None, None, 'View\'s author'],
        ['email', None, None, 'Author\'s email']
    ]

    def opt_version(self):
        """Show version information and exit
        """
        show_version()
        sys.exit(0)

    def parseArgs(self, name=None, controller=None):
        """Parse command arguments
        """

        self['name'] = name
        self['controller'] = controller

        if self['name'] is not None:
            regex = re.compile(r'[\W]')
            name = regex.sub('', self['name'])

            self['filename'] = name.lower()
            self['name'] = CamelCase(name.replace('_', ' ')).camelize(True)

    def postOptions(self):
        """Post options processing
        """

        commons.post_options(self)


class View(object):
    """
    View creation tool

    :param options: the command line options
    :type options: :class:`~mamba.scripts._view.ViewConfigOptions`
    """

    def __init__(self, options):
        self.options = options

        self.process()

    def process(self):
        """I process the View command
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
            self._dump_view()
            sys.exit(0)

        self._write_view()
        sys.exit(0)

    def _dump_view(self):
        """Dump the view model to the standard output
        """

        print('\n')
        print(self._process_template())

    @commons.decorate_output
    def _write_view(self):
        """Write the view to a file in the file system
        """

        view_path = 'templates/'
        if self.options.subOptions.opts['controller'] is not None:
            controller = self.options.subOptions.opts['controller']
            if filepath.exists(
                    'application/controller/{}.py'.format(controller)):
                view_path = '{}/'.format(controller.capitalize())

        view_file = filepath.FilePath(
            'application/view/{}{}.html'.format(
                view_path, self.options.subOptions.opts['filename'])
        )

        if self.options.subOptions.opts['noquestions'] is False:
            if view_file.exists():
                if commons.Interaction.userquery(
                    '{} file already exists in the file system. '
                    'Are you really sure do you want to overwrite it?'.format(
                        view_file.path
                    )
                ) == 'No':
                    return
        print('Writing the view...'.ljust(73), end='')
        view_file.open('w').write(self._process_template())

    def _process_template(self):
        """Prepare the template to write/dump
        """

        view_template = Template(
            filepath.FilePath('{}/templates/view.tpl'.format(
                '/'.join(filepath.dirname(__file__).split('/')[:-1])
            )).open('r').read()
        )

        args = {
            'year': datetime.datetime.now().year,
            'view_name': self.options.subOptions.opts['name'],
            'synopsis': self.options.subOptions.opts['description'],
            'author': self.options.subOptions.opts['author'],
            'author_email': self.options.subOptions['email']
        }

        return view_template.safe_substitute(**args)
