#!/bin/bash

set -e
set -x

# command-line options
declare -r branch=$1
declare -r server_host=$2

# Detect the Odroid model. This yields either ODROIDC or ODROID-XU3.
if [ "x${ODROID_MODEL}" == "x" ]; then
  declare -r odroid_model=$(cat /proc/cpuinfo | grep Hardware | grep -o "[^ ]*$")
else
  declare -r odroid_model=${ODROID_MODEL}
fi

declare -r base_repositories=("core")
declare -r nc_repositories=(" nodecontroller"  "plugin_manager")
declare -r ep_repositories=(" edge_processor")

repositories=${base_repositories[@]}
if [ "${odroid_model}" == "ODROIDC" ]; then
  repositories+=${nc_repositories[@]}
elif [ "${odroid_model}" == "ODROID-XU3" ]; then
  repositories+=${ep_repositories[@]}
elif [ "x${odroid_model}" == "x" ]; then
  echo "Error: no Odroid model detected. This script must be run on an Odroid C1+ or XU4."
  exit 1
else
  echo "Error: unrecognized Odroid model '${odroid_model}'."
  exit 2
fi

mkdir -p /usr/lib/waggle

for repository in ${repositories[@]}; do
  cd /usr/lib/waggle
  if [ "x${branch}" == "x" ]; then
  	git clone https://github.com/waggle-sensor/${repository}.git
  else
  	git clone -b ${branch} https://github.com/waggle-sensor/${repository}.git
  fi
  cd /usr/lib/waggle/${repository}
  ./configure --system --server-host=${server_host}
done

echo root:waggle | chpasswd

### create report
report_file="/root/report.txt"
echo "Image created on $(date)." > ${report_file}
echo "" >> ${report_file}
uname -a >> ${report_file}
echo "" >> ${report_file}
cat /etc/os-release >> ${report_file}
dpkg -l >> ${report_file}
