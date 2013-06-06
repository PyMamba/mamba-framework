#!/usr/bin/env python

# Copyright (c) ${year} - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for details.

"""
Distutils/Setuptools installer for ${application}
"""

import os
import sys

if not hasattr(sys, "version_info") or sys.version_info < (2, 7):
    raise RuntimeError("Mamba requires Python 2.7 or later.")

from setuptools import setup, find_packages, findall

from mamba import version

long_description = '%s\n\n%s' % (
    open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    'For more information about mamba visit the `Mamba website <http://www.pymamba.com>`_'
)

setup(
    name='''${application_name}''',
    version=${version},
    packages=find_packages(),
    include_package_data=True,
    description='''${description}''',
    long_description=long_description,
    author='''${author}''',
    author_email='''${author_email}''',
    license='''${license}''',
    zip_safe=False,
    requires=['mamba(>={})'.format(version.short())],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Mamba',
        'Framework :: Twisted',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        '${license_classifier}',
    ]
)