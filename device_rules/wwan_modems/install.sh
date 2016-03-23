#!/bin/bash
set -x
set -e


cp 75-wwan-net.rules /etc/udev/rules.d/

cp ./wvdial.conf to /etc/

set +x
echo "run: udevadm control --reload-rules"