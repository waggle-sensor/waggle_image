#!/bin/bash

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd $script_dir

declare -r latest_url="http://www.mcs.anl.gov/research/projects/waggle/downloads/waggle_images/base/latest.txt"
declare -r branch=$(git branch | awk '/^\*/ { sub(/^\* /, ""); print}')
declare -A dates
dates=([develop]=20170307 [v2.5.1]=20170307 ["hotfix-2.5.2"]=20170425)
date=${dates[$branch]}
if [ "x$date" == "x" ]; then
  curl ${latest_url} 2>&1 | sed -n 's/..*\([0-9]\{8\}\).img.xz/\1/p'
else
  echo $date
fi

