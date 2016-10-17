#!/bin/bash

set -e
set -x

apt-get update
apt-key update

cd /usr/lib/waggle
repos=$(ls --color=never -1 -d */)
for repo in $repos; do
  cd $repo
  ./configure --system
  cd /usr/lib/waggle
done

### create report
report_file="/root/report.txt"
echo "image created: " > ${report_file}
date >> ${report_file}
echo "" >> ${report_file}
uname -a >> ${report_file}
echo "" >> ${report_file}
cat /etc/os-release >> ${report_file}
dpkg -l >> ${report_file}

