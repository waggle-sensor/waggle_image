#!/bin/bash

service_list=$(cat /root/service_list.txt)
for service in ${service_list[@]}; do
  systemctl stop $service
  systemctl disable $service
done
systemctl stop rabbitmq-server
systemctl disable rabbitmq-server
rm /etc/init.d/rabbitmq-server
rm /etc/systemd/system/waggle*
rm /etc/systemd/system/rabbitmq-server.service
rm /etc/bash_completion.d/waggle*
rm /usr/bin/waggle*
rm /usr/bin/rabbitmqadmin
rm -rf /etc/waggle
rm -rf /home/waggle/.ssh
rm -rf /root/.ssh
rm -rf /var/log/waggle
rm /usr/lib/waggle
rm /var/dc
rm /var/log/comms
rm /etc/udev/rules.d/*
rm /home/waggle/*test*
# TODO:
# - replace /etc/shadow
# - replace /etc/group
# - replace /root/.bashrc
# - replace /home/waggle/.bashrc
# - replace /etc/hosts
# - replace /etc/network/interfaces
