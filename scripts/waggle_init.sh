#!/bin/bash




set -x
set -e

if [ ! -e /media/boot/boot.ini ] ; then
  echo "error: could not find /media/boot/boot.ini"
  exit 1
fi


# create Node ID
/usr/lib/waggle/waggle_image/create_node_id.sh


# increase file system on first boot
if [ -e /root/first_boot ] ; then
  # this script increases the partition size. It is an odroid script. The user will have to reboot afterwards.
  alias msgbox=echo
  .  /usr/local/bin/fs_resize.sh ; resize_p2

  rm -f /root/first_boot

  #update-rc.d -f waggle_first_boot.sh remove

  # to prevent user from changing filesystem at this point, reboot now.
  reboot

  # other waggle services should not be started at this point.
  sleep infinity
fi


# create recovery files for partitions
if [ ! -e /recovery_p2.tar.gz ] ; then
  cd /
  rm -f  /recovery_p2.tar.gz_part
  time -p tar -cvpzf /recovery_p2.tar.gz_part --exclude=/recovery_p2.tar.gz --exclude=/recovery_p2.tar.gz_part --exclude=/dev --exclude=/proc --exclude=/sys --exclude=/tmp --exclude=/run --exclude=/mnt --exclude=/media --exclude=/lost+found --exclude=/var/cache/apt/ --one-file-system /
  # takes 10 minutes to create file
  mv /recovery_p2.tar.gz_part /recovery_p2.tar.gz
fi


if [ ! -e /recovery_p1.tar.gz ] ; then
  rm -f  /recovery_p1.tar.gz_part
  tar -cvpzf /recovery_p1.tar.gz_part --exclude=./.Spotlight-V100 --exclude=./.fseventsd --exclude=./.Trashes --one-file-system --directory=/media/boot .
  mv /recovery_p1.tar.gz_part /recovery_p1.tar.gz
fi



