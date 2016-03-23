#!/bin/bash
set -x
set -e

rm -f /etc/udev/rules.d/75-wwan-net.rules
cp 75-wwan-net.rules /etc/udev/rules.d/

cp ./wvdial.conf to /etc/

set +x
echo "run: udevadm control --reload-rules"