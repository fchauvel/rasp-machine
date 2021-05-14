#
# This file is part of rasp-machine.
#
# Copyright (C) 2021 by Franck Chauvel
#
# This code is licensed under the MIT License.
# See LICENSE.txt for details
#


from rasp import About

from setuptools import setup, find_packages

setup(
    name=About.NAME,
    version=About.VERSION,
    url='https://github.com/fchauvel/rasp.git',
    author='Franck Chauvel',
    author_email='franck.chauvel@gmail.com',
    description='Emulator for the RASP machine proposed by Cook & Reckow in 1973',
    packages=find_packages(exclude='tests'),
    install_requires=[],
    tests_require=[],
    entry_points={
        'console_scripts': [
            'rasp = rasp.cli:main'
        ]
    }
)
