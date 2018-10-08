#!/bin/bash

set +e

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

echo ${apt_packages[*]} | grep rabbitmq
if [ $? -eq 0 ]; then
  echo 'deb http://www.rabbitmq.com/debian/ testing main' | tee /etc/apt/sources.list.d/rabbitmq.list
  if [ -e /root/rabbitmq-release-signing-key.asc ]; then
    apt-key add /root/rabbitmq-release-signing-key.asc
  else
    wget -O- https://www.rabbitmq.com/rabbitmq-release-signing-key.asc | apt-key add -
  fi
fi

set -e

apt-get update
apt-key update




# Install Ubuntu package dependencies.
if [ "x" == "x${apt_packages[*]}" ]; then
  echo "No APT packages specified. Skipping apt operation."
else
  echo "Installing the following Ubuntu packages: ${apt_packages[@]}"
  apt install -y ${apt_packages[@]}
fi
 

# Install Python 2 package dependencies.
if [ "x" == "x${python2_packages[*]}" ]; then
  echo "No Python 2 packages specified. Skipping pip operation."
else
  echo "Installing the following Python 2 packages: ${python2_packages[@]}"
  #pip install --upgrade pip==9.0.3
  pip install --upgrade pip
  pip install ${python2_packages[@]}
fi


# Install Python 3 package dependencies.
if [ "x" == "x${python3_packages[*]}" ]; then
  echo "No Python 3 packages specified. Skipping pip3 operation."
else
  echo "Installing the following Python 3 packages: ${python3_packages[@]}"
  #pip3 install --upgrade pip==9.0.3
  pip3 install --upgrade pip
  cd ${script_dir}/../var/cache/pip3/archives
  pip3 install ${python3_packages[@]}
fi

# Install Debian package dependencies.
if [ "x" == "x${deb_packages[*]}" ]; then
  echo "No Debian packages specified. Skipping dpkg operation."
else
  echo "Installing the following Debian packages: ${deb_packages[@]}"
  cd ${script_dir}/../var/cache/apt/archives
  dpkg -i ${deb_packages[@]}
fi

apt update
apt install -f
apt autoremove
