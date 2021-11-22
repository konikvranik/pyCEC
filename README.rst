|Build Status| |PyPi Version| |Issue Count| |Coverage Status|

``pyCEC``
=========

Purpose of this project is to provide object API to libcec for
home-assistant hdmi\_cec module as `primary
goal <https://github.com/konikvranik/pyCEC/projects/1>`__ and to make
TCP <=> HDMI bridge to control HDMI devices over TCP network as a
`secondary goal <https://github.com/konikvranik/pyCEC/projects/2>`__.

``libcec`` dependency [1]_
--------------------------

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


home-assistant with multiple on/off switches
--------------------------------------------

You can not only add a `hdmi_cec` instance to home-assistant with specified `host` for remote control of your TV, but also add switches for multiple TVs to turn on or off:

.. code-block:: yaml

   switch:
     - platform: telnet
       switches:
         some_device_id:
           name: "Some Device Name"
           resource: xxx.xxx.xxx.xxx
           port: 9526
           command_on: '10:04'
           command_off: '10:36'
           command_state: '10:8f'
           value_template: '{{ value == "01:90:00" }}'
           timeout: 1

.. |PyPi Version| image:: https://img.shields.io/pypi/v/pyCEC
   :target: https://pypi.org/project/pyCEC/
.. |Build Status| image:: https://github.com/konikvranik/pyCEC/workflows/Tests/badge.svg
   :target: https://github.com/konikvranik/pyCEC/actions
.. |Issue Count| image:: https://img.shields.io/github/issues-raw/konikvranik/pyCEC
   :target: https://github.com/konikvranik/pyCEC/issues
.. |Coverage Status| image:: https://img.shields.io/coveralls/github/konikvranik/pyCEC
   :target: https://coveralls.io/github/konikvranik/pyCEC
