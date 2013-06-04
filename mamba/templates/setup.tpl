#!/usr/bin/env python

# Copyright (c) ${year} - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for details.

"""
Distutils/Setuptools installer for ${application}
"""

import os
import sys
from setuptools import setup, find_packages, findall

from mamba import version

long_description = '''
${description}

For more information visit the `Mamba website <http://www.pymamba.com>`_
'''

data = ${data}
data += ['README', 'README.*', 'LICENSE', 'LICENSE.*', '.mamba-package']
os.chdir('${application}')
data += findall('static') + findall('application/view') + findall('config')
os.chdir('..')


setup(
    name='''${application_name}''',
    version=${version},
    description='''${description}''',
    long_description=long_description,
    author='''${author}''',
    author_email='''${author_email}''',
    license='GPL',
    packages=find_packages(),
    package_data={'${application}': data},
    requires=['mamba(>={})'.format(version.short())],
    entry_points=${entry_points},
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Framework :: Twisted',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ]
)