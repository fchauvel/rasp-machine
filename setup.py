from setuptools import setup, find_packages

setup(
    name='rasp',
    version='0.1.0',
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
