from setuptools import setup, find_packages

setup(
    name='ohmu',
    version='0.4.2',
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
    tests_require=['nose'],
)
