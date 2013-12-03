# -*- test-case-name: mamba.test.test_checkers -*-
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: checkers
    :platform: Unix, Windows
    :synopsis: Just some helper functions to check user inputs

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

import re
import string


class Checkers(object):
    """Just implement common methods to perform checks on user inputs

    .. versionadded:: 0.3.6
    """

    NONE, CAPS, NUMERIC, SYMBOLS = [1 << i for i in range(4)]
    MIN_LENGTH, NO_CAPS, NO_NUMBERS, NO_SYMBOLS = range(4)

    def __init__(self):
        super(Checkers, self).__init__()

    @staticmethod
    def check_email(email):
        """Checks if the given email is RFC2822 compliant

        http://www.rfc-editor.org/rfc/rfc2822.txt
        """

        RFC2822 = re.compile(
            r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*"
            "+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9]"
            ")?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
        )
        return True if RFC2822.match(email) is not None else False

    @staticmethod
    def check_password(password, min_length=8, characters=NONE):
        """Check for valid password using the given parameters

        :param password: the password to check
        :type password: str
        :param min_length: minimum password length (default 8)
        :type min_length: int
        :param characters: the valid cahracters to be used.
            A complete list of the possible options is as follows:

                * CAPS: Whatever can be used, we force some cap
                * NUMERIC: Whatever can be used, we force numbers
                * SYMBOLS: Whatever can be used, we force symbols

        :returns: a tuple containing a boolean value and a list of dicts
        """

        errors = []
        if len(password) < min_length:
            errors.append({
                'eng_desc': 'Minimum length is {}, but {} given'.format(
                    min_length, len(password)),
                'type': Checkers.MIN_LENGTH,
                'data': {'min_length': min_length, 'given': len(password)}
            })

        if characters & Checkers.CAPS > 0:
            if len(filter(str.isupper, password)) == 0:
                errors.append({
                    'eng_desc': 'String must contain caps',
                    'type': Checkers.NO_CAPS
                })

        if characters & Checkers.NUMERIC > 0:
            if len(filter(str.isdigit, password)) == 0:
                errors.append({
                    'eng_desc': 'String must comntain numbers',
                    'type': Checkers.NO_NUMBERS
                })

        if characters & Checkers.SYMBOLS > 0:
            if len(filter(lambda x: x in string.punctuation, password)) == 0:
                errors.append({
                    'eng_desc': 'String must comntain symbols',
                    'type': Checkers.NO_SYMBOLS
                })

        return len(errors) == 0, errors
