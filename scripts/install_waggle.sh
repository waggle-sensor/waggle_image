#!/bin/bash

set -e
set -x

# command-line options
declare -r server_host=$1
shift
declare -r branch=$1
shift
repositories=()
while [[ $# -gt 0 ]]; do
  repositories+=("$1")
  shift
done

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
