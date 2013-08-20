#!/usr/bin/python
# coding=utf-8

from distutils.core import setup
import mlite

classifiers = """
Development Status :: 3 - Alpha
Intended Audience :: Science/Research
License :: OSI Approved :: GNU General Public License v3 (GPLv3)
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Topic :: Utilities
Topic :: Scientific/Engineering
Topic :: Scientific/Engineering :: Artificial Intelligence
Topic :: Software Development :: Libraries
Topic :: Software Development :: Quality Assurance
"""


setup(
    name='MLite',
    version=mlite.__version__,
    author='Klaus Greff',
    author_email='qwlouse@gmail.com',
    packages=['mlite', 'mlite.test', 'mlite.observers', 'mlite.pylstm'],
    classifiers=filter(None, classifiers.split('\n')),
    scripts=[],
    url='http://pypi.python.org/pypi/MLizard/',
    license='LICENSE.txt',
    description='Machine Learning orchestration',
    long_description=open('README.rst').read(),
    install_requires=[
        "numpy >= 1.6.1"
    ],
)
