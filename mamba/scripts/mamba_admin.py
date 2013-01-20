# -*- test-case-name: mamba.scripts.test.test_mamba_admin -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

from __future__ import print_function

import sys
import glob
import signal
import subprocess

from twisted import copyright
from twisted.python import usage, filepath

from mamba import version, license
from mamba import copyright as mamba_copyright
from mamba.utils.output import darkgreen, darkred
from _project import ApplicationOptions, Application


class StartOptions(usage.Options):
    """Start command options for mamba-admin tool
    """
    synopsis = '[options]'

    optParameters = [
        ['port', 'p', '', 'override already mamba configured port']
    ]


class Options(usage.Options):
    """Base options for mamba-admin tool
    """
    synopsis = 'Usage: mamba-admin [options]'

    subCommands = [
        ['application', None, ApplicationOptions, 'Generate new application'],
        ['database', None, None, 'Manipulate database'],
        ['controller', None, None, 'Generate new controller'],
        ['model', None, None, 'Generate new model'],
        ['view', None, None, 'Generate new view'],
        ['entity', None, None, 'Generate a new entity'],
        ['test', None, None,
            'Test the mamba application (not the framework).'
            'To test the framework itself you can use the --test option'],
        ['start', None, StartOptions,
            'Start a mamba application (you should be in the app directory)'],
        ['stop', None, usage.Options,
            'Stop a mamba application (you should be in the app directory)']
    ]

    optFlags = [
        ['version', 'V', 'Print version information and exit'],
        ['disclaimer', None, 'Display disclaimer details and exit'],
        ['license', None, 'Print LICENSE information and exit']
    ]

    def __init__(self):
        super(Options, self).__init__()

    def opt_version(self):
        """Print version information and exit
        """
        print('Mamba Framework v{}').format(version.short())
        print('Twisted version: {}').format(copyright.version)
        print(mamba_copyright.copyright)

    def opt_disclaimer(self):
        """Display disclaimer details and exit
        """
        print(mamba_copyright.disclaimer)

    def opt_license(self):
        """Print LICENSE information and exit
        """
        print(license.__LICENSE__)

    def postOptions(self):
        """Post options processing
        """
        if len(sys.argv) == 1:
            print(self)


def run():

    try:
        options = Options()
        options.parseOptions()
    except usage.UsageError, errortext:
        print('{}: {}'.format(sys.argv[0], errortext))
        sys.exit(1)

    if options.subCommand == 'application':
        Application(
            options.subOptions.opts['name'],
            options.subOptions.opts['description'],
            options.subOptions.opts['app-version'],
            options.subOptions.opts['file'],
            options.subOptions.opts['port'],
            True if options.subOptions.opts['noquestions'] == 1 else False
        )

    if options.subCommand == 'start':
        args = ['twistd']
        try:
            app_name = glob.glob(
                'twisted/plugins/*.py')[0].split('/')[-1].split('_')[0]
        except IndexError:
            print(
                'error: twisted directory can\'t be found. You should be in '
                'the application directory in order to start it'
            )
            sys.exit(-1)

        if filepath.exists('twistd.pid'):
            print(
                'error: twistd.pid found, seems like the application is '
                'running already. If the application is not running, please '
                'delete twistd.pid and try again'
            )
            sys.exit(-1)

        args.append(app_name)

        if options.subOptions.opts['port']:
            args.append('--port={}'.format(options.subOptions.opts['port']))

        print('starting application {}...'.format(app_name).ljust(73), end='')
        if subprocess.call(args) == 0:
            print('[{}]'.format(darkgreen('Ok')))
            sys.exit(0)
        else:
            print('[{}]'.format(darkred('Fail')))
            sys.exit(-1)

    if options.subCommand == 'stop':
        twisted_pid = filepath.FilePath('twistd.pid')
        if not twisted_pid.exists():
            print(
                'error: twistd.pid file can\'t be found. You should be in the '
                'application directory in order to stop it'
            )
            sys.exit(-1)

        pid = twisted_pid.open().read()
        print('killing process id {} with SIGINT signal'.format(
            pid).ljust(73), end='')
        try:
            filepath.os.kill(int(pid), signal.SIGINT)
            print('[{}]'.format(darkgreen('Ok')))
        except:
            print('[{}]'.format(darkred('Fail')))
            raise


if __name__ == '__main__':
    run()
