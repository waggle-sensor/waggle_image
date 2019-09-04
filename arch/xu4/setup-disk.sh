#!/bin/bash -u
# Arch Linux Reference
# https://archlinuxarm.org/platforms/armv7/samsung/odroid-xu4

log() {
    echo -e "\033[34m$(date +'%Y/%m/%d %H:%M:%S') - $*\033[0m"
}

fatal() {
    >&2 echo -e "\033[31m$(date +'%Y/%m/%d %H:%M:%S') - $*\033[0m"
    exit 1
}

disk="$1"

umount root

if test -e ArchLinuxARM-odroid-xu3-latest.tar.gz; then
        log using cached image
else
        log pulling image
        wget http://os.archlinuxarm.org/os/ArchLinuxARM-odroid-xu3-latest.tar.gz
fi

dd if=/dev/zero of=$disk bs=1M count=8

log creating partitions
fdisk $disk <<EOF
o
n
p
1
4096

w
EOF

log creating filesystems
mkfs.ext4 "$disk"1

mkdir -p root
mount "$disk"1 root

log unpacking image
bsdtar -xpf ArchLinuxARM-odroid-xu3-latest.tar.gz -C root

log cleaning partitions
rm root/etc/resolv.conf

log writing bootloader
(cd root/boot; sh sd_fusing.sh "$disk")

systemd-nspawn -D root -P bash -s <<EOF
pacman-key --init
pacman-key --populate archlinuxarm
pacman -Syy

# install packages
yes | pacman -Sy rsync git

# ensure ntp enabled
timedatectl set-ntp yes
EOF

umount root
