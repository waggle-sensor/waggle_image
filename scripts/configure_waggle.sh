#!/bin/bash

set -e
set -x

apt-get update
apt-key update
apt-get install -y htop iotop iftop bwm-ng screen git python-dev python-pip python3-dev python3-pip tree psmisc dosfstools parted bash-completion fswebcam v4l-utils

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

