# -*- test-case-name: mamba.utils.test.test_filevariables -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Mamba Emacs variable declarations related class and methods
"""


class FileVariableError(Exception):
    pass


class FileVariables(object):
    """
    Emacs local variables format parser for Mamba.

    We don't use twisted self implementation because we need extra stuff.
    """

    _filename = None

    def __init__(self, filename=None):
        """Initialize"""

        self._filename = filename
        self._local_vars = dict()
        self._load_variables()

    def get_value(self, key):
        """Return a value"""

        return self._local_vars.get(key, None)

    def get_variables(self):
        """Return the local variables"""

        return self._local_vars

    def _load_variables(self):
        """
        Load the Emacs variable desclarations from _filename.

        See http://kcy.me/6hso
        """

        if not self._filename:
            raise FileVariableError('No filename has been given')

        fd = file(self._filename, 'r')  # Just the first two lines
        lines = [fd.readline(), fd.readline()]
        fd.close()
        for line in lines:
            try:
                self._parse_variables(line)
            except ValueError:
                pass

    def _parse_variables(self, line):
        """
        Accepts a single line in Emacs local variable declaration format and
        returns a dict of all the variables {key: value} found.
        Raises ValueError if 'line' is in the wrong format.

        This method has been extract from Twisted framework directly

        See http://kcy.me/6hso
        """
        paren = '-*-'
        start = line.find(paren) + len(paren)
        end = line.rfind(paren)
        if start == -1 or end == -1:
            raise ValueError(
                "%r not a valid local variable declaration" % (line,))
        items = line[start:end].split(';')

        for item in items:
            if len(item.strip()) == 0:
                continue
            split = item.split(':')
            if len(split) != 2:
                raise ValueError("%r contains invalid declaration %r"
                                 % (line, item))
            self._local_vars[split[0].strip()] = split[1].strip()
