# -*- test-case-name: mamba.scripts.test.test_mamba_admin -*-
# Copyright (c) 2012 - 2013 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

from __future__ import print_function

import sys
import getpass
from string import Template

from twisted.python import usage, filepath

from mamba import copyright
from mamba.scripts import commons
from mamba._version import versions
from mamba.utils.output import darkred, darkgreen

# This is an auto-generated property, Do not edit it.
version = versions.Version('package', 0, 0, 0)


def show_version():
    print('Mamba Package tools v{}'.format(version.short()))
    print(copyright.copyright)


def mamba_services_not_found():
    print(
        'error: make sure you are inside a mamba application root directory '
        'and then run this command again'
    )
    sys.exit(-1)


class PackageInstallOptions(usage.Options):
    """Package Install configuration options for mamba-admin tool
    """
    synopsis = '[options]'

    optFlags = [
        ['user', 'u', 'Install Package into the user directory'],
        ['global', 'g', 'Instakll Package into the global directory']
    ]

    def opt_version(self):
        """Show version information and exit
        """
        show_version()
        sys.exit(0)

    def postOptions(self):
        """Post options processing
        """
        if ((self['user'] and self['global'])
                or (not self['user'] and not self['global'])):
            raise usage.UsageError(
                'you must choose between `user` and `global` installations'
            )


class PackageUninstallOptions(usage.Options):
    """Package Uninstall configuration options for mamba-admin tool
    """
    synopsis = ''

    def opt_version(self):
        """Show version information and exit
        """
        show_version()
        sys.exit(0)


class PackagePackOptions(usage.Options):
    """Package pack configuration options for mamba-admin tool
    """
    synopsis = '[options] <optional_name>'

    optFlags = [
        ['egg', 'e', 'Generate an egg installable file']
    ]

    def opt_version(self):
        """Show version information and exit
        """
        show_version()
        sys.exit(0)

    def parseArgs(self, name=None):
        """Parse command arguments
        """

        try:
            mamba_services = commons.import_services()
        except Exception:
            mamba_services_not_found()

        # if a name is not provided we use the application name instead
        if name is None:
            self['name'] = mamba_services.config.Application().name


class PackageOptions(usage.Options):
    """Package options for mamba-admin tool
    """
    synopsis = '[options] command'

    optFlags = [
        ['version', 'V', 'display version information and exit']
    ]

    subCommands = [
        ['pack', None, PackagePackOptions, 'Pack the current application'],
        ['install', None, PackageInstallOptions,
            'Install a packed mamba application or the actual application'],
        ['uninstall', None, PackageUninstallOptions,
            'Uninstall an already installed mamba application']
    ]

    def opt_version(self):
        """Print version information and exit
        """
        show_version()
        sys.exit(0)


class Package(object):
    """
    Package configuration and tools

    :param options: the command line options
    :type options: :class:`~mamba.scripts._package.PackageOptions`
    """

    def __init__(self, options):
        self.options = options
        self.process()
        self.entry_points = '{}'

    def process(self):
        """I process the Package commands
        """

        if self.options.subCommand == 'pack':
            self._handle_pack_command()
        elif self.options.subCommand == 'install':
            self._handle_install_command()
        elif self._options.subCommand == 'uninstall':
            self._handle_uninstall_command()
        else:
            print(self.options)

    def _handle_pack_command(self):
        """Pack the current mamba application
        """

        try:
            mamba_services = commons.import_services()
        except Exception:
            mamba_services_not_found()

        use_egg = self.options.subOptions.opts['egg']
        command = 'bdist_egg' if use_egg else 'sdist'

        try:
            print('Packing {} application into {} format...'.format(
                mamba_services.config.Application().name,
                'egg' if use_egg else 'source'
            ).ljust(73), end='')
            self._pack(command, mamba_services.config.Application())
            print('[{}]'.format(darkgreen('Ok')))
        except:
            print('[{}]'.format(darkred('Fail')))
            raise
            sys.exit(-1)

    def _pack(self, command, config):
        """
        Really pack the application using setuptools. It generates a temp
        setup.py file and use the Application configuration details in order
        to fill it

        :param command: the command to use on packing, can be sdist or egg
        :param config: the Application configuration
        """

        with open('setup.py', 'w') as setup_script:
            setup_script_template = self._load_template_from_mamba('setup')
            args = {
                'application': self['name'],
                'description': config.description,
                'author': getpass.getuser(),
                'author_email': '{}@localhost'.format(getpass.getuser()),
                'application_name': config.name,
                'entry_points': self['entry_points']
            }
            setup_script.write(setup_script_template.safe_substitute(**args))

    def _load_template_from_mamba(self, template):
        """
        Load a template from the installed mamba directory

        :param template: the template name
        :type template: str
        """

        # windows need '\\' as path separator
        sep = filepath.os.sep
        return Template(
            filepath.FilePath('{}/templates/{}'.format(
                '/'.join(filepath.dirname(__file__).split(sep)[:-1]),
                template if template.endswith('.tpl') else '{}.tpl'.format(
                    template
                )
            )).open('rb' if template.endswith('.ico') else 'r').read()
        )
