# -*- test-case-name: mamba.test.test_fabric -*-
# Copyright (c) 2012 - 2013 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: fabric_deployer
    :plarform: Unix, Windows
    :synopsis: Fabric plugin for Mamba deployer.

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

import sys

from twisted.python import log, filepath

try:
    from fabric import state
    from fabric.tasks import execute
    from fabric import main as fabric_main
except ImportError:
    log.err('Fabric is not installed on this system')
    raise  # propagate

from mamba.deployment import deployer
from mamba.utils.filevariables import FileVariables


class FabricMissingConfigFile(deployer.DeployerError):
    """Fired when missing config file is detected
    """


class FabricConfigFileDontExists(deployer.DeployerError):
    """Fired when the config file does not exists
    """


class FabricNotValidConfigFile(deployer.DeployerError):
    """Fired when the config file is not valid
    """


class FabricDeployer(deployer.DeployerProvider):
    """Fabric Deployment System compatible with Mamba Plugabble Interface
    """

    def __init__(self):
        self.name = 'Fabric'
        self.mode = 'remote'
        self.deployer_object = None
        self.deployer_name = None
        self.deployer_module = None

    def deploy(self, config_file=None):
        """Deploys the system following the configuration in the config file
        """

        if config_file is None:
            raise FabricMissingConfigFile(
                'deploy was called without \'config_file\' parameter'
            )

        if not filepath.exists(config_file):
            raise FabricConfigFileDontExists(
                'The {file} file doesn\'t exists'.format(file=config_file)
            )

        if not _valid_file(config_file):
            raise FabricNotValidConfigFile(
                'The {file} file is not a valid Fabric config file'.format(
                    file=config_file
                )
            )

        try:
            self.load(config_file)
        except SystemExit:
            raise  # propagate
        except KeyboardInterrupt:
            if state.output.status:
                sys.stderr.write('\nStopped\.n')
            sys.exit(1)
        except Exception:
            sys.excepthook(*sys.exc_info())
            # we might leave stale threads if we don't explicitly exit()
            sys.exit(1)
        finally:
            fabric_main.disconnect_all()

    def identify(self):
        """Returns the deployer identity
        """

        return self.name

    def operation_mode(self):
        """Return the operation mode for this deployer
        """

        return self.mode

    def load(self, config_file):
        """Load the workflow rules from a Mamba .dc Python file

        :param config_file: The file where to load the configuration from
        :type config_file: str
        """

        module_name = filepath.splitext(filepath.basename(config_file))[0]

        if self.deployer_object and self.deployer_object.loaded:
            raise deployer.DeployerError(
                'Tried to load {module} deployer that is '
                'already loaded!'.format(module=module_name)
            )

        self.deployer_name = module_name
        self.deployer_module = deployer.deployer_import(
            self.deployer_name,
            config_file
        )

        # load tasks
        docstring, new_style, classic, default = (
            fabric_main.load_tasks_from_module(self.deployer_module)
        )
        self.tasks = {
            'docstring': docstring,
            'functions': new_style if state.env.new_style_tasks else classic,
            'default': default
        }

        state.commands.update(self.tasks.get('functions', {}))

        # abort if no commands found
        if not state.commands:
            log.err('No commands found ...aborting')
        else:
            for name in state.commands:
                execute(name)


def _valid_file(config_file):
    """
    Return True if 'config_file' is a valid config file, otherwise return False

    :param config_file: the file to check
    :type config_file: str
    """

    basename = filepath.basename(config_file)
    if filepath.splitext(basename)[1] == '.dc':
        ftype = FileVariables(config_file).get_value('mamba-deployer')
        if ftype and ftype == 'fabric':
            return True

    return False
