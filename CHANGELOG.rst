Change Log
##########

`0.6.0`_ 2024-01-27
*************
Added
=====
- Publicly expose mute and volume status
- New vendor ID mapping for Vizio

Changed
=======
- Base Docker image on balenalib instead of resin

`0.5.2`_ 2022-07-08
*************
Added
=====
- Added Python 3.9 support.
- Added Python 3.10 support.

`0.5.1`_ 2020-10-24
*******************
Fixed
=====
- Fixed a ``TypeError`` exception when using the pyCEC server.

`0.5.0`_ 2020-10-04
*******************
Added
=====
- Added a changelog.
- Added Python 3.8 testing.

Changed
=======
- Updated PyPi classifiers.
- Updated asyncio syntax to use ``await`` and ``async def``.

Removed
=======
- Drop Python 3.4 support (EOL).

Fixed
=====
- Allow ``TcpAdapter`` to recover from a lost connection.
- Added a missing ``await`` for an ``asyncio.sleep``.
- Fixed long_description field for PyPi releases, the README will now render.

`0.4.14`_ 2020-09-27
********************
Changed
=======
- Removed `typing` requirement.

.. _Unreleased: https://github.com/konikvranik/pyCEC/compare/v0.5.1..HEAD
.. _0.5.1: https://github.com/konikvranik/pyCEC/releases/tag/v0.5.1
.. _0.5.0: https://github.com/konikvranik/pyCEC/releases/tag/v0.5.0
.. _0.4.14: https://github.com/konikvranik/pyCEC/releases/tag/v0.4.14
