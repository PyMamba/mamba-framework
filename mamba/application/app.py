# -*- test-case-name: mamba.test.test_application mamba.test.test_mamba -*-
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module: app
    :platform: Linux
    :synopsis: Mamba Application Manager

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

import os
import gc

from twisted.web import http
from twisted.internet import address
from twisted.python.logfile import DailyLogFile
from twisted.python.monkey import MonkeyPatcher
from twisted.python import versions, filepath, log

from mamba.utils import borg
from mamba.http import headers
from mamba import _version as _mamba_version
from mamba.application import controller, model


_app_ver = versions.Version('Application', 0, 1, 0)
_app_project_ver = versions.Version('Project', 0, 1, 0)


class ApplicationError(Exception):
    """ApplicationError raises when an error occurs
    """


class Mamba(borg.Borg):
    """
    This object is just a global configuration for mamba applications that
    act as the central object on them and is able to act as a central registry.
    It inherits from the :class: `~mamba.utils.borg.Borg` so you can just
    instantiate a new object of this class and it will share all the
    information between instances.

    You create an instance of the :class:`~Mamba` class in your main module
    or in your `Twisted` `tac` file:

    .. sourcecode:: python

        from mamba import Mamba
        app = Mamba({'name': 'MyApp', 'description': 'My App', ...})

    Mamba only works in the GNU/Linux operating system (for now).

    :param options: options to initialize the application with
    :type options: dict

    """

    def __init__(self, options=None):
        """Mamba constructor"""

        super(Mamba, self).__init__()

        self.monkey_patched = False
        self.already_logging = False
        self._mamba_ver = _mamba_version.version.short()
        self._ver = _app_ver.short()
        self._port = 1936
        self._log_file = None
        self._project_ver = _app_project_ver.short()

        self.name = 'Mamba Webservice v%s' % _mamba_version.version.short()
        self.description = (
            'Mamba %s is a Web applications framework that works '
            'over Twisted using Jinja2 as GUI enhancement '
            'Mamba has been developed by Oscar Campos '
            '<oscar.campos@member.fsf.org>' % _mamba_version.version.short()
        )

        self.language = os.environ.get('LANG', 'en_EN').split('_')[0]
        self.lessjs = False

        self._parse_options(options)

        # monkey patch twisted
        self._monkey_patch()

        # register log file if any
        if self.log_file is not None:
            self.already_logging = True
            log.startLogging(DailyLogFile.fromFullPath(self.log_file))

        # PyPy does not implement set_debug method in gc object
        if getattr(options, 'debug', False):
            if hasattr(gc, 'set_debug'):
                gc.set_debug(gc.DEBUG_STATS | gc.DEBUG_INSTANCES)
            else:
                log.msg(
                    'Debug is set as True but gc object is laking '
                    'set_debug method'
                )

        self._header = headers.Headers()
        self._header.language = self.language
        self._header.description = self.description

        self.managers = {
            'controller': controller.ControllerManager(),
            'model': model.ModelManager()
        }

        # self._prepare_render_keys()

    def _prepare_render_keys(self):
        self.render_keys = {
            'doctype': self._header.get_doctype(),
            'header': {
                'title': self.name,
                'content_type': self._header.content_type,
                'generator_content': self._header.get_generator_content(),
                'description_content': self._header.get_description_content(),
                'language_content': self._header.get_language_content(),
                'mamba_content': self._header.get_mamba_content(),
                'media': self._header.get_favicon_content('assets'),
                'styles': self.managers['styles'].get_styles().values(),
                'scripts': self.managers['scripts'].get_scripts().values()
            }
        }

    def _parse_options(self, options):
        if options is not None:
            for key in dir(options):
                if not key.startswith('__'):
                    if key == 'port':
                        setattr(self, '_port', getattr(options, key))
                    elif key == 'version':
                        setattr(self, '_ver', getattr(options, key))
                    elif key == 'log_file':
                        setattr(self, '_log_file', getattr(options, key))
                    else:
                        setattr(self, key, getattr(options, key))

    def _monkey_patch(self):
        """
        Monkeypatch some parts of the twisted library that are waiting
        for bugfix inclussion in the trunk
        """

        if not self.monkey_patched:
            # add new method
            setattr(http.Request, 'getClientProxyIP', getClientProxyIP)

            # patch getClientIP
            monkey_patcher = MonkeyPatcher(
                (http.Request, 'getClientIP', getClientIPPatch)
            )
            monkey_patcher.patch()
            self.monkey_patched = True

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        if type(value) is not int:
            raise ApplicationError("Int expected, get %s" % (type(value)))

        self._port = value

    @property
    def log_file(self):
        return self._log_file

    @log_file.setter
    def log_file(self, file):
        path = filepath.FilePath(file)
        if not filepath.exists(path.dirname()):
            raise ApplicationError('%s' % (
                'Given directory %s don\t exists' % path.dirname())
            )

        self._log_file = file

    @property
    def project_ver(self):
        return self._project_ver

    @project_ver.setter
    def project_ver(self, ver):
        if type(ver) is not versions.Version:
            raise ApplicationError('%s expected, get %s' % (
                'twisted.python.versions.Version', type(ver))
            )

        self._project_ver = ver

    @property
    def mamba_ver(self):
        return self._mamba_ver

    @mamba_ver.setter
    def mamba_ver(self, value):
        raise ApplicationError("'mamba_ver' is readonly")

    @property
    def ver(self):
        return self._ver

    @ver.setter
    def ver(self, value):
        raise ApplicationError("'ver' is readonly")


def getClientIPPatch(self):
    """
    Return the IP address of the client who submitted this request. If
    there are headers for X-Forwarded-For, they are returned as well.

    If you need to get the value of Request.client.host you can use the
    new patched method Request.getClientProxyIP() on Request objects.

    :returns: the client IP address(es)
    """
    x_forwarded_for = self.getHeader('x-forwarded-for')

    if x_forwarded_for is not None:
        return x_forwarded_for.split(', ')[0]

    return self.getClientProxyIP()


def getClientProxyIP(self):
    """
    Return the IP address of the client/proxy who submitted the request.

    :returns: the client/proxy IP address or None
    """

    if isinstance(self.client, address.IPv4Address):
        return self.client.host

    return None


__all__ = ['Mamba', 'ApplicationError']
