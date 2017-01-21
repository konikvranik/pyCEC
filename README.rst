|Build Status| |CodeShip| |Code Climate| |Test Coverage| |Issue Count|
|Coverage Status|

``pyCEC``
=====

Purpose of this project is to provide object API to libcec for
home-assistant hdmi\_cec module as `primary
goal <https://github.com/konikvranik/pyCEC/projects/1>`__ and to make
TCP <=> HDMI bridge to control HDMI devices over TCP network as a
`secondary goal <https://github.com/konikvranik/pyCEC/projects/2>`__.

``libcec`` dependency [1]_
---------------------

`libcec <https://github.com/Pulse-Eight/libcec>`__ must be installed [2]_ for
this module to work in direct mode. Follow the installation instructions
for your environment, provided at the link.  ``libcec`` installs Python 3
bindings by default as a system Python module. If you are running ``pyCEC`` in a *Python virtual
environment*, make sure it
can access the system module, by either symlinking it or using the
``--system-site-packages`` flag.

.. [1] \:bulb: When using ``pyCEC`` as a network client, ``libcec`` is not needed.
.. [2] \:warning: Do not use ``pip3 install cec``. This will fail. `Compile <https://github.com/Pulse-Eight/libcec#supported-platforms>`__ ``libcec`` instead.

running server
--------------

You can run ``pyCEC`` server which will provide bridge between HDMI CEC port
and TCP network by exexcuting ``python3 -m pycec``. Server will bind to
default port ``9526`` on all interfaces.

Then you can connect by client part of ``pyCEC`` without need of libcec or
HDMI port on client's machine. Just use ``TcpAdapter`` instead of
``CecAdapter``.

You can also connect to ``9526`` by `NetCat <https://www.wikiwand.com/en/Netcat>`_ and send CEC commands directly.

.. |Build Status| image:: https://travis-ci.org/konikvranik/pyCEC.svg?branch=dev
   :target: https://travis-ci.org/konikvranik/pyCEC
.. |CodeShip| image:: https://codeship.com/projects/7e847d60-a377-0134-e221-0a9a91773973/status?branch=dev
   :target: https://app.codeship.com/projects/190270
.. |Code Climate| image:: https://codeclimate.com/github/konikvranik/pyCEC/badges/gpa.svg
   :target: https://codeclimate.com/github/konikvranik/pyCEC
.. |Test Coverage| image:: https://codeclimate.com/github/konikvranik/pyCEC/badges/coverage.svg
   :target: https://codeclimate.com/github/konikvranik/pyCEC/coverage
.. |Issue Count| image:: https://codeclimate.com/github/konikvranik/pyCEC/badges/issue_count.svg
   :target: https://codeclimate.com/github/konikvranik/pyCEC
.. |Coverage Status| image:: https://coveralls.io/repos/github/konikvranik/pyCEC/badge.svg?branch=dev
   :target: https://coveralls.io/github/konikvranik/pyCEC?branch=dev
