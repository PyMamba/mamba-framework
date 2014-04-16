
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details


try:
    import ujson as json
except ImportError:
    import json

__all__ = ['json']

__doc__ = '''
Subpackage containing the modules that implement common utilities
'''
