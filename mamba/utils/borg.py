# -*- test-case-name: mamba.utils.test.test_borg -*- 
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Mamba implementation of Alex Martelli's Borg 'no-pattern'
"""

class Borg(object):
    """The Mamba Borg Class.
    
    Every object created using the Borg pattern will share their information, as long as
    they refer to the same state information. This is a more elegant type of singleton, but, 
    in other hand, Borg objects doesn't have the same ID, every object have his own ID
    """
    _shared_state = {}
    def __init__(self):
        self.__dict__ = self._shared_state
