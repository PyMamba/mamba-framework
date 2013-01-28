# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-model -*-
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>

"""
.. model:: Dummy
    :plarform: Linux
    :synopsis: Dummy model for testing purposes

.. modelauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

from storm.locals import Int, Unicode

from mamba.application import model


class DummyModel(model.Model, model.ModelProvider):
    """Dummy model for testing purposes
    """

    __storm_table__ = 'dummy'

    id = Int(primary=True, unsigned=True, auto_increment=True)
    name = Unicode(size=64, allow_none=False)

    def __init__(self, name=None):
        super(DummyModel, self).__init__()

        if name is not None:
            self.name = unicode(name)
