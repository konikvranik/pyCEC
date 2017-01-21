[![Build Status](https://travis-ci.org/konikvranik/pyCEC.svg?branch=dev)](https://travis-ci.org/konikvranik/pyCEC)
[![CodeShip](https://codeship.com/projects/7e847d60-a377-0134-e221-0a9a91773973/status?branch=dev)](https://app.codeship.com/projects/190270)
[![Code Climate](https://codeclimate.com/github/konikvranik/pyCEC/badges/gpa.svg)](https://codeclimate.com/github/konikvranik/pyCEC)
[![Test Coverage](https://codeclimate.com/github/konikvranik/pyCEC/badges/coverage.svg)](https://codeclimate.com/github/konikvranik/pyCEC/coverage)
[![Issue Count](https://codeclimate.com/github/konikvranik/pyCEC/badges/issue_count.svg)](https://codeclimate.com/github/konikvranik/pyCEC)
[![Coverage Status](https://coveralls.io/repos/github/konikvranik/pyCEC/badge.svg?branch=dev)](https://coveralls.io/github/konikvranik/pyCEC?branch=dev)


pyCEC
=====


Purpose of this project is to provide object API to libcec for home-assistant hdmi_cec module as [primary goal](https://github.com/konikvranik/pyCEC/projects/1)
and to make TCP <=> HDMI bridge to control HDMI devices over TCP network as a [secondary goal](https://github.com/konikvranik/pyCEC/projects/2).


`libcec` dependency
-----------------

[libcec](https://github.com/Pulse-Eight/libcec) must be installed for this module to work in direct mode. Follow the installation instructions for your environment, provided at the link. `libcec` installs Python 3 bindings by default as a system Python module. If you are running Home Assistant in a [Python virtual environment](/getting-started/installation-virtualenv/), make sure it can access the system module, by either symlinking it or using the `--system-site-packages` flag.

When using as network client, libcec is not needed.

running server
--------------

You can run pyCEC server which will provide bridge between HDMI CEC port and TCP network by exexcuting `python3 -m pycec`.
Server will bind to default port `9526` on all interfaces.

Then you can connect by client part of pyCEC without need of libcec or HDMI port on client's machine.
Just use `TcpAdapter` instead of `CecAdapter`.



