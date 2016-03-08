#!/bin/bash
#This goes in /usr/bin/wvwaggle.sh, and make the file executable with chmod +x /usr/bin/wvwaggle.sh
#Let us give the modem time to settle.
sleep 20
rm /dev/$1
ln -s  $(ls /dev/$1* | sort | head -1) /dev/$1
wvdial $1
