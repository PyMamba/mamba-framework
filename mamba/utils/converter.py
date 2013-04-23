# -*- test-case-name: mamba.test.test_converter -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module: converter
    :platform: Unix, Windows
    :synopsis: Converts to serializable objects that are exportable in JSON

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

import logging
import collections

from twisted.python import log


class Converter(object):
    """
    Object Converter class
    """

    primitives = (int, long, float, bool, str, unicode)
    containers = (str, tuple, list, dict)

    def __init__(self):
        super(Converter, self).__init__()

    @staticmethod
    def serialize(obj):
        """Serialize an object and returns it back"""
        try:
            if type(obj) not in Converter.primitives:
                if type(obj) is dict:
                    tmpdict = {}
                    for key, value in obj.iteritems():
                        tmpdict.update({
                            key: Converter.serialize(value)
                        })

                    return tmpdict
                elif getattr(obj, '__class__', False):
                    if type(obj) not in Converter.containers:
                        tmpdict = {}
                        if getattr(obj, '__dict__', False):
                            for key, value in obj.__dict__.iteritems():
                                if not key.startswith('_'):
                                    tmpdict.update({key: value})
                        else:
                            for item in dir(obj):
                                if not item.startswith('_'):
                                    tmpdict.update({item: getattr(obj, item)})

                        return tmpdict
                elif type(obj) is collections.Iterable:
                    values = []
                    for value in obj:
                        values.append(Converter.serialize(value))

                    return values
        except AttributeError as error:
            log.msg(error, logLevel=logging.WARN)

        return obj
