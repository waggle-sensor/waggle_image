#!/bin/bash

set -e
set -x

# yields either ODROIDC or ODROID-XU3
declare -r odroid_model=$(cat /proc/cpuinfo | grep Hardware | grep -o "[^ ]*$")

# install Ubuntu package dependencies
declare -r base_apt_packages=("htop" "iotop" "iftop" "bwm-ng" "screen" "git" "python-dev" "python-pip" "python3-dev" "python3-pip" "dosfstools"
                              "parted" "bash-completion" "fswebcam" "v4l-utils" "network-manager" "usbutils" "nano" "stress-ng")
declare -r nc_apt_packages=(" wvdial" "autossh" "bossa-cli" "curl" "python3-zmq")
declare -r ep_apt_packages=(" fswebcam")

apt_packages=${base_apt_packages[@]}
if [ "${odroid_model}" == "ODROIDC" ]; then
  apt_packages+=${nc_apt_packages[@]}
elif [ "${droid_model}" == "ODROID-XU3" ]; then
  apt_packages+=${ep_apt_packages[@]}
else
fi

apt-get install -y ${apt_packages[@]}
 

# install Python 2 package dependencies
pip install --upgrade pip
 
python2_packages=("tabulate" "pika")
nc_python2_packages=(" crcmod" "pyserial")
ep_python2_packages=""
python2_packages=${base_apt_packages[@]}
if [ "${odroid_model}" == "ODROIDC" ]; then
  python2_packages+=${nc_python2_packages[@]}
elif [ "${droid_model}" == "ODROID-XU3" ]; then
  python2_packages+=${ep_python2_packages[@]}
fi

pip install ${python2_packages[@]}


# install Python 3 package dependencies
pip3 install --upgrade pip

python3_packages=("tabulate" "pika")
nc_python3_packages=(" crcmod" "pyserial" "netifaces")
ep_python3_packages=""
python3_packages=${base_apt_packages[@]}
if [ "${odroid_model}" == "ODROIDC" ]; then
  python3_packages+=${nc_python3_packages[@]}
elif [ "${droid_model}" == "ODROID-XU3" ]; then
  python3_packages+=${ep_python3_packages[@]}
fi
pip3 install ${python3_packages[@]}
