#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of `cron-wrapper` utility released under the MIT license.
# See the LICENSE file for more information.

from setuptools import setup, find_packages
DESCRIPTION = ("A cron job wrapper to add some missing features (locks, "
               "timeouts, random sleeps, env loading...")
LONG_DESCRIPTION = DESCRIPTION

with open('pip-requirements.txt') as reqs:
    install_requires = [
        line for line in reqs.read().split('\n')
        if (line and not line.startswith('--'))
    ]

setup(
    name='cron-wrapper',
    version="0.1.0",
    author="Fabien MARTY",
    author_email="fabien.marty@gmail.com",
    url="https://github.com/metwork-framework/cron-wrapper",
    packages=find_packages(),
    license='MIT',
    download_url='https://github.com/metwork-framework/cron-wrapper',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Communications',
        'Topic :: Scientific/Engineering :: Atmospheric Science',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Software Development',
        'Topic :: System :: Distributed Computing',
        'Topic :: Utilities',
    ],
    entry_points={
        'console_scripts': [
            'cronwrap = cronwrapper.cronwrap:main',
        ],
    },
)
