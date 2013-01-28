# -*- test-case-name: mamba.scripts.test.test_commons -*-
# Copyright (c) 2012 - 2013 Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
.. module:: commons
    :platform: Unix, Windows
    :synopsis: Commono utilities used in mamba scripts

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

from __future__ import print_function
import sys
import imp
import functools

from twisted.python import filepath

from mamba.utils.output import bold, darkgreen, darkred, create_color_func


class Interaction(object):
    """User interaction class
    """

    @staticmethod
    def userquery(prompt, response=None, colors=None):
        """
        Taken from Gentoo emerge tool and adapted to Mamba. This function
        just ask a simple question to the user that shoudl be answered with
        yes or no

        :param prompt: the prompt to be shown to the user
        :type prompt: str
        :param response: a tuple or list with the posible responses
        :type response: tuple or list
        :param colors: a tuple ot list with the colors for responses
        """

        if response is None:
            response = ('Yes', 'No')
        elif type(response) is not tuple and type(response) is not list:
            print('Error: response must be tuple or list')
            sys.exit(1)

        if colors is None:
            colors = (
                create_color_func('darkgreen'),
                create_color_func('darkred')
            )
        else:
            if type(colors) is not tuple and type(colors) is not list:
                print('Error: colors must be tuple or list')
                sys.exit(1)

            colors = tuple([create_color_func(color) for color in colors])

        print('\n{}'.format(prompt), end=' ')
        try:
            while True:
                result = raw_input('[{}] '.format(
                    '/'.join([colors[i](response[i])
                    for i in range(len(response))])
                ))

                if result:
                    for key in response:
                        if result.upper() == key[:len(result)].upper():
                            return key

                print(
                    'Sorry, response "{}" not understood.'.format(result),
                    end=' '
                )
        except (EOFError, KeyboardInterrupt):
            print('Interrupted')
            sys.exit(1)
        except IndexError:
            print('Response number is greater than colors tuple')
            sys.exit(1)

    @staticmethod
    def userchoice(prompt, choices, help):
        """
        Choices menu for user input.

        The user get a menu with help content for choices index followed by
        a numeric index value. The user just choose a numeric index for his
        choice and this choice is returned back

        :param prompt: the prompt to be shown to the user
        :type prompt: str
        :param choices: the choices to be shown
        :type choices: tuple or list
        :param help: the help to be shown
        :type help: tuple or list
        """

        if help is None:
            raise RuntimeError('Help can not be None')

        if len(choices) != len(help):
            raise RuntimeError(
                'Choices and Help should has the same number of items'
            )

        if len(choices) == 0 or len(help) == 0:
            raise RuntimeError('Nor choices or help can be empty')

        color = create_color_func('blue')
        print('\n{}'.format(prompt))
        try:
            while True:
                for choice in choices:
                    print('{} [{}] '.format(
                        color(help[choices.index(choice)].ljust(30)),
                        bold(str(choices.index(choice)))
                    ))

                response = raw_input('[{}] '.format(
                    '/'.join([str(choices.index(choices[i]))
                    for i in range(len(choices))])
                ))

                if response:
                    for key in choices:
                        # an empty response will match the first
                        # value in responses
                        if response == str(choices.index(key))[:len(response)]:
                            return key

                print('Sorry, response "{}" not understood.'.format(response))
                print('\n{}'.format(prompt))
        except (EOFError, KeyboardInterrupt):
            print('Interrupted')
            sys.exit(1)

    @staticmethod
    def userinput(prompt):
        """
        Process user input

        :param prompt: the prompt to be shown
        :type prompt: str
        """

        print('\n{}'.format(bold(prompt)))
        try:
            response = raw_input('$ ')
            if response:
                return response
        except (EOFError, KeyboardInterrupt):
            print('Interrupted')
            sys.exit(1)


def import_services():
    """I try to import services file from application directory
    """

    path = filepath.FilePath('mamba_services.py')
    if not path.exists():
        raise ImportError('mamba_services.py file does not exists')

    code = compile(path.open('U').read(), path.path, 'exec')

    # create a new module
    module = imp.new_module('mamba_services')
    sys.modules['mamba_services'] = module

    # fill the module scope
    module.__name__ = 'mamba_services'
    module.__file__ = 'mamba_services.py'

    try:
        exec code in module.__dict__
    except:
        del sys.modules['mamba_services']
        # propagate
        raise

    return module


def decorate_output(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            print('[{}]'.format(darkgreen('Ok')))
            return result
        except:
            print('[{}]'.format(darkred('Fail')))
            raise

    return wrapper
