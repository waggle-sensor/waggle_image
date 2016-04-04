#!/bin/bash
set -e

# This script tries to get the time from the beehive server. If the year seems to be ok already, it will not try to fetch time
#  from the beehive server. This is not intended to provide accurate time. For accurate time either use ntp or get time via the waggle protocol.



SERVER_HOST="beehive1.mcs.anl.gov"
REFERENCE_YEAR=2016

while [ 1 ] ; do


  # check if time is needed
  CURRENT_YEAR=$(date +"%Y")


  if [ "${CURRENT_YEAR}x" == "x" ] ; do
    CURRENT_YEAR=0
  fi


  if [ ! ${CURRENT_YEAR} -lt ${REFERENCE_YEAR} ] ; do
    echo "date seems to be ok"
    exit 0
  fi

  echo "Device seems to have the wrong date: year=${CURRENT_YEAR}"

  # get epoch from server
  set +e
  EPOCH=$(curl http://${SERVER_HOST}/api/1/epoch | grep -oP '{"epoch": \d+}' | grep -oP '\d+')
  set -e

  # if EPOCH is not empty, set date
  if [ ! "${EPOCH}x" == "x" ] ; do
    date -s@${EPOCH}
  fi

  sleep 10


done



