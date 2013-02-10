
# Copyright (c) 2012 - 2013 Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
Tests for mamba.core.templating
"""

import os

from twisted.trial import unittest

from mamba.core.templating import MambaTemplate, Template
from mamba.test.dummy_app.application.controller.dummy import DummyController
from mamba.core.templating import TemplateNotFound, NotConfigured


class MambaTemplateTest(unittest.TestCase):

    def test_mamba_template(self):
        mamba_template = MambaTemplate(template='test.html')
        self.assertEqual(
            mamba_template.render(
                title='Dummy Test',
                content='Dummy'
            ),
            u'<!DOCTYPE html>\n'
            '<html lang="en">\n'
            '<head>\n'
            '    <title>Dummy Test</title>\n'
            '</head>\n'
            '<body>\n'
            '    Dummy\n'
            '</body>\n'
            '</html>'
        )

    def test_mamba_template_raise_templatenotfound(self):
        mamba_template = MambaTemplate(template='fail.html')
        self.assertRaises(TemplateNotFound, mamba_template.render)

    def test_mamba_template_raise_notconfigured(self):
        mamba_template = MambaTemplate()
        self.assertRaises(NotConfigured, mamba_template.render)

    def test_mamba_template_not_escaped(self):
        mamba_template = MambaTemplate(template='fail.html')
        self.assertFalse(mamba_template.env.autoescape)


class TemplateTest(unittest.TestCase):

    def setUp(self):
        self.currdir = os.getcwd()
        os.chdir('../mamba/test/dummy_app')

        self.template = Template(cache_size=0)

    def tearDown(self):
        os.chdir(self.currdir)

    def test_template_without_controller(self):

        self.assertEqual(
            self.template.render_template(
                'dummy.html',
                title='Dummy Test',
                content='Dummy'
            ),
            u'<!DOCTYPE html>\n'
            '<html lang="en">\n'
            '<head>\n'
            '    <title>Dummy Test</title>\n'
            '</head>\n'
            '<body>\n'
            '    Dummy\n'
            '</body>\n'
            '</html>'
        )

    def test_template_with_controller_and_not_existent_template(self):

        dummy = DummyController()
        self.template.controller = dummy
        self.assertEqual(
            self.template.render_template(
                'dummy_test.html',
                title='Dummy Test',
                content='Dummy'
            ),
            u'<!DOCTYPE html>\n'
            '<html lang="en">\n'
            '<head>\n'
            '    <title>Dummy Test Controller</title>\n'
            '</head>\n'
            '<body>\n'
            '    Dummy\n'
            '</body>\n'
            '</html>'
        )

    def test_template_with_controller_and_not_template_argument(self):

        def dummy_test(self):
            return Template(self).render_template(
                title='Dummy Test', content='Dummy')

        dummy = DummyController()
        dummy.dummy_test = dummy_test
        self.assertEqual(
            dummy.dummy_test(dummy),
            u'<!DOCTYPE html>\n'
            '<html lang="en">\n'
            '<head>\n'
            '    <title>Dummy Test Controller</title>\n'
            '</head>\n'
            '<body>\n'
            '    Dummy\n'
            '</body>\n'
            '</html>'
        )

    def test_template_with_template_arg_on_render_hides_controller(self):

        def dummy_test2(self):
            return Template(self, cache_size=0).render_template(
                template='dummy_test2.html')

        dummy = DummyController()
        dummy.dummy_test2 = dummy_test2
        self.assertEqual(dummy.dummy_test2(dummy), 'HIDDEN!')

    def test_template_raises_templatenotfound_on_non_existent(self):
        self.assertRaises(
            TemplateNotFound,
            self.template.render_template, 'fail.html'
        )

    def test_template_raises_notconfigured_when_no_arguments(self):
        self.assertRaises(
            NotConfigured,
            self.template.render_template
        )
