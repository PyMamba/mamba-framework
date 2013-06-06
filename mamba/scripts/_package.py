# -*- test-case-name: mamba.scripts.test.test_mamba_admin -*-
# Copyright (c) 2012 - 2013 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

from __future__ import print_function

import os
import re
import sys
import json
import zipfile
import tarfile
import getpass
import subprocess
from string import Template
try:
    import pip
    assert pip
    PIP_IS_AVAILABLE = True
except ImportError:
    PIP_IS_AVAILABLE = False


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
    raise usage.UsageError(
        'error: make sure you are inside a mamba application root directory '
        'and then run this command again'
    )


class PackageInstallOptions(usage.Options):
    """Package Install configuration options for mamba-admin tool
    """
    synopsis = '[options] <optional_file_path/name> '

    optFlags = [
        ['user', 'u', 'Install Package into the user directory'],
        ['global', 'g', 'Install Package into the global directory']
    ]

    optParameters = [
        ['entry_points', None, None,
            'A Json structured string as valid setuptools entry_points '
            'configuration (if you don\'t know what this mean, is quite '
            'possible that you don\'t need this)', str],
        ['extra_directories', None, None,
            'Extra directories to been added to the package. This must be '
            'provided as a valid Json list string', str],
        ['author', None, None, 'Controller\'s author'],
        ['email', None, None, 'Author\'s email'],
        ['license', None, 'GPL', 'Application License', str],
        ['license_classifier', None,
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)']
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

        if self['entry_points'] is not None:
            try:
                self['entry_points'] = json.loads(self['entry_points'])
            except ValueError:
                raise usage.UsageError(
                    'invalid JSON entry_points structure')

            if type(self['entry_points']) is not dict:
                raise usage.UsageError(
                    'the entry_points JSON string must be decoded as a dict')
        else:
            self['entry_points'] = {}

        if self['extra_directories'] is not None:
            try:
                self['extra_directories'] = json.loads(
                    self['extra_directories'])
            except ValueError:
                raise usage.UsageError(
                    'invalid JSON extra_directories structure')

            if type(self['extra_directories']) is not list:
                raise usage.UsageError(
                    'the extra_directories JSON string '
                    'must be decoded as a list'
                )
        else:
            self['extra_directories'] = []

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

    def parseArgs(self, path=None):
        """Parse command arguments
        """

        if path is None:
            try:
                mamba_services = commons.import_services()
                assert mamba_services
                self['filepath'] = None
                # if a name is not provided we use the application name instead
                self['name'] = 'mamba-{}'.format(
                    mamba_services.config.Application(
                        'config/application.json').name.lower()
                )
            except Exception:
                mamba_services_not_found()
        else:
            fp = filepath.FilePath(path)
            if fp.exists():
                self['filepath'] = fp
            else:
                print('{} does not exists... using it as name'.format(path))
                # if a name is not provided we use the application name instead
                self['name'] = path


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
        ['egg', 'e', 'Generate an installable egg file'],
        ['cfgdir', 'c', 'Add the config directory to the package']
    ]

    optParameters = [
        ['entry_points', None, None,
            'A Json structured string as valid setuptools entry_points '
            'configuration (if you don\'t know what this mean, is quite '
            'possible that you don\'t need this)', str],
        ['extra_directories', None, None,
            'Extra directories to been added to the package. This must be '
            'provided as a valid Json list string', str],
        ['author', None, None, 'Controller\'s author'],
        ['email', None, None, 'Author\'s email'],
        ['license', None, 'GPL', 'Application License', str],
        ['license_classifier', None,
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)']
    ]

    def opt_version(self):
        """Show version information and exit
        """
        show_version()
        sys.exit(0)

    def postOptions(self):
        """Post options processing
        """

        if self['entry_points'] is not None:
            try:
                self['entry_points'] = json.loads(self['entry_points'])
            except ValueError:
                raise usage.UsageError(
                    'invalid JSON entry_points structure')

            if type(self['entry_points']) is not dict:
                raise usage.UsageError(
                    'the entry_points JSON string must be decoded as a dict')
        else:
            self['entry_points'] = {}

        if self['extra_directories'] is not None:
            try:
                self['extra_directories'] = json.loads(
                    self['extra_directories'])
            except ValueError:
                raise usage.UsageError(
                    'invalid JSON extra_directories structure')

            if type(self['extra_directories']) is not list:
                raise usage.UsageError(
                    'the extra_directories JSON string '
                    'must be decoded as a list'
                )
        else:
            self['extra_directories'] = []

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

    def parseArgs(self, name=None):
        """Parse command arguments
        """

        try:
            mamba_services = commons.import_services()
        except Exception:
            mamba_services_not_found()

        # if a name is not provided we use the application name instead
        if name is None:
            self['name'] = 'mamba-{}'.format(
                mamba_services.config.Application(
                    'config/application.json').name.lower()
            )


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
        self.entry_points = '{}'
        self.options = options
        self.process()

    def process(self):
        """I process the Package commands
        """

        if self.options.subCommand == 'pack':
            self._handle_pack_command()
        elif self.options.subCommand == 'install':
            self._handle_install_command()
        elif self.options.subCommand == 'uninstall':
            self._handle_uninstall_command()
        else:
            print(self.options)

    def _handle_pack_command(self):
        """Pack the current mamba application
        """

        try:
            mamba_services = commons.import_services()
            mamba_services.config.Application('config/application.json')
        except Exception:
            mamba_services_not_found()

        use_egg = self.options.subOptions.opts['egg']
        command = 'bdist_egg' if use_egg else 'sdist'

        try:
            print('Packing {} application into {} format...'.format(
                mamba_services.config.Application().name,
                'egg' if use_egg else 'source'
            ).ljust(73), end='')
            Packer().pack_application(
                command,
                self.options.subOptions,
                mamba_services.config.Application()
            )
            print('[{}]'.format(darkgreen('Ok')))
        except:
            print('[{}]'.format(darkred('Fail')))
            raise
            sys.exit(-1)

    def _handle_install_command(self):
        """Install the current mamba application or a packed one
        """

        if self.options.subOptions.opts['filepath'] is None:
            try:
                mamba_services = commons.import_services()
            except Exception:
                mamba_services_not_found()

            self._handle_install_current_directory(mamba_services)
        else:
            self._handle_install_already_packed_application(
                self.options.subOptions.opts['filepath']
            )

    def _handle_install_current_directory(self, mamba_services):
        """Handles the installation of the current directory
        """

        packer = Packer()
        config = mamba_services.config.Application('config/application.json')

        print('Installing {} application in {} store...'.format(
            mamba_services.config.Application().name,
            'global' if self.options.subOptions['global'] else 'user'
        ).ljust(73), end='')

        try:
            packer.create_package_directory(
                config.name, self.options.subOptions, config)
            packer.install_package_directory(self.options.subOptions)
            print('[{}]'.format(darkgreen('Ok')))
        except:
            print('[{}]'.format(darkred('Fail')))
            raise

    def _handle_install_already_packed_application(self, path):
        """Handles the installation of the given installable mamba app
        """

        packer = Packer()
        if not packer.is_mamba_package(path):
            raise usage.UsageError(
                '{} is not a valid mamba package file'.format(path)
            )

        print('Installing {} application in {} store...'.format(
            path.basename(),
            'global' if not self.options.subOptions['global'] else 'user'
        ).ljust(73), end='')
        try:
            packer.install_package_file(path, self.options.subOptions)
            print('[{}]'.format(darkgreen('Ok')))
        except:
            print('[{}]'.format(darkred('Fail')))
            raise

    def _handle_uninstall_command(self):
        """Uninstall a package using pip (we don't want to reinvent the wheel)
        """

        if not PIP_IS_AVAILABLE:
            raise usage.UsageError('pip is not available')

        try:
            mamba_services = commons.import_services()
            mamba_services.config.Application('config/application.json')
        except Exception:
            mamba_services_not_found()

        print('Uninstalling {}...'.format(
            mamba_services.config.Application().name).ljust(73), end='')
        try:
            p = subprocess.Popen(
                ['pip', 'uninstall', mamba_services.config.Application().name],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                stdin=subprocess.PIPE
            )
            stdout, error = p.communicate('y')
            if error is not '':
                raise RuntimeError(error)
            elif p.returncode is not 0:
                raise RuntimeError(stdout)
            else:
                print('[{}]'.format(darkgreen('Ok')))
        except:
            print('[{}]'.format(darkred('Fail')))
            raise


