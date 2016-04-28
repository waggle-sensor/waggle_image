#!/bin/bash

#
# Run this script manually with argument "recover" to actually start recovering partitions after all tests.
# The upstart-invoked version will not automatically do the recovery.
#

# argument "force" will kill other process
# argument "recover" will write waggle image to other memory device (SD-card or eMMC)
# It is not possible to combine those arguments at the moment


set -x
set -e

if [ ! -e /media/boot/boot.ini ] ; then
  echo "error: could not find /media/boot/boot.ini"
  exit 1
fi


pidfile='/var/run/waggle/waggle_init.pid'


if [ -e ${pidfile} ] ; then
  oldpid=`cat ${pidfile}`

  if [ "${1}x" != "forcex" ] ; then
      echo "Script is already running."
  fi

  # delete process only if PID is different from ours (happens easily)  
  if [ "${oldpid}_" != "$$_"  ] ; then
    echo "Kill other waggle_init process"
    set +e
    kill -9 ${oldpid}
    set -e
    sleep 2
    rm -f ${pidfile}
  fi
fi

mkdir -p /var/run/waggle/

echo "$$" > ${pidfile}



# create Node ID
/usr/lib/waggle/waggle_image/create_node_id.sh


if ! hash mkdosfs > /dev/null 2>&1 ; then  
  echo "mkdosfs not found (apt-get install -y dosfstools)"
  exit 1
fi

MAC_ADDRESS=""
MODALIAS=""
for dev in /sys/class/net/eth? ; do
    MODALIAS=$(cat ${dev}/device/modalias)
    if [ "${MODALIAS}x" ==  "platform:meson-ethx" ] ; then
        MAC_ADDRESS=$(cat ${dev}/address)
        echo "MAC_ADDRESS: ${MAC_ADDRESS}"
        MAC_STRING=$(echo ${MAC_ADDRESS} | tr -d ":")
    fi 
done


# increase file system on first boot
if [ -e /root/first_boot ] ; then
  # this script increases the partition size. It is an odroid script. The user will have to reboot afterwards.
  
  #create new udev rules file to fix wrong eth order
  if [ "${MAC_ADDRESS}x" != "x" ] ; then
    # if MAC address is assigned to eth0 than all is ok.
    if [ $(cat /etc/udev/rules.d/70-persistent-net.rules | grep -v "^#" | grep "ATTR{address}\=\=\"${MAC_ADDRESS}" | grep "NAME\=\"eth0\"" | wc -l) -ne 1 ] ; then
      sed -i.bak -e "/${MAC_ADDRESS}/d" -e '/NAME=\"eth0/d' /etc/udev/rules.d/70-persistent-net.rules
  
      export INTERFACE=eth0
      export MATCHADDR=${MAC_ADDRESS}
      /lib/udev/write_net_rules
    else
        echo "udev eth0 ok"
    fi
  fi
  
  sleep 3
  
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
  tar -cvpzf /recovery_p2.tar.gz_part --exclude=/recovery_p1.tar.gz --exclude=/recovery_p1.tar.gz_part --exclude=/recovery_p2.tar.gz_part --exclude=/recovery_p2.tar.gz --exclude=/dev --exclude=/proc --exclude=/sys --exclude=/tmp --exclude=/run --exclude=/mnt --exclude=/media --exclude=/lost+found --exclude=/var/cache/apt --exclude=/var/log --one-file-system /
  # takes 10 minutes to create file
  mv /recovery_p2.tar.gz_part /recovery_p2.tar.gz
fi


if [ ! -e /recovery_p1.tar.gz ] ; then
  rm -f  /recovery_p1.tar.gz_part
  tar -cvpzf /recovery_p1.tar.gz_part --exclude=./.Spotlight-V100 --exclude=./.fseventsd --exclude=./.Trashes --one-file-system --directory=/media/boot .
  mv /recovery_p1.tar.gz_part /recovery_p1.tar.gz
fi

# make sure /media/test is available 
mkdir -p /media/test
set +e
while [ $(mount | grep "/media/test" | wc -l) -ne 0 ] ; do
  umount /media/test
  sleep 5
done
set -e


CURRENT_DEVICE=$(mount | grep "on / " | cut -f 1 -d ' ' | grep -o "/dev/mmcblk[0-1]")
OTHER_DEVICE=""

if [ "${CURRENT_DEVICE}x" == "x" ] ; then
  echo "memory card not recognized"
  exit 1
fi


if [ "${CURRENT_DEVICE}x" == "/dev/mmcblk0x" ] ; then
  OTHER_DEVICE="/dev/mmcblk1"
  OTHER_DEVICE_NAME="mmcblk1"
fi

