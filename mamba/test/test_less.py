
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
Tests for mamba.utils.less
"""

import os
import tempfile

from twisted.web import server
from twisted.trial import unittest
from twisted.python import filepath
from twisted.internet import utils, defer
from twisted.web.test.test_web import DummyRequest

from mamba.utils import less


less_file = (
    '#functions {\n'
    '  @var: 10;\n'
    '  color: _color("evil red"); // #660000\n'
    '  width: increment(15);\n'
    '  height: undefined("self");\n'
    '  border-width: add(2, 3);\n'
    '  variable: increment(@var);\n'
    '}\n'
    '\n'

    '#built-in {\n'
    '  @r: 32;\n'
    '  escaped: e("-Some::weird(#thing, y)");\n'
    '  lighten: lighten(#ff0000, 40%);\n'
    '  darken: darken(#ff0000, 40%);\n'
    '  saturate: saturate(#29332f, 20%);\n'
    '  desaturate: desaturate(#203c31, 20%);\n'
    '  greyscale: greyscale(#203c31);\n'
    '  spin-p: spin(hsl(340, 50%, 50%), 40);\n'
    '  spin-n: spin(hsl(30, 50%, 50%), -40);\n'
    '  format: %("rgb(%d, %d, %d)", @r, 128, 64);\n'
    '  format-string: %("hello %s", "world");\n'
    '  format-multiple: %("hello %s %d", "earth", 2);\n'
    '  format-url-encode: %(\'red is %A\', #ff0000);\n'
    '  eformat: e(%("rgb(%d, %d, %d)", @r, 128, 64));\n'
    '\n'
    '  hue: hue(hsl(98, 12%, 95%));\n'
    '  saturation: saturation(hsl(98, 12%, 95%));\n'
    '  lightness: lightness(hsl(98, 12%, 95%));\n'
    '  rounded: round(@r/3);\n'
    '  roundedpx: round(10px / 3);\n'
    '  percentage: percentage(10px / 50);\n'
    '  color: color("#ff0011");\n'
    '\n'
    '  .is-a {\n'
    '    color: iscolor(#ddd);\n'
    '    color: iscolor(red);\n'
    '    color: iscolor(rgb(0, 0, 0));\n'
    '    keyword: iskeyword(hello);\n'
    '    number: isnumber(32);\n'
    '    string: isstring("hello");\n'
    '    pixel: ispixel(32px);\n'
    '    percent: ispercentage(32%);\n'
    '    em: isem(32em);\n'
    '  }\n'
    '}\n'
    '\n'
    '#alpha {\n'
    '  alpha: darken(hsla(25, 50%, 50%, 0.6), 10%);\n'
    '}\n'
)


class LessCompilerTests(unittest.TestCase):
    """
    Tests for L{mamba.utils.less}
    """

    def setUp(self):
        self.file = tempfile.NamedTemporaryFile(delete=False)
        self.file.write(less_file)
        self.file.close()

        self._fp = filepath.FilePath(self.file.name)

    def tearDown(self):
        self.flushLoggedErrors()
        self._fp.remove()

    @defer.inlineCallbacks
    def test_less_compiles(self):
        try:
            result = yield utils.getProcessOutput('lessc', [''], os.environ)
        except utils._UnexpectedErrorOutput:
            raise unittest.SkipTest('lessc is not available')
        except Exception as error:
            raise unittest.SkipTest(error)

        lc = less.LessCompiler(self.file.name)
        result = yield lc.compile()

        self.assertNotEqual(result, less_file)

    @defer.inlineCallbacks
    def test_less_compile_to_css(self):

        try:
            result = yield utils.getProcessOutput(
                'lessc', [self.file.name], os.environ)
            lc = less.LessCompiler(self.file.name)
            retval = yield lc.compile()

            self.assertEqual(retval, result)
        except utils._UnexpectedErrorOutput:
            raise unittest.SkipTest('lessc is not available')
        except Exception as error:
            raise unittest.SkipTest(error)

    @defer.inlineCallbacks
    def test_less_compile_fallbacks(self):

        def _get_script(self, ignore):
            return filepath.FilePath(self.stylesheet).getContent().decode(
                'utf-8'
            )

        # Monkeypatch to avoid unclean reactor state from mamba.app
        self.patch(less.LessCompiler, '_get_script', _get_script)
        lc = less.LessCompiler(self.file.name, exe='lessc-fail')

        retval = yield lc.compile()

        self.assertEqual(
            filepath.FilePath(self.file.name).getContent().decode('utf-8'),
            retval
        )

        self.flushLoggedErrors()


class LessResourceTest(unittest.TestCase):
    """
    Tests for mamba.utils.less.LessResource
    """

    def setUp(self):
        self.r = less.LessResource()
        self.fd = tempfile.NamedTemporaryFile(delete=False)
        self.fd.write(less_file)
        self.fd.close()
        self._fp = filepath.FilePath(self.fd.name)

    def tearDown(self):
        self.flushLoggedErrors()
        self._fp.remove()

    def test_is_leaf(self):
        self.assertTrue(self.r.isLeaf)

    @defer.inlineCallbacks
    def test_render(self):
        request = DummyRequest([self.fd.name])

        def _get_script(self, ignore):
            return filepath.FilePath(self.stylesheet).getContent().decode(
                'utf-8'
            )

        # Monkeypatch to avoid unclean reactor state from mamba.app
        self.patch(less.LessCompiler, '_get_script', _get_script)
        result = yield self._render(self.r, request)
        result = ''.join(result.written)
        lc = less.LessCompiler(self.fd.name)
        retval = yield lc.compile()

        self.assertEqual(retval, result)

    def _render(self, resource, request):
        result = resource.render(request)
        if isinstance(result, str):
            request.write(result)
            request.finish()
            return defer.succeed(request)
        elif result is server.NOT_DONE_YET:
            if request.finished:
                return defer.succeed(request)
            else:
                return request.notifyFinish().addCallback(lambda _: request)
        else:
            raise ValueError("Unxpected return value: {0}".format(result))
