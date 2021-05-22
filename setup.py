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


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name=About.NAME,
    version=About.VERSION,
    url="https://github.com/fchauvel/rasp-machine",
    author='Franck Chauvel',
    author_email='franck.chauvel@gmail.com',
    description='Emulator for the RASP machines proposed by Cook & Reckow in 1973',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude='tests'),
    project_urls={
        "Documentation": "https://fchauvel.github.io/rasp-machine",
        "Bug Tracker": "https://github.com/fchauvel/rasp-machine/issues"
    },
    python_requires=">=3.6",
    install_requires=[
        "argparse==1.4.0",
        "pyparsing==2.4.7"
    ],
    extras_require={
          "dev": [
              "build==0.3.1",
              "twine==3.4.1",
              "pytest==6.2.4",
              "coverage==5.5",
              "pyyaml==5.4.1",
          ]
      },
    entry_points={
        'console_scripts': [
            'rasp = rasp.cli:main'
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Assemblers",
        "Topic :: System :: Emulators"
    ],
)
