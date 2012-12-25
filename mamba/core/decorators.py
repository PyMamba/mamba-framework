# -*- test-case-name: mamba.test.test_decorators -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
.. module:: decorators
    :platform: Unix, Windows
    :synopsys: Decorators

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

import cPickle
import functools
from collections import OrderedDict


def cache(size=16):
    """
    Cache the results of the function if the same positional arguments
    are provided.

    We only store the size provided (if any) in MB, after that we should
    perform FIFO queries until the size of the cache is lower than
    the provided one.

    If the size is 0 then an unlimited cache is provided

    .. admonition:: Notice

        The memory size of the int_cache is just an approximation
    """
    int_cache = OrderedDict()

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if args in int_cache:
                return int_cache.get(args)

            result = func(*args, **kwargs)
            int_cache.update({args: result})

            if size != 0:
                while len(cPickle.dumps(int_cache)) >= size * 1024 * 1024:
                    int_cache.popitem(False)

            return result

        return wrapper

    return decorator


def unlimited_cache(func):
    """
    Just a wrapper over cache decorator to alias :meth:`@cache(size=0)`
    """
    @functools.wraps(func)
    @cache(size=0)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
