#!/bin/bash

set -e
set -x

print_usage() {
  echo "Usage: build-base-docker-images [OPTIONS]"
  echo "OPTIONS"
  line="--help                         "
  line+="show this usage message"
  echo "  $line"
  line="-n |--node-controller        "
  line+="build the Node Controller base Docker image"
  line="-e |--edge-processor        "
  line+="build the Edge Processor base Docker image"
  line="-v |--version=<version>        "
  line+="show this usage message"
  echo "  $line"
  line="-r |--revision=<revision>      "
  line+="build revision <revision> of the specified version"
  echo "  $line"
  line="-d |--deployment=<deployment>  "
  line+="build deployment <deployment> of the specified version"
  echo "  $line"
}

node_controller=0
version=''
revision=0
deployment='Public'
server_host=''
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --help)
      print_usage
      exit
      ;;
    -n)
      node_controller=1
      shift
      ;;
    --node-controller=*)
      node_controller=1
      ;;
    -e)
      edge_processor=1
      shift
      ;;
    --edge-processor=*)
      edge_processor=1
      ;;
    -v)
      version="$2"
      shift
      ;;
    --version=*)
      version="${key#*=}"
      ;;
    -r)
      revision="$2"
      shift
      ;;
    --revision=*)
      revision="${key#*=}"
      ;;
    -d)
      deployment="$2"
      shift
      ;;
    --deployment=*)
      deployment="${key#*=}"
      ;;
    -h)
      server_host="$2"
      shift
      ;;
    --server-host=*)
      server_host="${key#*=}"
      ;;
      *)
      ;;
  esac
  shift
done

declare -r script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd ${script_dir}/config

if [ "x$version" == "x" ]; then
  # query DB for latest version and revision if not specified
  version_revision=$(./get-latest-build)
  version_revision_tuple=(${version_revision//-/ })
  version=${version_revision_tuple[0]}
fi

# command-line options
declare -r server_host=$1
declare -r branch=$2

# Detect the Odroid model. This yields either ODROIDC or ODROID-XU3.
# The ODROID_MODEL environment variable can be used to override detection
# in cases such as building Docker images where actual hardware is not present.
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
