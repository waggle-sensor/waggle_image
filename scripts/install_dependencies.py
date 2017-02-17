#!/usr/bin/python3

import argparse
import commands
import os
import os.path
import shutil
import subprocess
import sys
import time

waggle_image_directory = os.path.dirname(os.path.abspath(__file__))
print("### Run directory for build_image.py: %s" % waggle_image_directory)
sys.path.insert(0, '%s/lib/python/' % waggle_image_directory)
from waggle.build import *

###### TIMING ######
start_time = time.time()
####################

odroid_model = detect_odroid_model()

base_apt_packages = ['htop', 'iotop', 'iftop', 'bwm-ng', 'screen', 'git', 'python-dev', 'python-pip', 'python3-dev', 'python3-pip', 'dosfstools', 'parted',
                 'bash-completion', 'fswebcam', 'v4l-utils', 'network-manager', 'usbutils', 'nano', 'stress-ng']
nc_apt_packages = ['wvdial', 'autossh', 'bossa-cli', 'curl', 'python3-zmq']
ep_apt_packages = ['fswebcam',]

apt_packages = base_apt_packages
if odroid_model == 'odroid-c1':
  apt_packages.extend(nc_apt_packages)
elif odroid_model == 'odroid-xu3':
  apt_packages.extend(ep_apt_packages)

run_command('apt-get install -y ' + ' '.join(packages))

run_command('pip install --upgrade pip')

python2_packages = ['tabulate', 'pika']
nc_python2_packages = ['crcmod', 'pyserial']
ep_python2_packages = []
if odroid_model == 'odroid-c1':
  python2_packages.extend(nc_python2_packages)
elif odroid_model == 'odroid-xu3':
  python2_packages.extend(ep_python2_packages)
run_command('pip install ' + ' '.join(python2_packages))

run_command('pip3 install --upgrade pip')

python3_packages = ['tabulate', 'pika']
nc_python3_packages = ['crcmod', 'pyserial', 'netifaces']
ep_python3_packages = []
if odroid_model == 'odroid-c1':
  python3_packages.extend(nc_python3_packages)
elif odroid_model == 'odroid-xu3':
  python3_packages.extend(ep_python3_packages)
run_command('pip install ' + ' '.join(python3_packages))

#install pika package from the git repo.
# cd nc-wag-os/packages/python/
# pip install -e pika-0.10.0
# pip3 install -e pika-0.10.0

###### TIMING ######
end_time = time.time()
print("Build Duration: %ds" % (end_time - start_time))
####################
