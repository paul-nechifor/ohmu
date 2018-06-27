This repository has been moved to `gitlab.com/paul-nechifor/ohmu <http://gitlab.com/paul-nechifor/ohmu>`_.
==========================================================================================================

Old readme:

Ohmu
====

View space usage in your terminal.

.. image:: https://img.shields.io/travis/paul-nechifor/ohmu.svg?style=flat-square
    :target: https://travis-ci.org/paul-nechifor/ohmu

.. image:: https://img.shields.io/codecov/c/github/paul-nechifor/ohmu.svg?style=flat-square
    :target: https://codecov.io/github/paul-nechifor/ohmu

.. image:: https://img.shields.io/pypi/v/ohmu.svg?style=flat-square
    :target: https://pypi.python.org/pypi/ohmu

.. image:: https://img.shields.io/pypi/dm/ohmu.svg?style=flat-square
    :target: https://pypi.python.org/pypi/ohmu

.. image:: https://img.shields.io/pypi/l/ohmu.svg?style=flat-square
    :target: http://opensource.org/licenses/MIT

.. image:: animation.gif

Usage
-----

Install the Python headers (TODO: specify the commands on every major OS.)

Install (prefix with ``sudo`` if you need to)::

    pip install ohmu --user --upgrade

Scan the current directory::

    ohmu

Scan some random directory::

    ohmu some/random/dir

Development
-----------

Make sure you have Tox_ installed globally.

Run the tests with::

    tox

License
-------

MIT

.. _Tox: https://tox.readthedocs.io/en/latest/
