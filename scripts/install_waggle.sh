#!/bin/bash

set -e
set -x

# Detect the Odroid model. This yields either ODROIDC or ODROID-XU3.
declare -r odroid_model=$(cat /proc/cpuinfo | grep Hardware | grep -o "[^ ]*$")

declare -r base_repositories=("core" "plugin_manager")
declare -r nc_repositories=(" nodecontroller")
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

for repository in ${repositories[@]}; do
  cd /usr/lib/waggle
  git clone https://github.com/waggle-sensor/${repository}.git
  cd /usr/lib/waggle/${repository}
  ./configure --system
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
