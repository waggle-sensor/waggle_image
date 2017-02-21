#!/bin/bash

set -e

apt-get update
apt-key update

# Detect the Odroid model. This yields either ODROIDC or ODROID-XU3.
declare -r odroid_model=$(cat /proc/cpuinfo | grep Hardware | grep -o "[^ ]*$")

# Define Ubuntu package dependencies
declare -r base_apt_packages=("htop" "iotop" "iftop" "bwm-ng" "screen" "git" "python-dev" "python-pip" "python3-dev" "python3-pip" "dosfstools"
                              "parted" "bash-completion" "fswebcam" "v4l-utils" "network-manager" "usbutils" "nano" "stress-ng")
declare -r nc_apt_packages=(" wvdial" "autossh" "bossa-cli" "curl" "python3-zmq")
declare -r ep_apt_packages=(" fswebcam")

# Define Python 2 package dependencies
declare -r base_python2_packages=("tabulate" "pika")
declare -r nc_python2_packages=(" crcmod" "pyserial")
declare -r ep_python2_packages=""

# Define Python 3 package dependencies
declare -r base_python3_packages=("tabulate" "pika")
declare -r nc_python3_packages=(" crcmod" "pyserial" "netifaces")
declare -r ep_python3_packages=""

# Assemble dependencies for the particular Odroid on which this is running.
apt_packages=${base_apt_packages[@]}
python2_packages=${base_python2_packages[@]}
python3_packages=${base_python3_packages[@]}
if [ "${odroid_model}" == "ODROIDC" ]; then
  apt_packages+=${nc_apt_packages[@]}
  python2_packages+=${nc_python2_packages[@]}
  python3_packages+=${nc_python3_packages[@]}
elif [ "${droid_model}" == "ODROID-XU3" ]; then
  apt_packages+=${ep_apt_packages[@]}
  python2_packages+=${ep_python2_packages[@]}
  python3_packages+=${ep_python3_packages[@]}
elif [ "x${odroid_model}" == "x" ]; then
  echo "Error: no Odroid model detected. This script must be run on an Odroid C1+ or XU4."
  exit 1
else
  echo "Error: unrecognized Odroid model '${odroid_model}'."
  exit 2
fi

# Install Ubuntu package dependencies.
echo "Installing the following Ubuntu packages:\n${apt_packages}"
apt-get install -y ${apt_packages[@]}
 

# Install Python 2 package dependencies.
echo "Installing the following Python 2 packages:\n${python2_packages}"
pip install --upgrade pip
pip install ${python2_packages[@]}


# Install Python 3 package dependencies.
echo "Installing the following Python 3 packages:\n${python3_packages}"
pip3 install --upgrade pip
pip3 install ${python3_packages[@]}
