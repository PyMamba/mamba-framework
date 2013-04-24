# -*- test-case-name: mamba.test.test_deployer -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: deployer
    :platform: Linux
    :synopsis: Deployment pluggable system for Mamba.

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

import sys
import imp
import errno
import marshal

from twisted.python import filepath

from mamba import plugin


class DeployerError(Exception):
    """Fired when some problem arises
    """


class DeployerProvider:
    """Mount point for plugins which refer to Deployers for our applications.
    """

    __metaclass__ = plugin.ExtensionPoint


def deployer_import(name, path):
    """Import a deployer configuration file as Python code and initializes it
    """

    fpath = filepath.FilePath(path)
    importer = DeployerImporter(fpath)

    module = sys.modules.get(name)
    is_reload = True if module is not None else False

    if not is_reload:
        module = imp.new_module(name)
        sys.modules[name] = module
    else:
        original_values = {}
        modified_attrs = ['__loader', '__name__', '__file__']
        for attr in modified_attrs:
            try:
                original_values[attr] = getattr(module, attr)
            except AttributeError:
                pass  # ignore, huh?

    module.__loader__ = DeployerImporter
    module.__name__ = name
    module.__file__ = path

    try:
        exec importer.code_object in module.__dict__
    except Exception:
        del sys.modules[name]
        raise  # propagate

    return module


class DeployerImporter(object):
    """Imports DeployerConfig files in a very similar way as __import__ does
    """

    def __init__(self, filename):
        super(DeployerImporter, self).__init__()
        self.sourcefile = filename
        self.bytefile = filepath.FilePath(filename.path.replace('.dc', '.dco'))
        self.code_object = self._handle_file()

    def _handle_file(self):
        """Load and compile the config source code from the given filename
        """

        source_timestamp = None
        # use bytecode if available
        if self._bytecode_is_available():
            magic, timestamp, bytecode = self._get_bytecode()
            try:
                if imp.get_magic() != magic:
                    raise DeployerError('bad magic number for obj config file')

                source_timestamp = self._get_timestamp()
                if timestamp < source_timestamp:
                    return self._compile_source_file(source_timestamp)

                try:
                    # use marshal to read the binary data
                    return marshal.loads(bytecode)
                except ValueError:
                    # bytecode is not good, just fallback to source code
                    pass
            except DeployerError:
                raise  # propagate

        # use the source
        return self._compile_source_file(source_timestamp)

    def _compile_source_file(self, source_timestamp):
        """Compiles a source config file into bytecode

        :param source_timestamp: the compilation timestamp
        """

        code = compile(self._get_source(), self.sourcefile.path, 'exec')
        if source_timestamp is None:
            source_timestamp = self._get_timestamp()

        # use marshal to write the binary data
        data = marshal.dumps(code)
        self._write_bytecode(source_timestamp, data)

        return code

    def _get_bytecode(self):
        """Return magic number, timestamp and bytecode from DC file
        """

        try:
            with self.bytefile.open('rb') as bytecode_file:
                data = bytecode_file.read()
            return data[:4], _lt_to_int(data[4:8]), data[8:]
        except AttributeError:
            return None

    def _write_bytecode(self, timestamp, data):
        """Write out 'data' using timestamp

        :param timestamp: the timestamp to use
        :param data: the data (in bytes) to write
        :raises: IOError
        """

        try:
            with self.bytefile.open('wb') as bytecode_file:
                bytecode_file.write(imp.get_magic())
                bytecode_file.write(_int_to_lt(timestamp))
                bytecode_file.write(data)
                return True
        except IOError as err:
            if err.errno == errno.EACCES:
                return False
            else:
                raise  # propagate

    def _get_source(self):
        """Return the source from the config file
        """

        return self.sourcefile.open('U').read()

    def _get_timestamp(self):
        """Return the timestamp of the last file modification
        """

        return int(self.sourcefile.getModificationTime())

    def _bytecode_is_available(self):
        """Returns true if bytecode file is available
        """

        return self.bytefile.exists()


def _lt_to_int(int_bytes):
    """Convert bytes in little-endian to integer
    """

    integer = 0
    for i in range(len(int_bytes)):
        if i == 0:
            integer = ord(int_bytes[i])
        else:
            integer |= ord(int_bytes[i]) << (8 * i)

    return integer


def _int_to_lt(integer):
    """Convert an integer to bytes in little-endian
    """

    integer = int(integer)
    int_bytes = list()
    for i in range(4):  # 4 bytes in a 32 bits integer
        if i == 0:
            int_bytes.append(integer & 0xff)
        else:
            int_bytes.append(integer >> (8 * i) & 0xff)

    return ''.join(chr(x) for x in int_bytes)


__all__ = ['DeployerError', 'DeployerProvider']
