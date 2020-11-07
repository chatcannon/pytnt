#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-FileCopyrightText: 2014 Christopher Kerr
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os.path

from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
    readme = f.read()

setup(
    name='pytnt',
    version='0.1.0',
    description="Read NMR data files in the TecMag .tnt file format",
    long_description=readme,
    long_description_content_type="text/markdown",
    url='https://github.com/chatcannon/pytnt',
    author='Chris Kerr',
    author_email='chris.kerr@mykolab.ch',
    license='GPLv3+',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering :: Chemistry',
    ],
    packages=['pytnt'],
    entry_points={
        'console_scripts': [
            'find_TNMR_backup_files = pytnt.find_TNMR_backup_files:main',
        ],
    },
    python_requires='>=2.7',
    install_requires=['numpy'],
    tests_require=['pytest'],
)
