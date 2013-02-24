
from os.path import normpath

from mamba.core import module


class ControllerManager(module.ModuleManager):
    """
    Uses a ControllerProvider to load, store and reload Mamba Controllers.

    :attr:`_model_store` A private attribute that sets the prefix
    path for the controllers store
    """

    def __init__(self):
        """Initialize
        """

        self._module_store = 'application/controller'
        super(ControllerManager, self).__init__()

    def get_controllers(self):
        """Return the controllers pool
        """

        return self._modules

    def is_valid_file(self, file_path):
        """
        Check if a file is a Mamba controller file

        :param file_path: the file path of the file to check
        :type file_path: str
        """

        return self._valid_file(
            normpath('{}/{}'.format(self._module_store, file_path)),
            'mamba-controller'
        )
