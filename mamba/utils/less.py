# -*- test-case-name: mamba.test.test_less -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Mamba less compiler
"""

import os

from twisted.python import filepath
from twisted.web import resource, server
from twisted.internet import utils


class LessResource(resource.Resource):
    """
    Mamba LessResource class define a web accesible LESS script
    """

    isLeaf = True
    less_exec = 'lessc'

    def render_GET(self, request):
        """
        Try to compile a LESS file and then serve it as CSS
        """

        self.less_compiler = LessCompiler(request.postpath[0], self.less_exec)

        d = self.less_compiler.compile()

        def cb_sendback(resp):
            """
            Write result from callback
            """
            request.write(resp)
            request.finish()

        d.addCallback(cb_sendback)

        return server.NOT_DONE_YET


class LessCompiler(object):
    """
    Compile LESS scripts if LESS NodeJS compiler is present. Otherwise
    adds the less.js JavaScript compiler to the page.
    """

    def __init__(self, style, exe='lessc'):
        super(LessCompiler, self).__init__()
        self.stylesheet = style
        self.exe = exe

    def compile(self):
        """
        Compile a LESS script
        """

        d = utils.getProcessOutput(self.exe, [self.stylesheet], os.environ)
        d.addCallbacks(self._get_compiled, self._get_script)

        return d

    def _get_compiled(self, resp):
        """
        Return the result compiled LESS script
        """

        return resp.decode('utf-8')

    def _get_script(self, ignore):
        """
        Return the LESS script and set Application use of LESS compiler
        script as True
        """

        from mamba.application import app
        mamba_app = app.Mamba()
        mamba_app.lessjs = True

        return filepath.FilePath(self.stylesheet).getContent().decode('utf-8')


__all__ = ["LessResource", "LessCompiler"]
