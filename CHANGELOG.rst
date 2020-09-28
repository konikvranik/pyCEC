Change Log
##########

`Unreleased`_
*************
Added
=====
- Added a changelog.
- Added Python 3.8 testing.

Changed
=======
- Updated PyPi classifiers.
- Updated asyncio syntax to use ``await`` and ``async def``.

Deprecated
==========

Removed
=======
- Drop Python 3.4 support (EOL).

Fixed
=====
- Allow ``TcpAdapter`` to recover from a lost connection.
- Added a missing ``await`` for an ``asyncio.sleep``.
- Fixed long_description field for PyPi releases, the README will now render.

Security
========

`0.4.14`_ 2020-09-27
********************
Changed
=======
- Removed `typing` requirement.

.. _Unreleased: https://github.com/konikvranik/pyCEC/compare/v0.4.14..HEAD
.. _0.4.14: https://github.com/konikvranik/pyCEC/releases/tag/v0.4.14
