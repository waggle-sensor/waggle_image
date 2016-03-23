#!/bin/bash
set -x
set -e


cp 75-wwan-net.rules /etc/udev/rules.d/

cp ./wvdial.conf to /etc/


echo "run: udevadm control --reload-rules"