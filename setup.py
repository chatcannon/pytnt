# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='pytnt',
    version='0.0.2',
    description="Open and process data files from TecMag's .tnt file format",
    url='https://github.com/chatcannon/pytnt',
    author='Chris Kerr',
    license='GPLv3+',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English'],
    packages=['pytnt'],
    scripts=['scripts/find_TNMR_backup_files.py'],  # TODO make this use entry_points
    install_requires=['numpy']
)
