
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
.. module:: interfaces
    :platform: Unix, Windows
    :synopsys: Interfaces Documentation

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

from zope.interface import Interface, Attribute


class INotifier(Interface):
    """
    Every Inotifier class will implement this interface

    .. versionadded:: 0.1
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

    .. versionadded:: 0.1
    """

    name = Attribute(
        """
        :param name: Controller's name
        :type name: str
        """
    )

    desc = Attribute(
        """
        :param desc: Controller's description
        :type desc: str
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

    .. versionadded:: 0.1
    """


class IResponse(Interface):
    """
    Mamba Web Response interface.

    Every web response must implement this interface.

    .. versionadded:: 0.1
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
