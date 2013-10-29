# -*- test-case-name: mamba.test.test_less -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
Mamba less compiler
"""

import os
from functools import partial

from twisted.internet import utils
from twisted.python import filepath
from twisted.web import resource, server


class LessResource(resource.Resource):
    """
    Mamba LessResource class define a web accesible LESS script
    """

    isLeaf = True
    less_exec = 'lessc'

    def __init__(self, path=None):
        self.path = path

    def render_GET(self, request):
        """
        Try to compile a LESS file and then serve it as CSS
        """

        if self.path is None:
            self.less_compiler = LessCompiler(
                request.postpath[0], exe=self.less_exec
            )
        else:
            self.less_compiler = LessCompiler(
                request.prepath[1], exe=self.less_exec, path=self.path
            )

        # windows can't handle with non existrnt commands in CreateProcess
        # and raises an exception so we have to hack this here to support
        # fallback on windows platform
        # NOTE: I don't know why but if you use maybeDeferred here, Windows
        # implementations get stuck here forever until it fails with an
        # exception from CreateProcess. Win is not my main platform so I
        # decided to patch this to make it work but we really need a win
        # developer that care to port mamba to windows properly

        d = self.less_compiler.compile()

        if type(d) is unicode:
            return bytes(d)
        else:
            def cb_sendback(resp):
                """
                Write result from callback
                """
                request.write(bytes(resp))
                request.finish()

            d.addCallback(cb_sendback)

            return server.NOT_DONE_YET


class LessCompiler(object):
    """
    Compile LESS scripts if LESS NodeJS compiler is present. Otherwise
    adds the less.js JavaScript compiler to the page.
    """

    def __init__(self, style, exe='lessc', path=None):
        super(LessCompiler, self).__init__()
        self.stylesheet = style
        self.exe = exe
        self.path = path

    def compile(self):
        """
        Compile a LESS script
        """

        style_path = self.stylesheet if self.path is None else self.path

        # windows can't handle with non existent commands in CreateProcess
        # and raise an exception so we have to hack this here to support
        # fallback on windows platforms
        try:
            d = utils.getProcessOutput(self.exe, [style_path], os.environ)
            d.addCallbacks(
                self._get_compiled, partial(self._get_script, style_path)
            )
            return d
        except Exception:
            return self._get_script(style_path)

    def _get_compiled(self, resp):
        """
        Return the result compiled LESS script
        """

        return resp.decode('utf-8')

    def _get_script(self, style_path, ignore=None):
        """
        Return the LESS script and set Application use of LESS compiler
        script as True
        """

        return filepath.FilePath(style_path).getContent().decode('utf-8')


__all__ = ["LessResource", "LessCompiler"]
