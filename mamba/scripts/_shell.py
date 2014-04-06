# Copyright (c) 2013 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details
import os
import sys

from mamba._version import versions

# This is an auto-generated property, Do not edit it.
version = versions.Version('shell', 0, 0, 0)


def mysql(uri):
    """Runs a MySQL shell.

    :param uri: An `storm.URI` object.
    """
    executable = 'mysql'
    args = [executable]

    if uri.host:
        args.append('--host={}'.format(uri.host))

    if uri.port:
        args.append('--port={}'.format(uri.port))

    if uri.username:
        args.append('--user={}'.format(uri.username))

    if uri.password:
        args.append('--password={}'.format(uri.password))

    if uri.database:
        args.append('{}'.format(uri.database))

    _run(args)


def postgres(uri):
    """Runs a PostgreSQL shell.

    :param uri: An `storm.URI` object.
    """
    executable = 'psql'
    args = [executable]

    if uri.username:
        args.extend(['--username', uri.username])

    if uri.host:
        args.extend(['--host', uri.host])

    if uri.port:
        args.extend(['--port', uri.port])

    if uri.database:
        args.extend(['--dbname', uri.database])

    _run(args)


def sqlite(uri):
    """Runs a SQLite shell.

    :param uri: An `storm.URI` object.
    """
    executable = 'sqlite'

    args = [executable, uri.database]
    _run(args)


def _run(args):
    if os.name != 'nt':
        os.execvp(args[0], args[1:])
    else:
        sys.exit(os.system(' '. join(args)))
