#!/bin/bash -u

log() {
    echo -e "\033[34m$(date +'%Y/%m/%d %H:%M:%S') - $*\033[0m"
}

fatal() {
    >&2 echo -e "\033[31m$(date +'%Y/%m/%d %H:%M:%S') - $*\033[0m"
    exit 1
}


disk="$1"

if test -e ArchLinuxARM-odroid-c1-latest.tar.gz; then
        log using cached image
else
        log pulling image
        wget http://os.archlinuxarm.org/os/ArchLinuxARM-odroid-c1-latest.tar.gz
fi

dd if=/dev/zero of=$disk bs=1M count=8

log creating partitions
fdisk $disk <<EOF
o
n
p
1


w
EOF

log creating filesystems
mkfs.ext4 -O ^metadata_csum,^64bit "$disk"1

mkdir -p root
umount root
mount "$disk"1 root

log unpacking image
bsdtar -xpf ArchLinuxARM-odroid-c1-latest.tar.gz -C root

log cleaning partitions
rm root/etc/resolv.conf

log writing bootloader
(cd root/boot; ./sd_fusing.sh "$disk")

systemd-nspawn -D root -P bash -s <<EOF
pacman-key --init
pacman-key --populate archlinuxarm
pacman -Syy
EOF

umount root
