# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-controller -*-
# Copyright (c) ${year} - ${author} <${author_email}>

"""
.. controller:: ${controller_name}
    :platform: ${platforms}
    :synopsis: ${synopsis}

.. controllerauthor:: ${author} <${author_email}>
"""

from mamba.web.response import Ok
from mamba.application import route
from mamba.application import controller


class ${controller_class}(controller.Controller):
    """
    ${synopsis}
    """

    name = '${controller_class}'
    __route__ = '${register_path}'

    def __init__(self):
        """
        Put your initializarion code here
        """
        super(${controller_class}, self).__init__()

    @route('/')
    def root(self, request, **kwargs):
        return Ok('I am the ${controller_class}, hello world!')
