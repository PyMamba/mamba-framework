# -*- test-case-name: mamba.core.test.test_decorators -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
.. module:: decorators
    :platform: Unix, Windows
    :synopsys: Decorators

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

import functools


def cache(size=16):
    """
    Cache the results of the function if the same positional arguments
    are provided.

    We only store the size provided (if any) in MB, after that we should
    perform FIFO queries until the size of the cache is lower than
    the provided one.

    If the size is 0 then an unlimited cache is provided
    """
    cache = list()

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for result in cache:
                if args == result[0]:
                    return result[1]

            result = func(*args, **kwargs)
            cache.append((args, result))

            if size != 0:
                while cache.__sizeof__() >= size * 1024 * 1024:
                    cache.pop(0)

            return result

        return wrapper

    return decorator


def unlimited_cache(func):
    """
    Just a wrapper over cache decorator to alias @cache(size=0)
    """
    @functools.wraps(func)
    @cache(size=0)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
