
# Copyright (c) 2012 - 2013 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

from twisted.trial import unittest

from mamba.deployment import deployer


class DummyDeployerTest(deployer.DeployerProvider):
    """A Dummy Deployer for testing purposes
    """

    name = 'Dumb'
    mode = 'local'

    def deploy(self):
        return 'OMG! I am deploying!'

    def identify(self):
        return '{name} Deployer System'.format(name=self.name)

    def operation_mode(self):
        return self.mode


class DeployerExtensionTest(unittest.TestCase):
    """Tests for mamba.deployment.deployer
    """

    def test_deployment_extension_points(self):
        for deployer_ in DummyDeployerTest.plugins:
            if deployer_().identify() != 'Dumb':
                continue

            self.assertEqual(deployer_().deploy(), 'OMG! I am deploying')
            self.assertEqual(deployer_(), 'Dumb Deployer System')
            self.assertIdentical(deployer_().operation_mode(), 'local')
