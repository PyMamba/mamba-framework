#!/usr/bin/env python

# Copyright (c) ${year} - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for details.

"""
Distutils/Setuptools installer for ${application}
"""

import sys
from setuptools import setup, find_packages

from mamba import version

long_description = '''
${description}

For more information visit the `Mamba website <http://www.pymamba.com>`_
'''

setup(
    name='${application}',
    version=version.short(),
    description='${description}',
    author='${author}',
    author_email='${author_email}',
    packages=find_packages(),
    package_data={'${application_name}': [
        'static/*',
        'application/config/*.json',
        'application/view/*'
    ]},
    requires=['mamba>={}'.format(version.short())],
    entry_points=${entry_points}
)