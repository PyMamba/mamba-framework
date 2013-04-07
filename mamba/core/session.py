
# Copyright (c) 2012 - 2013 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: session
    :platform: Unix, Windows
    :synopsis: Just a wrapper around Twisted Sessions

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

from zope.interfaces import implements
from twisted.python.components import registerAdapter
from twisted.web.server import Session as TwistedSession

from mamba.core.interfaces import ISession


class Session(TwistedSession):
    """Mamba session wrapper
    """

    authed = False

    def authenticate(self):
        """Set authed as True
        """

        self.authed = True

    def is_authed(self):
        """Return the authed value
        """

        return self.authed

    def set_lifetime(self, lifetime):
        """Set the sessionTimeout to lifetime value

        :param lifetime: the value to set as session timeout in seconds
        :type lifetime: int
        """

        self.sessionTimeout = lifetime


class MambaSession(object):
    """An authed session store object
    """

    implements(ISession)

    def __init__(self, session):
        self.session = session


registerAdapter(MambaSession, Session, ISession)
