#!/bin/bash

#
# Run this script manually with argument "recover" to actually start recovering partitions after all tests.
# The upstart-invoked version will not automatically do the recovery.
#

# argument "force" will kill other waggle_init process
# argument "recover" will write waggle image to other memory device (SD-card or eMMC), only if needed, e.g. filesystem broken
# argument "wipe" will force writing to other memory device (wipe forces recover)


echo "starting waggle_init.sh"


DO_RECOVERY=0
WANT_RECOVER=0
WANT_WIPE=0
WANT_FORCE=0


for i in ${1} ${2} ${3} ; do
    if [ "${i}x" == "recoverx" ] ; then
        WANT_RECOVER=1
    fi
    
    if [ "${i}x" == "wipex" ] ; then
        WANT_WIPE=1
        DO_RECOVERY=1
    fi
    
    if [ "${i}x" == "forcex" ] ; then
        WANT_FORCE=1
    fi
    
done


if [ ! -e /media/boot/boot.ini ] ; then
  echo "error: could not find /media/boot/boot.ini"
  exit 1
fi

set -x
set -e

pidfile='/var/run/waggle/waggle_init.pid'


# delete pidfile if process does not exist
oldpid=""
if [ -e ${pidfile} ] ; then
  oldpid=`cat ${pidfile}`

  if ! ps -p ${oldpid} > /dev/null 2>&1 ; then
     rm ${pidfile}
     oldpid=""
  fi
fi

# if old process is still running
if [ "${oldpid}x" != "x" ] ; then
 
  # either stop current process
  if [ ${WANT_FORCE} -eq 0 ] ; then
     echo "Script is already running. (pid: ${oldpid})"
     exit 1  
     
  fi

  # or delete old process (only if PID is different from ours (happens easily))
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




if ! hash mkdosfs > /dev/null 2>&1 ; then  
  echo "mkdosfs not found (apt-get install -y dosfstools)"
  rm -f ${pidfile}
  exit 1
fi

#
# detect MAC address
#
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

CURRENT_DEVICE=$(mount | grep "on / " | cut -f 1 -d ' ' | grep -o "/dev/mmcblk[0-1]")
OTHER_DEVICE=""

if [ "${CURRENT_DEVICE}x" == "x" ] ; then
  echo "memory card not recognized"
  rm -f ${pidfile}
  exit 1
fi


if [ "${CURRENT_DEVICE}x" == "/dev/mmcblk0x" ] ; then
  CURRENT_DEVICE_NAME="mmcblk0"
  OTHER_DEVICE="/dev/mmcblk1"
  OTHER_DEVICE_NAME="mmcblk1"
fi

if [ "${CURRENT_DEVICE}x" == "/dev/mmcblk1x" ] ; then
  CURRENT_DEVICE_NAME="mmcblk1"
  OTHER_DEVICE="/dev/mmcblk0"
  OTHER_DEVICE_NAME="mmcblk0"
fi

#
# SD-card or eMMC ? "SD" or "MMC"
#
CURRENT_DEVICE_TYPE=$(cat /sys/block/${CURRENT_DEVICE_NAME}/device/type)

if [ "${CURRENT_DEVICE_TYPE}x" == "SDx" ] || [ "${CURRENT_DEVICE_TYPE}x" == "MMCx" ] ; then

  echo -e "#e.g. 'SD' or 'MMC'\n${CURRENT_DEVICE_TYPE}" > /etc/waggle/current_memory_device
else
  echo "error: memory device not recognized: ${CURRENT_DEVICE_TYPE}"
  exit 1
fi

#
# set hostname
#
if [ "${MAC_ADDRESS}x" !=  "x" ] ; then
    
    NEW_HOSTNAME="${MAC_STRING}_${CURRENT_DEVICE_TYPE}"
    
    OLD_HOSTNAME=$(cat /etc/hostname)
    
    if [ "${NEW_HOSTNAME}x" != "${OLD_HOSTNAME}x" ] ; then
      echo ${NEW_HOSTNAME} > /etc/hostname
      echo "NEW_HOSTNAME: ${NEW_HOSTNAME}"
    fi 
fi

#
# first boot: increase file system size
#
if [ -e /root/first_boot ] ; then
  
  
  # disable u-boot console
  if [ $(grep 'setenv bootdelay "0"' /media/boot/boot.ini | wc -l) -eq 0 ] ; then
    sed -i.bak '1s/^\(.*\)/\1\n\nsetenv bootdelay "0"\n/' /media/boot/boot.ini 
  fi
  
  
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
  

  if [ -e /root/do_resize ] ; then 
    sleep 3

    # this script increases the partition size. It is an odroid script. The user will have to reboot afterwards.
    alias msgbox=echo
    .  /usr/local/bin/fs_resize.sh ; resize_p2
    rm -f /root/do_resize
  fi

  rm -f /root/first_boot

  # to prevent user from changing filesystem at this point, reboot now.
  reboot

  # other waggle services should not be started at this point.
  sleep infinity
fi

#
# create Node ID
#
/usr/lib/waggle/waggle_image/create_node_id.sh

