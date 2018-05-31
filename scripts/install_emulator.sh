#!/bin/bash


apt-get update
add-apt-repository ppa:linaro-maintainers/tools
apt-get install -y linaro-image-tools qemu-user-static qemu-system libvirt-bin
apt-get install -y libpixman-1-dev zlib1g-dev libglib2.0-dev shtool build-essential

mkdir odroid
cd odroid
wget http://odroid.us/odroid/users/osterluk/qemu-example/qemu-example.tgz
tar -xvf qemu-example.tgz

qemu-img create rootfs-buildroot.ext2 200M
sudo mkfs.ext2 rootfs-buildroot.ext2
mkdir -p mnt
sudo mount -o loop rootfs-buildroot.ext2 mnt
echo "Done preparing empty VM disk." > mnt/report.txt
cat mnt/report.txt
umount ./mnt
