#!/bin/bash
set -e


# Documentation
#
# ODROID-XU3/XU4
# Pin 4 = Export No 173 
# (GND = PIN2 or PIN30)
# Source: http://odroid.com/dokuwiki/doku.php?id=en:xu4_hardware
# Source: http://dn.odroid.com/5422/ODROID-XU3/Schematics/XU4_HIGHTOPSILK.png

# ODROID-C1/C1+/C0/C2
# Pin 3 = Export GPIO#205 
#
# Source: http://odroid.com/dokuwiki/doku.php?id=en:c2_hardware#expansion_connectors
#

TIME_LOW=1.0
TIME_HIGH=1.0


########

echo ""
echo ""
echo "Starting heartbeat script...  "
echo "TIME: "$(date +"%Y-%m-%d %H:%M" -u)

echo ""
echo "TIME_LOW  : ${TIME_LOW}"
echo "TIME_HIGH : ${TIME_HIGH}"



# Check if the current device is a C1+ or XU4. 

HEADER=`head -n 1 /media/boot/boot.ini`

DEVICE=""

if [ ${HEADER}x == "ODROIDXU-UBOOT-CONFIGx" ] ; then
  if [ -e /media/boot/exynos5422-odroidxu3.dtb ] ; then
    # XU3 and XU4 are identical
    DEVICE="XU3"
  fi
elif [ ${HEADER}x == "ODROIDC-UBOOT-CONFIGx" ] ; then

  DEVICE="C"


fi


if [ ${DEVICE}x == "x" ] ; then
  echo "Device not recognized"
  exit 1
fi 


if [ ${DEVICE}x == "XU3x" ] ; then
  GPIO_EXPORT=173
  PIN=4
elif [ ${DEVICE}x == "Cx" ] ; then
  GPIO_EXPORT=205
  PIN=3
else
  echo "Device ${DEVICE} not recognized"
  exit 1
fi

echo "Detected device: ${DEVICE}"


echo "Activating GPIO pin ${PIN} with export number ${GPIO_EXPORT}."

if [ ! -d /sys/class/gpio/gpio${GPIO_EXPORT} ] ; then
  set -x
  echo ${GPIO_EXPORT} > /sys/class/gpio/export
  set +x
fi

set -x
echo "out" > /sys/class/gpio/gpio${GPIO_EXPORT}/direction
set +x

echo "Starting heartbeat..."



set +x

while [ 1 ] ; do 
  echo 1 > /sys/class/gpio/gpio${GPIO_EXPORT}/value
  sleep ${TIME_HIGH}
  echo 0  > /sys/class/gpio/gpio${GPIO_EXPORT}/value
  sleep ${TIME_LOW}
done


