#!/bin/bash

set -e
set -x


apt-get install -y htop iotop iftop bwm-ng screen git python-dev python-serial python-pip tree psmisc wvdial dosfstools autossh parted bash-completion fswebcam v4l-utils


# python3

apt-get install -y python3-pip

pip3 install tabulate
pip3 install pyzmq
