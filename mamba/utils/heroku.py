# -*- test-case-name: mamba.test.test_heroku -*-
# Copyright (c) 2013 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: heroku
    :platform: Unix, Windows
    :synopsis: Heroku helper functions and classes

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

import os


def are_we_on_heroku():
    """
    Determine if we are running in heroku or not

    Heroku python environments declare several nevironment variables,
    one of them is the ```PYTHONHOME``` that normally should contain the
    value ```/app/.heroku/python```, we use this environment variable
    to determine if we are running on heroku

    .. versionadded:: 0.3.6
    """

    return '.heroku' in os.environ.get('PYTHONHOME', '')