class Packer(object):
    """Perform automated tasks in order to pack and installs Mamba projects
    """

    def do(self, args, out=subprocess.PIPE):
        """Do a task
        """

        return subprocess.call(args, stdout=out, stderr=out)

    def is_mamba_package(self, path):
        """Determine if the given path is a valid mamba package file
        """

        if path.basename().endswith('.egg'):
            zf = zipfile.ZipFile(path.path)
            for name in zf.namelist():
                if '.mamba-package' in name:
                    return True
        else:
            tf = tarfile.open(path.path)
            for name in tf.getnames():
                if '.mamba-package' in name:
                    return True

        return False

    def install_package_file(self, path, options):
        """Installs a package file given by path
        """

        args = ['install']
        if options['user']:
            args.append('--user')
        args.append(path.path)

        if path.basename().endswith('.egg'):
            # this is an egg file, pip can't install egg files
            # we try to import easy_install main func and use it in order
            # to install the package, if easy_install is not present we fail
            try:
                from setuptools.command.easy_install import main
                assert main
            except ImportError:
                raise RuntimeError('easy_install is not present on system')

            p = subprocess.Poepn(
                args[1:], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            output, error = p.communicate()
            if error is not '':
                raise RuntimeError(error)
        else:
            if PIP_IS_AVAILABLE:
                args.insert(0, 'pip')
                p = subprocess.Popen(
                    args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                output, error = p.communicate()
                if error is not '':
                    raise RuntimeError(error)
            else:
                args.insert(0, 'setup.py')
                args.insert(0, sys.executable)
                p = subprocess.Popen(
                    args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                output, error = p.communicate()
                if error is not '':
                    raise RuntimeError(error)

    def install_package_directory(self, options):
        """Installs a package directory in the given location
        """

        args = [sys.executable, 'setup.py', 'install']
        if options['user']:
            args.append('--user')

        os.chdir('package')
        p = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        output, error = p.communicate()

        os.chdir('..')
        self.do(['rm', '-Rf', 'package'])

        if error is not '':
            raise RuntimeError(error)

    def create_package_directory(self, name, options, config):
        """Create the package directory layout
        """

        # check if README.rst and LICENSE files are present
        if not filepath.exists('README.rst') or not filepath.exists('LICENSE'):
            raise usage.UsageError(
                'You must create a README.rst and LICENSE files if you want '
                'to pack/install this application.')

        # check if docs directory exists
        if not filepath.exists('docs'):
            raise usage.UsageError(
                'You have to add a *docs* directory to your package')

        # check if MANIFEST.in exits and copy it if does
        if filepath.exists('MANIFEST.in'):
            self.do(['cp', 'MANIFEST.in', 'package/'])

        # clean the application
        self.do(['find', '.', '-type', 'f', '-name', '"*.py[co]"', "-delete"])

        # create layout
        self.do(['mkdir', 'package'])
        self.do(['cp', '-Rf', 'docs', 'package/'])
        self.do(['cp', '-Rf', 'static', 'package/'])
        self.do(['cp', 'README.rst', 'LICENSE', 'package/'])
        self.do(['cp', '-Rf', 'application', 'package/' + name])

        if len(options['extra_directories']) != 0:
            for directory in options['extra_directories']:
                self.do(['cp', '-Rf', directory, 'package/'])

        self.do(['touch', 'package/.mamba-package'])
        os.chdir('package')
        self.write_setup_script(name, options, config)
        self.fix_application_path(name)
        self.write_manifest(name, options, config)
        os.chdir('..')

    def pack_application(self, command, options, config):
        """Prepare the package directory
        """

        name = config.name.lower()
        self.create_package_directory(name, options, config)

        os.chdir('package')
        self.do([sys.executable, 'setup.py', command, '-d', '../'])
        self.do([sys.executable, 'setup.py', 'clean'])
        os.chdir('..')
        # self.do(['rm', '-Rf', 'package'])

    def fix_application_path(self, name):
        """Fix the application path renaming `application` to `name`
        """

        command = (
            'find -type f -name "*.py" -print0 | xargs -0 sed -i '
            '"s/from application/from {}/"'.format(name)
        )
        subprocess.call(command, shell=True)

    def write_manifest(self, name, options, config):
        """Write the MANIFEST.in file
        """

        with open('MANIFEST.in', 'a+') as manifest:
            manifest.write('include .mamba-package\n')
            manifest.write('recursive-include static *\n')
            manifest.write('recursive-include {}/view *\n'.format(name))

            for directory in options['extra_directories']:
                manifest.write('recursive-include {} *\n'.format(directory))

    def write_setup_script(self, name, options, config):
        """Write the setup.py script
        """

        with open('setup.py', 'w') as setup_script:
            setup_script_template = self._load_template_from_mamba('setup')
            args = {
                'application': name,
                'description': config.description,
                'author': options['author'],
                'author_email': options['email'],
                'entry_points': options['entry_points'],
                'version': config.version,
                'application_name': options['name'],
                'license': options['license'],
                'license_classifier': options['license_classifier']
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
            )).open('r').read()
        )
