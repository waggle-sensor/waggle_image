#!/bin/bash
set -e

# This script tries to get the time from the beehive server. 


SERVER_HOST="beehive1.mcs.anl.gov"


try_set_time()
{
  # check if time is needed
  #CURRENT_YEAR=$(date +"%Y")
  #if [ "${CURRENT_YEAR}x" == "x" ] ; then
  #  CURRENT_YEAR=0
  #fi
  #if [ ! ${CURRENT_YEAR} -lt ${REFERENCE_YEAR} ] ; then
  #  echo "date seems to be ok"
  #  return 0
  #fi
  #echo "Device seems to have the wrong date: year=${CURRENT_YEAR}"

  # get epoch from server
  set +e
  EPOCH=$(curl --connect-timeout 10 --retry 100 --retry-delay 10 http://${SERVER_HOST}/api/1/epoch | grep -oP '{"epoch": \d+}' | grep -oP '\d+')
  set -e

  # if EPOCH is not empty, set date
  if [ ! "${EPOCH}x" == "x" ] ; then
    set -x
    date -s@${EPOCH}
    SUCCESS=$?
    set +x
    if [ ${SUCCESS} -eq 0 ] ; then
       return 0
    fi
    return 1
  fi
  return 1
}

########### start ###########

while [ 1 ] ; do
  
  while [ 1 ] ; do
    try_set_time
    if [ $? -eq 0 ] ; then
      break
    fi
    # did not set time, will try again.
    sleep 10
  done

  echo "sleep 24h"
  sleep 24h
done



