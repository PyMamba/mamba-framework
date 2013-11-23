#!/usr/bin/env python

# Copyright (c) 2012 - 2013 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for details.

"""
Distutils installer for Mamba.
"""

import sys
if not hasattr(sys, "version_info") or sys.version_info < (2, 7):
    raise RuntimeError("Mamba requires Python 2.7 or later.")

from setuptools import setup, find_packages


def get_mamba_version():
    with open('mamba.ver', 'r') as mamba_ver_file:
        mamba_ver = mamba_ver_file.read()

    return mamba_ver.strip()

long_description = '''
This is a new release of Mamba the web applications framework for Twisted. Read
the `relnotes <https://github.com/DamnWidget/mamba/blob/master/docs/relnotes/
{}.rst>`_ to know more about this specific Mamba release.

If you like to live at the edge, you can also install the in-development
version <https://github.com/DamnWidget/mamba.git>

For more information visit the `Mamba website <http://www.pymamba.com>`_
'''.format(get_mamba_version())

setup(
    name='mamba-framework',
    version=get_mamba_version(),
    description=('Mamba is a high-level RAD Web Applications framework '
                 'based on Twisted Web that uses Storm ORM as database '
                 'access layer'),
    long_description=long_description,
    author='Oscar Campos',
    author_email='oscar.campos@member.fsf.org',
    url='http://www.pymamba.com',
    license='GPL',
    packages=find_packages(),
    package_data={'mamba': [
        'templates/*.tpl',
        'templates/jinja/*',
        'test/application/config/*.json',
        'test/application/view/stylesheets/*.css',
        'test/application/view/stylesheets/*.less'
    ]},
    tests_require=['twisted>=10.2.0', 'doublex', 'PyHamcrest'],
    install_requires=[
        'twisted>=10.2.0', 'storm>=0.19', 'jinja2>=2.4', 'singledispatch'],
    requires=[
        'twisted(>=10.2.0)', 'storm(>=0.19)', 'zope.component', 'transaction',
        'jinja2(>=2.4)', 'singledispatch'
    ],
    entry_points={
        'console_scripts': [
            'mamba-admin = mamba.scripts.mamba_admin:run',
        ]
    },
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Twisted',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: System :: Networking',
    ],
)
