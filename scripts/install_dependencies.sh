#!/bin/bash

set -e

# command-line options
declare -r dependencies_string=$1

# Parse dependency string
apt_packages=()
python2_packages=()
python3_packages=()
deb_packages=()
dependency_strings=(${dependencies_string//,/ })
for dependency_string in ${dependency_strings[*]}; do
  dependency_tuple=(${dependency_string//:/ })
  dependency=${dependency_tuple[0]}
  dependency_type=${dependency_tuple[1]}
  if [ "$dependency_type" == "apt" ]; then
    apt_packages="${apt_packages} $dependency"
  elif [ "$dependency_type" == "python2" ]; then
    python2_packages="${python2_packages} $dependency"
  elif [ "$dependency_type" == "python3" ]; then
    python3_packages="${python3_packages} $dependency"
  elif [ "$dependency_type" == "deb" ]; then
    deb_packages="${deb_packages} $dependency"
  fi
done

echo "APT packages: ${apt_packages[*]}"
echo "Python 2 packages: ${python2_packages[*]}"
echo "Python 3 packages: ${python3_packages[*]}"
echo "Debian packages: ${deb_packages[*]}"

declare -r script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export LC_ALL=C

echo 'deb http://www.rabbitmq.com/debian/ testing main' | tee /etc/apt/sources.list.d/rabbitmq.list
apt-key add /root/rabbitmq-release-signing-key.asc
# wget -O- https://www.rabbitmq.com/rabbitmq-release-signing-key.asc | apt-key add -


apt-get update
apt-key update



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
cd ${script_dir}/../var/cache/apt/archives
dpkg -i ${deb_packages[@]}

apt update
apt install -f
apt autoremove
