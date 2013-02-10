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

from twisted.python import versions, log, filepath

from mamba.utils import borg
from mamba import _version as _mamba_version
from mamba.application import controller, scripts, appstyles, model


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
        self._install_paths = dict()
        self._mamba_ver = _mamba_version.version.short()
        self._ver = _app_ver.short()
        self._port = 1936
        self._log_file = None
        self._project_ver = _app_project_ver.short()

        self.name = 'Mamba Webservice v%s' % _mamba_version.version.short()
        self.description = (
            'Mamba %s is a Web applications framework that works '
            'over Twisted using JavaScript libraries as GUI enhancement '
            'Mamba has been developed by Oscar Campos '
            '<oscar.campos@member.fsf.org>' % _mamba_version.version.short()
        )
        self.file = 'my_mamba_app.tac'
        self.js_dir = 'js'
        self.language = os.environ['LANG'].split('_')[0]
        self.lessjs = False
        self.managers = {
            'controller': controller.ControllerManager(),
            'scripts': scripts.Scripts(),
            'styles': appstyles.AppStyles(),
            'model': model.ModelManager()
        }

        if options:
            for key in dir(options):
                if not key.startswith('__'):
                    if key == 'port':
                        setattr(self, '_port', getattr(options, key))
                    elif key == 'version':
                        setattr(self, '_ver', getattr(options, key))
                    elif key == 'logfile':
                        setattr(self, '_log_file', getattr(options, key))
                    else:
                        setattr(self, key, getattr(options, key))

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


__all__ = ['Mamba', 'ApplicationError']
