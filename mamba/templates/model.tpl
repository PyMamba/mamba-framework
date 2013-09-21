# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-model -*-
# Copyright (c) ${year} - ${author} <${author_email}>

"""
.. model:: ${model_name}
    :plarform: ${platforms}
    :synopsis: ${synopsis}

.. modelauthor:: ${author} <${author_email}>
"""

# is better if you remove this star import and import just what you
# really need from storm.properties, storm.references and storm.expr
from storm.locals import *

from mamba.application import model


class ${model_class}(model.Model):
    """
    ${synopsis}
    """

    __storm_table__ = '${model_table}'

    ${model_properties}
