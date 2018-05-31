#!/bin/bash

set -e
set -x

echo $@

# command-line options
declare -r server_host=$1
shift
declare -r repositories_string=$1
shift
repositories=()
while [[ $# -gt 0 ]]; do
  repositories+=("$1")
  shift
done

mkdir -p /usr/lib/waggle

repository_strings=(${repositories_string//,/ })
for repository_string in ${repository_strings[*]}; do
  repository_tuple=(${repository_string//:/ })
  repository=${repository_tuple[0]}
  tag=${repository_tuple[1]}

  cd /usr/lib/waggle
  git clone https://github.com/waggle-sensor/${repository}.git
  cd /usr/lib/waggle/${repository}
	git checkout $tag
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
