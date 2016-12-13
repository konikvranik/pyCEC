FROM resin/armv7hf-debian

VOLUME /tmp/pycec

RUN [ "apt-get", "-y", "install", "python3", "python3-pip", "libcec-dev" ]

RUN [ "pip3", "install", "cec" ]

