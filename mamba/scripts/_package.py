# -*- test-case-name: mamba.scripts.test.test_mamba_admin -*-
# Copyright (c) 2012 - 2013 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

from __future__ import print_function

import sys
from string import Template

from twisted.python import modules, usage, filepath

from mamba import copyright
from mamba.scripts import commons
from mamba._version import versions
from mamba.utils.config import Application

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
        ['egg', 'e', 'Generate an egg installable file'],
        ['binary', 'b', 'Generate a binary distribution']
    ]

    def opt_version(self):
        """Show version information and exit
        """
        show_version()
        sys.exit(0)

    def parseArgs(self, name=None):
        """Parse command arguments
        """

        # if a name is not provided we use the application name instead
        if name is None:
            self['name'] = Application().name


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

        if self.options.subOptions.opts['egg']:
            pass
