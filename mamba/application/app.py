# -*- test-case-name: mamba.test.test_application,mamba.test.test_mamba -*-
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

import fnmatch
import sys
import os

from twisted.python import versions, log, filepath
from twisted.python.dist import twisted_subprojects

from mamba import _version as _mamba_version
from mamba.application import controller, appstyles
from mamba.utils import borg

_app_ver = versions.Version('Application', 12, 3, 0)
_app_project_ver = versions.Version('Project', 0, 1, 0)


class ApplicationError(Exception):
    """ApplicationError raises when an error occurs"""

    pass


class Application(borg.Borg):
    """
    Mamba Application Manager.

    Mamba only works on GNU/Linux operating system.
    """

    def __init__(self, options=None):
        """L{mamba.application.app.Application} constructor"""

        super(Application, self).__init__()
        self._install_paths = dict()
        self._mamba_ver = _mamba_version.version.short()
        self._ver = _app_ver.short()
        self._port = 1936
        self._log_file = '/var/log/mamba/my_mamba_app.log'
        self._project_ver = _app_project_ver.short()

        self.name = 'Mamba Webservice v%s' % _mamba_version.version.short()
        self.description = \
            'Mamba %s is a Web applications framework that works ' \
            'over Twisted using ExtJS or Sencha as GUI enhancement ' \
            'Mamba has been developed by Oscar Campos ' \
            '<oscar.campos@member.fsf.org>' % _mamba_version.version.short()
        self.file = 'my_mamba_app.tac'
        self.js_dir = 'js'
        self.language = os.environ['LANG'].split('_')[0]
        self.lessjs = False
        self._managers = {
            'controller': controller.ControllerManager(),
            'styles': appstyles.AppStyles()
        }

        if options:
            for k, v in options.iteritems():
                setattr(self, k, v)

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
            raise ApplicationError("%s" % (
                "Given directory %s don\t exists" % path.dirname())
            )

        self._log_file = file

    @property
    def project_ver(self):
        return self._project_ver

    @project_ver.setter
    def project_ver(self, ver):
        if type(ver) is not versions.Version:
            raise ApplicationError("%s expected, get %s" % (
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


__all__ = [
    'Application', 'ApplicationError'
]
