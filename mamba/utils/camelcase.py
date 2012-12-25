# -*- test-case-name: mamba.test.test_camelcase -*-
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
.. module:: borg
    :platform: Unix, Windows
    :synopsys: Stupid class that just offers stupid CamelCase functionality

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""


class CamelCase(object):
    """
    Stupid class that just offers stupid CamelCase funcionallity

    :param camelize: the string to camelize
    :type camelize: str
    """

    def __init__(self, camelize):
        self._camelized = None
        self._camelize = camelize
        super(CamelCase, self).__init__()

    def camelize(self, union=False):
        """
        Camelize and return camelized string

        :param union: if true is will use a space between words
        :type union: bool
        """

        if not union:
            joiner = ' '
        else:
            joiner = ''

        if type(self._camelize) is str:
            self._camelized = joiner.join(
                [p.capitalize() for p in self._camelize.split(' ')])
        elif type(self._camelize) is tuple or type(self._camelize) is list:
            self._camelized = joiner.join([
                p.capitalize() for p in self._camelize])
        elif type(self._camelize) is unicode:
            self._camelized = joiner.join([
                p.capitalize() for p in self._camelize.split(' ')])
        else:
            raise ValueError('Expected str, tuple or list get %s instead.' % (
                type(self._camelize)))

        return self._camelized
