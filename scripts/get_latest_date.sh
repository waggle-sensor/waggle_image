#!/bin/bash

declare -r latest_url="http://www.mcs.anl.gov/research/projects/waggle/downloads/waggle_images/base/latest.txt"
curl ${latest_url} 2>&1 | sed -n 's/..*\([0-9]\{8\}\).img.xz/\1/p'
