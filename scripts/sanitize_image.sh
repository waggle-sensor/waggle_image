#!/bin/bash

service_list=$(cat /root/service_list.txt)
for service in ${service_list[@]}; do
  systemctl stop $service
  systemctl disable $service
done
systemctl stop rabbitmq-server
systemctl disable rabbitmq-server
rm -f /etc/init.d/rabbitmq-server
rm -f /etc/systemd/system/waggle*
rm -f /etc/systemd/system/rabbitmq-server.service
rm -f /etc/bash_completion.d/waggle*
rm -f /usr/bin/waggle*
rm -f /usr/bin/rabbitmqadmin
rm -rf /etc/waggle
rm -rf /home/waggle/.ssh
rm -rf /root/.ssh
rm -rf /var/log/waggle
rm -rf /usr/lib/waggle
rm -rf /var/dc
rm -rf /var/log/comms
rm -f /etc/udev/rules.d/*
rm -f /home/waggle/*test*
rm -f /recovery*.tar.gz
# TODO:
# - replace /etc/shadow
# - replace /etc/group
# - replace /root/.bashrc
# - replace /home/waggle/.bashrc
# - replace /etc/hosts
# - replace /etc/network/interfaces
