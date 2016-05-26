#!/bin/bash


HEADER=`head -n 1 /media/boot/boot.ini`


ODROID_MODEL=""

if [ ${HEADER}x == "ODROIDXU-UBOOT-CONFIGx" ] ; then
  if [ -e /media/boot/exynos5422-odroidxu3.dtb ] ; then
    # XU3 and XU4 are identical
    ODROID_MODEL ="XU3"
  fi
elif [ ${HEADER}x == "ODROIDC-UBOOT-CONFIGx" ] ; then
  ODROID_MODEL ="C"
fi

if [ ${ODROID_MODEL}x == "x" ] ; then
  echo "Device not recognized"
  exit 1
fi 

echo "ODROID_MODEL=${ODROID_MODEL}"