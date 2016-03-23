#!/bin/bash
set -e
set -x

cp 75-waggle-arduino.rules /etc/udev/rules.d/


set +x
echo "run: udevadm control --reload-rules"