#
# create recovery files for partitions
#
if [ ! -e /recovery_p2.tar.gz ] ; then
  cd /
  rm -f  /recovery_p2.tar.gz_part
  set +e 
  GZIP=-1 tar -cvpzf /recovery_p2.tar.gz_part --warning=no-file-changed --exclude=/recovery_p1.tar.gz --exclude=/recovery_p1.tar.gz_part --exclude=/recovery_p2.tar.gz_part --exclude=/recovery_p2.tar.gz --exclude=/dev/* --exclude=/proc/* --exclude=/sys/* --exclude=/tmp/* --exclude=/run/* --exclude=/mnt/* --exclude=/media/* --exclude=/lost+found --exclude=/var/log/upstart/waggle-* --exclude=/var/cache/apt/* --one-file-system /
  exitcode=$?
  if [ "$exitcode" != "1" ] && [ "$exitcode" != "0" ]; then
    # exit code 1 means: Some files differ
    exit $exitcode
  fi
  set -e
  # takes 10 minutes to create file
  mv /recovery_p2.tar.gz_part /recovery_p2.tar.gz
fi


if [ ! -e /recovery_p1.tar.gz ] ; then
  rm -f  /recovery_p1.tar.gz_part
  set +e 
  tar -cvpzf /recovery_p1.tar.gz_part --exclude=./.Spotlight-V100 --exclude=./.fseventsd --exclude=./.Trashes --one-file-system --directory=/media/boot .
  exitcode=$?
  if [ "$exitcode" != "1" ] && [ "$exitcode" != "0" ]; then
    exit $exitcode
  fi
  set -e
  mv /recovery_p1.tar.gz_part /recovery_p1.tar.gz
fi

#
# make sure /media/test is available 
#
mkdir -p /media/test
set +e
while [ $(mount | grep "/media/test" | wc -l) -ne 0 ] ; do
  umount /media/test
  sleep 5
done
set -e



#
# Test if other memory card actually exists
#
if [ ! -e ${OTHER_DEVICE} ] ; then
  echo "Other memory card not found. Exit."
  rm -f ${pidfile}
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
  rm -f ${pidfile}
  exit 1
done



#
# Check other boot partition
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
  set +e
  fsck.fat -n /dev/mmcblk1p1
  if [ $? -eq 0 ]  ; then
    BOOT_PARTITION_FS_OK=1
  else
    DO_RECOVERY=1
  fi
  set -e
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
# Check other data partition
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
  set +e
  fsck.ext4 -n ${OTHER_DEVICE}p2
  if [ $? -eq 0 ]  ; then
    DATA_PARTITION_FS_OK=1
  else
    DO_RECOVERY=1
  fi
  set -e
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
  echo "Warning: Recovery needed !"

  if [ ${WANT_RECOVER} -eq 1 ] || [ ${WANT_WIPE} -eq 1 ]; then
    echo "recovering..."
      
    set -e
    set -x
    
    #wipe first 500MB
    dd if=/dev/zero of=${OTHER_DEVICE} bs=1M count=500
    sync
    sleep 2
    
    # write boot loader and u-boot files (this is an odroid script)
    
    
    cd /usr/lib/waggle/waggle_image/setup-disk/
    #./write-boot.sh ${OTHER_DEVICE}
    ./make-partitions.sh  ${OTHER_DEVICE}
    sleep 3
    
    cd /usr/share/c1_uboot
    ./sd_fusing.sh ${OTHER_DEVICE}
    
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
    
    cp /recovery_p1.tar.gz /recovery_p2.tar.gz /media/test
    mkdir -p sys tmp run mnt media dev proc
    
    #
    # copy certificate files if available
    #
    mkdir -p /media/test/usr/lib/waggle/SSL/node
    if [ -d /usr/lib/waggle/SSL/node ] ; then
        for file in $(ls -1 /usr/lib/waggle/SSL/node/) ; do
          cp ${file} /media/test/usr/lib/waggle/SSL/node
        done
    fi
    
    #
    # indicate recovery process completed
    #
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
        rm -f ${pidfile}
        exit 1
    fi
    
    if [ $(grep "^setenv bootargs" /media/test/boot.ini | grep "root=UUID=${OTHER_DEVICE_DATA_UUID}" | wc -l) -eq 0 ] ; then
        echo "Error: boot.ini does not have new UUID in bootargs"
        rm -f ${pidfile}
        exit 1
    fi
    
    set +e
    while [ $(mount | grep "/media/test" | wc -l) -ne 0 ] ; do
      umount /media/test
      sleep 5
    done
    set -e
    
    # write /etc/fstab
    mount ${OTHER_DEVICE}p2 /media/test/
    
    echo "UUID=${OTHER_DEVICE_DATA_UUID}	/	ext4	errors=remount-ro,noatime,nodiratime		0 1" > /media/test/etc/fstab
    echo "UUID=${OTHER_DEVICE_BOOT_UUID}	/media/boot	vfat	defaults,rw,owner,flush,umask=000	0 0" >> /media/test/etc/fstab
    echo "tmpfs		/tmp	tmpfs	nodev,nosuid,mode=1777			0 0" >> /media/test/etc/fstab
    
    
    # udev should not require changes once it is ok
    
    
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

rm -f ${pidfile}