if [ "${CURRENT_DEVICE}x" == "/dev/mmcblk1x" ] ; then
  OTHER_DEVICE="/dev/mmcblk0"
  OTHER_DEVICE_NAME="mmcblk0"
fi

# Test if other memory card exists
if [ ! -e ${OTHER_DEVICE} ] ; then
  echo "Other memory card not found. Exit."
  exit 0
fi

# umount, just in case
for device in $(mount | grep "^${OTHER_DEVICE}" | cut -f1 -d ' ') ; do 
  echo "Warning, device ${device} is currently mounted"
  umount ${device}
  sleep 5
done

for device in $(mount | grep "^${OTHER_DEVICE}" | cut -f1 -d ' ') ; do 
  echo "Error, device ${device} is still mounted"
  exit 1
done

DO_RECOVERY=0

#
# Check boot partition
#

BOOT_PARTITION_EXISTS=0
if [ $(parted -m ${OTHER_DEVICE} print | grep "^1:.*fat16::;" | wc -l ) -eq 1 ] ; then
  echo "boot partition found"
  BOOT_PARTITION_EXISTS=1
else
  echo "boot partition not found"
  DO_RECOVERY=1  
fi

BOOT_PARTITION_FS_OK=0
if [ ${DO_RECOVERY} -eq 0 ] && [ ${BOOT_PARTITION_EXISTS} -eq 1 ] ; then
  fsck.fat -n /dev/mmcblk1p1
  if [ $? -eq 0 ]  ; then
    BOOT_PARTITION_FS_OK=1
  else
    DO_RECOVERY=1
  fi
fi


BOOT_PARTITION_MOUNTABLE=0
if [ ${DO_RECOVERY} -eq 0 ] && [ ${BOOT_PARTITION_FS_OK} -eq 1 ] ; then
  mkdir -p /media/test

  set +e
  mount ${OTHER_DEVICE}p1 /media/test
  if [ $? -ne 0 ]  ; then
    echo "Could not mount boot partition"
    DO_RECOVERY=1
  else
    BOOT_PARTITION_MOUNTABLE=1
  fi
fi

BOOT_PARTITION_BOOT_INI=0
if [ ${DO_RECOVERY} -eq 0 ] && [ ${BOOT_PARTITION_MOUNTABLE} -eq 1 ] ; then

    echo "Boot partition mounted"

    if [ -e /media/test/boot.ini ] ; then
      echo "boot partition looks legit"
      BOOT_PARTITION_BOOT_INI=1
    else
      echo "boot partition has no boot.ini"
      DO_RECOVERY=1
    fi
fi

set +e
while [ $(mount | grep "/media/test" | wc -l) -ne 0 ] ; do
  umount /media/test
  sleep 5
done
set -e

#
# Check data partition
#

DATA_PARTITION_EXISTS=0
if [ $(parted -m ${OTHER_DEVICE} print | grep "^2:.*ext4::;" | wc -l ) -eq 1 ] ; then
  echo "data partition found"
  DATA_PARTITION_EXISTS=1
else
  echo "data partition not found"
  DO_RECOVERY=1
fi

DATA_PARTITION_FS_OK=0
if [ ${DO_RECOVERY} -eq 0 ] && [ ${DATA_PARTITION_EXISTS} -eq 1 ] ; then
  fsck.ext4 -n ${OTHER_DEVICE}p2
  if [ $? -eq 0 ]  ; then
    DATA_PARTITION_FS_OK=1
  else
    DO_RECOVERY=1
  fi
fi



DATA_PARTITION_MOUNTABLE=0
if [ ${DO_RECOVERY} -eq 0 ] && [ ${DATA_PARTITION_FS_OK} -eq 1 ] ; then
  mkdir -p /media/test

  set +e
  mount ${OTHER_DEVICE}p2 /media/test
  if [ $? -ne 0 ]  ; then
    echo "Could not mount data partition"
    DO_RECOVERY=1
  else
    DATA_PARTITION_MOUNTABLE=1
  fi
fi

DATA_PARTITION_WAGGLE=0
if [ ${DO_RECOVERY} -eq 0 ] && [ ${DATA_PARTITION_MOUNTABLE} -eq 1 ] ; then

    echo "Data partition mounted"

    if [ -d /media/test/usr/lib/waggle ] ; then
      echo "data partition looks legit"
      DATA_PARTITION_WAGGLE=1
    else
      echo "data partition has no waggle directory"
      DO_RECOVERY=1
    fi
fi

set +e
while [ $(mount | grep "/media/test" | wc -l) -ne 0 ] ; do
  umount /media/test
  sleep 5
done
set -e

