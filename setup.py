import sys
from setuptools import setup, find_packages

install_requires = [
    'future==0.15.2',
]

if sys.version_info[0] == 2:
    install_requires.append('scandir==1.3')

setup(
    name='ohmu',
    version='0.5.0',
    author='Paul Nechifor',
    author_email='paul@nechifor.net',
    description='View space usage in your terminal.',
    packages=find_packages(),
    keywords='space usage',
    long_description=open('README.rst').read(),
    entry_points={'console_scripts': ['ohmu=ohmu:entry_point']},
    license='MIT',
    url='http://github.com/paul-nechifor/ohmu',
    test_suite='nose.collector',
    tests_require=[
        'nose==1.3.7',
        'mock==1.0.1',
    ],
    install_requires=install_requires,
)
