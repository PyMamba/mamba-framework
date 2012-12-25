# -*- test-case-name: mamba.test.test_project_manager -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Project Manager for L{mamba.project} used by L{mamba.application}
"""

from mamba.utils import borg


class ProjectManagerError(Exception):
    """L{mamba.project.manager} exceptions"""
    pass


class ProjectManager(borg.Borg):
    """Mamba Project Manager

    L{mamba.project.manager.ProjectManager} inherits from
    L{mamba.utils.borg.Borg} you can create as many ProjectManager objects
    as you want and them all will share data as long as they refer to the
    same state information.

    The L{mamba.project.manager.ProjectManager} class manage all the Mamba
    project aspects.
    """

    _project_options = None

    def __init__(self, options):
        """Constructor"""

        self._project_options = options
        super(ProjectManager, self).__init__()
