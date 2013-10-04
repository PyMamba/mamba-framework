
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: interfaces
    :platform: Unix, Windows
    :synopsys: Interfaces Documentation

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

from zope.interface import Interface, Attribute


class INotifier(Interface):
    """Every Inotifier class will implement this interface
    """

    def _notify(ignore, file_path, mask):
        """
        Notifies the chages on file_path filesystem directory
        The 'ignore' param is ignored

        :param file_path: :class:`~twisted.python.filepath.FilePath` on which
                          the event happened`
        :type file_path: :class:`~twisted.python.filepath.FilePath`
        :param mask: inotify event as hexadecimal mask
        :type mask: int
        """

    notifier = Attribute(
        """
        :param notifier: A notifier to start watching a FilePath
        :type notifier: :class:`~twistd.internet.inotify.INotify`
        """
    )


class IController(Interface):
    """
    Manba Controllers interface.

    Every controller will implement this interface
    """

    name = Attribute(
        """
        :param name: Controller's name
        :type name: str
        """
    )

    __route__ = Attribute(
        """
        :param __route__: Controller's route
        :type __route__: str
        """
    )

    loaded = Attribute(
        """
        :param loaded: True if the controller has been loaded, otherwise
                       returns False
        :type loaded: bool
        """
    )


class IDeployer(Interface):
    """
    Mamba Deployers interface.

    Every deployer must implement this interface
    """


class IResponse(Interface):
    """
    Mamba Web Response interface.

    Every web response must implement this interface.
    """

    code = Attribute(
        """
        :param code: the HTTP response code
        :type code: number
        """
    )

    body = Attribute(
        """
        :param body: the HTTP response body
        :type body: string
        """
    )

    headers = Attribute(
        """
        :param headers: the HTTP response headers
        :type headers: dict
        """
    )


class IMambaSQL(Interface):
    """
    Mamba SQL interface.

    I'm usefull to create common SQL queries for create or alter tables
    for all the SQL backends supported by Mamba.
    """

    original = Attribute(
        """
        :param original: the original underlying SQL backend type
        """
    )

    def parse_column(self, column):
        """Parse a Storm column to the correct SQL value
        """

    def detect_primary_key(self):
        """Detect and reeturn the primary key for the table
        """

    def create_table(self):
        """
        Return the SQL syntax string to create a table to the selected
        underlying database system
        """

    def drop_table(self):
        """
        Return the SQL syntax string to drop a table from the selected
        underlying database system
        """

    def insert_data(self):
        """Return the SQL syntax string to insert data that populate a table
        """


class ISession(Interface):
    """
    Mamba Session interface.
    I'm just a Session interface used to store objects in Twisted Sessions
    """

    session = Attribute('A Mamba Session object')
