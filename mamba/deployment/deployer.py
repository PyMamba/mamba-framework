# -*- test-case-name: mamba.deployment.test_deployer -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Mamba deployer
"""

from mamba import plugin


class DeployerError(Exception):
    pass


class DeployerProvider:
    """
    Mount point for plugins which refer to Deploters for out applications.

    Deployers implementing this reference should implement the IDeployer
    interface
    """

    __metaclass__ = plugin.ExtensionPoint