if [ ${DO_RECOVERY} -eq 1 ] ; then
  echo "I want to do recovery"

  if [ "${1}x" == "recoverx" ] ; then
    echo "recovering"
      
    set -e
    set -x
    
    #wipe first 500MB
    dd if=/dev/zero of=${OTHER_DEVICE} bs=1M count=500
    sync
    sleep 2
    
    cd /usr/lib/waggle/waggle_image/setup-disk/
    ./write-boot.sh ${OTHER_DEVICE}
    ./make-partitions.sh  ${OTHER_DEVICE}
    sleep 3
    mount ${OTHER_DEVICE}p1 /media/test/
    cd /media/test
    tar xvzf /recovery_p1.tar.gz
    touch /media/test/recovered.txt
    
    cd /media
    sleep 1
    
    set +e
    while [ $(mount | grep "/media/test" | wc -l) -ne 0 ] ; do
      umount /media/test
      sleep 5
    done
    set -e
    
    mount ${OTHER_DEVICE}p2 /media/test/
    cd /media/test
    tar xvzf /recovery_p2.tar.gz
    
    # copy certificate files
    mkdir -p /media/test/usr/lib/waggle/SSL/node
    if [ -d /usr/lib/waggle/SSL/node ] ; then
        cp 
    fi
    
    
    touch /media/test/recovered.txt
    
    cd /media
    sleep 1
    
    set +e
    while [ $(mount | grep "/media/test" | wc -l) -ne 0 ] ; do
      umount /media/test
      sleep 5
    done
    set -e
    
    
    OTHER_DEVICE_BOOT_UUID=$(blkid -o export ${OTHER_DEVICE}p1 | grep "^UUID" |  cut -f2 -d '=')
    echo "OTHER_DEVICE_BOOT_UUID: ${OTHER_DEVICE_BOOT_UUID}"
    
    OTHER_DEVICE_DATA_UUID=$(blkid -o export ${OTHER_DEVICE}p2 | grep "^UUID" |  cut -f2 -d '=')
    echo "OTHER_DEVICE_DATA_UUID: ${OTHER_DEVICE_DATA_UUID}"
    
    # Is the other device SD-card or eMMC ?
    OTHER_DEVICE_TYPE=$(cat /sys/block/${OTHER_DEVICE_NAME}/device/type)
    
    
    # modify boot.ini
    mount ${OTHER_DEVICE}p1 /media/test/
    sleep 1
    sed -i.bak 's/root=UUID=[a-fA-F0-9-]*/root=UUID='${OTHER_DEVICE_DATA_UUID}'/' /media/test/boot.ini 
    
    if [ $(grep "^setenv bootargs" /media/test/boot.ini | grep "root=UUID=" | wc -l) -eq 0 ] ; then
        echo "Error: boot.ini does not have UUID in bootargs"
        exit 1
    fi
    
    if [ $(grep "^setenv bootargs" /media/test/boot.ini | grep "root=UUID=${OTHER_DEVICE_DATA_UUID}" | wc -l) -eq 0 ] ; then
        echo "Error: boot.ini does not have new UUID in bootargs"
        exit 1
    fi
    
    set +e
    while [ $(mount | grep "/media/test" | wc -l) -ne 0 ] ; do
      umount /media/test
      sleep 5
    done
    set -e
    
    # write /etc/fstab
    mount ${OTHER_DEVICE}p1 /media/test/
    
    echo "UUID=${OTHER_DEVICE_DATA_UUID}	/	ext4	errors=remount-ro,noatime,nodiratime		0 1" > /media/test/etc/fstab
    echo "UUID=${OTHER_DEVICE_BOOT_UUID}	/media/boot	vfat	defaults,rw,owner,flush,umask=000	0 0" >> /media/test/etc/fstab
    echo "tmpfs		/tmp	tmpfs	nodev,nosuid,mode=1777			0 0" >> /media/test/etc/fstab
    
    
    # udev should not require changes once it is ok
    
    
    # modify /etc/hostname
    if [ "${MAC_ADDRESS}x" !=  "x" ] ; then
        
        NEW_HOSTNAME = "${MAC_STRING}_${OTHER_DEVICE_TYPE}"
        echo ${NEW_HOSTNAME} > /media/test/etc/hostname
        echo "{NEW_HOSTNAME: ${NEW_HOSTNAME}"
    fi
    
    
    set +e
    while [ $(mount | grep "/media/test" | wc -l) -ne 0 ] ; do
      umount /media/test
      sleep 5
    done
    set -e
    
    # TODO check for failed/partial recovery !
    #TODO recovery files, certificate files, 
    
    
    
    
  else
    echo "No automatic recovery. Use argument \"recover\" to invoke recovery."        
  fi
else
  echo "all looks good" 
fi


