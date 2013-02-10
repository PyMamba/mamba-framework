# -*- test-case-name: mamba.test.test_borg -*-
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: borg
    :platform: Unix, Windows
    :synopsys: Mamba implementation of Alex Martelli's Borg 'no-pattern'

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""


class Borg(object):
    """The Mamba Borg Class.

    Every object created using the Borg pattern will share their information,
    as long as they refer to the same state information. This is a more elegant
    type of singleton, but, in other hand, Borg objects doesn't have the
    same ID, every object have his own ID

    Borg objects doesn't share data between inherited classes. If a class A
    inherits from Borg and a class B inherits from A then A and B doesn't share
    the same namespace

    Example::

        class LockerManager(borg.Borg):

            def __init__(self):
                super(LockerManager, self).__init__()

    Used as::

        >>> manager1 = LockerManager()
        >>> manager1.name = 'Locker One'
        >>> manager2 = LockerManager()
        >>> print(manager2.name)
        Locker One
        >>>
    """
    _shared_state = {}

    def __new__(cls, *args, **kwargs):
        obj = super(Borg, cls).__new__(cls, *args, **kwargs)
        obj.__dict__ = cls._shared_state.setdefault(cls, {})
        return obj
