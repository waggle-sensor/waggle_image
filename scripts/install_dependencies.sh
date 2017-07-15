#!/bin/bash

set -e

declare -r script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Detect the Odroid model. This yields either ODROIDC or ODROID-XU3.
if [ "x${ODROID_MODEL}" == "x" ]; then
  declare -r odroid_model=$(cat /proc/cpuinfo | grep Hardware | grep -o "[^ ]*$")
else
  declare -r odroid_model=${ODROID_MODEL}
fi

export LC_ALL=C

echo 'deb http://www.rabbitmq.com/debian/ testing main' | tee /etc/apt/sources.list.d/rabbitmq.list
wget -O- https://www.rabbitmq.com/rabbitmq-release-signing-key.asc | apt-key add -

apt-get update
apt-key update

# Define Ubuntu package dependencies
declare -r base_apt_packages=("htop" "iotop" "iftop" "bwm-ng" "screen" "git" "python-dev" "python-pip"
                              "python3-dev" "python3-pip" "dosfstools" "parted" "bash-completion"
                              "v4l-utils" "network-manager" "usbutils" "nano" "stress-ng" "rabbitmq-server"
                              "python-psutil" "python3-psutil")
declare -r nc_apt_packages=(" wvdial" "autossh" "bossa-cli" "curl" "python3-zmq")
declare -r ep_apt_packages=(" fswebcam" "alsa-utils" "portaudio19-dev" "libavcodec-ffmpeg56" "libavformat-ffmpeg56" "libavutil-ffmpeg54" "libc6" "libcairo2" "libgdk-pixbuf2.0-0" "libglib2.0-0" "libgtk-3-0" "libpng12-0" "libstdc++6" "libswscale-ffmpeg3" "zlib1g")


# Define Python 2 package dependencies
declare -r base_python2_packages=("tabulate" "pika")
declare -r nc_python2_packages=(" crcmod" "pyserial")
declare -r ep_python2_packages=(" numpy")

# Define Python 3 package dependencies
declare -r base_python3_packages=("tabulate" "pika")
declare -r nc_python3_packages=(" crcmod" "pyserial" "netifaces" "pyzmq" "pyinotify" "pynmea2")
declare -r ep_python3_packages=(" pyaudio" "numpy")

# Define Debian package dependencies
declare -r arch=`uname -m`
declare -r base_deb_packages=
declare -r nc_deb_packages=
#declare -r ep_deb_packages=(" OpenCV-unknown-${arch}-dev.deb" "OpenCV-unknown-${arch}-main.deb" "OpenCV-unknown-${arch}-samples.deb" "OpenCV-unknown-${arch}-libs.deb" "OpenCV-unknown-${arch}-python.deb")
declare -r ep_deb_packages=(" OpenCV-dev" "OpenCV-main" "OpenCV-samples" "OpenCV-libs" "OpenCV-python")

# Assemble dependencies for the particular Odroid on which this is running.
apt_packages=${base_apt_packages[@]}
python2_packages=${base_python2_packages[@]}
python3_packages=${base_python3_packages[@]}
deb_packages=${base_deb_packages[@]}
if [ "${odroid_model}" == "ODROIDC" ]; then
  apt_packages+=${nc_apt_packages[@]}
  python2_packages+=${nc_python2_packages[@]}
  python3_packages+=${nc_python3_packages[@]}
  deb_packages+=${nc_deb_packages[@]}
elif [ "${odroid_model}" == "ODROID-XU3" ]; then
  apt_packages+=${ep_apt_packages[@]}
  python2_packages+=${ep_python2_packages[@]}
  python3_packages+=${ep_python3_packages[@]}
  deb_packages+=${ep_deb_packages[@]}
elif [ "x${odroid_model}" == "x" ]; then
  echo "Error: no Odroid model detected. This script must be run on an Odroid C1+ or XU4."
  exit 1
else
  echo "Error: unrecognized Odroid model '${odroid_model}'."
  exit 2
fi

# Install Ubuntu package dependencies.
echo "Installing the following Ubuntu packages: ${apt_packages[@]}"
apt-get install -y ${apt_packages[@]}
 

# Install Python 2 package dependencies.
echo "Installing the following Python 2 packages: ${python2_packages[@]}"
pip install --upgrade pip
pip install ${python2_packages[@]}


# Install Python 3 package dependencies.
echo "Installing the following Python 3 packages: ${python3_packages[@]}"
pip3 install --upgrade pip
pip3 install ${python3_packages[@]}

# Install Debian package dependencies.
echo "Installing the following Debian packages: ${deb_packages[@]}"
cp ${script_dir}/var/cache/apt/archives/*.deb /var/cache/apt/archives
dpkg -i ${deb_packages[@]}
apt update
apt install -f
apt autoremove
