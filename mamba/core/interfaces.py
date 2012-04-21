
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Interface documentation.
"""

from zope.interface import Interface, Attribute


class INotifier(Interface):
    """
    Every Inotifier class will implement this interface
    """

    def _notify(wd, file_path, mask):
        """
        Notifies the chages on file_path filesystem directory
        The 'wd' param is ignored

        @param file_path: L{twisted.python.filepath.FilePath} on which the
        event happened
        @param mask: inotify event as hexadecimal mask
        """

    notifier = Attribute(
        """
        @type notifier: C{twisted.internet.inotify.INotify}
        @ivar notifier: A notifier to start watching a FilePath
        """
    )


class IController(Interface):
    """
    Manba Controllers interface.

    Every controller will implement this interface
    """

    name = Attribute(
        """
        @type name: C{string}
        @ivar name: Controller's name
        """
    )

    desc = Attribute(
        """
        @type desc: C{string}
        @ivar desc: Controller's description
        """
    )

    loaded = Attribute(
        """
        @type loaded: C{boolean}
        @ivar loaded: Returns true if the controller has been loaded, otherwise
                      returns false
        """
    )

    def get_register_path():
        """
        Return the controller register path for URL Rewriting

        @return a C{string}
        """


class IDeployer(Interface):
    """
    Mamba Deployers interface.

    Every deployer will implement this interface
    """

    mode = Attribute(
        """
        @type mode: C{string}
        @ivar mode: Deployer mode can be "local" or "remote" if unknown local
                    is assumed
        """
    )
