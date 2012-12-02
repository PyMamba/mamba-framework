# -*- test-case-name: mamba.deployment.test_deployer -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
.. module:: deployer
    :platform: Linux
    :synopsis: Deployment pluggable system for Mamba.

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

from mamba import plugin


__all__ = ['DeployerError', 'DeployerProvider']


class DeployerError(Exception):
    pass


class DeployerProvider:
    """
    Mount point for plugins which refer to Deployers for our applications.

    Deployers implementing this reference should implement the IDeployer
    interface
    """

    __metaclass__ = plugin.ExtensionPoint
