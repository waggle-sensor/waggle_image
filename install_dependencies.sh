#!/bin/bash

set -e
set -x


apt-get install -y htop iotop iftop bwm-ng screen git python-dev python-serial python-pip tree psmisc wvdial dosfstools autossh parted bash-completion fswebcam v4l-utils


# python3

apt-get install -y python3-pip
apt-get install python3-zmq

pip3 install tabulate
