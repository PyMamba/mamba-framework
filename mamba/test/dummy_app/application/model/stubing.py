# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-model -*-
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>

"""
.. model:: Stubing
    :platform: Linux
    :synopsis: Stubing dumming stupid dubing

.. modelauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

from storm.locals import Int, Unicode

from mamba.application import model


class StubingModel(model.Model, model.ModelProvider):
    """Stubing dumming stupid dubing
    """

    __storm_table__ = 'stubing'

    id = Int(primary=True, unsigned=True, auto_increment=True)
    name = Unicode(size=64, allow_none=False)

    def __init__(self, name=None):
        super(StubingModel, self).__init__()

        if name is not None:
            self.name = unicode(name)
