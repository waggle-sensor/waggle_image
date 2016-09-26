#!/bin/bash

set -e
set -x

cd /usr/lib/waggle
repos=$(ls --color=never -1 -d */)
for repo in $repos; do
  cd $repo
  ./configure --system
  cd /usr/lib/waggle
done
