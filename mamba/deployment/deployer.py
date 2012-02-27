# -*- test-case-name: mamba.deployment.test_deployer -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Mamba deployer
"""

from zope.interface import Interface, Attribute

from mamba import plugin
from mamba.utils import borg
from mamba.core import module

class DeployerError(Exception):
	pass


class DeployerProvider:
	"""
	Mount point for plugins which refer to Deploters for out applications.

	Deployers implementing this reference should implement the IDeployer
	interface
	"""

	__metaclass__ = plugin.ExtensionPoint

