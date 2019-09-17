#!/bin/bash -u
# Arch Linux Reference
# https://archlinuxarm.org/platforms/armv7/amlogic/odroid-c1

log() {
    echo -e "\033[34m$(date +'%Y/%m/%d %H:%M:%S') - $*\033[0m"
}

fatal() {
    echo -e "\033[31m$(date +'%Y/%m/%d %H:%M:%S') - $*\033[0m"
    exit 1
}

partuuid() {
    blkid -s UUID -o value "$1"
}

disk="$1"
rootpart="$disk"1
rwpart="$disk"2

log 'starting setup'

# ensure mountpoints exists and nothing is currently using them
mkdir -p root rw
umount -f root
umount -f rw

if test -e ArchLinuxARM-odroid-c1-latest.tar.gz; then
    log 'using cached image'
else
    log 'pulling image'
    wget http://os.archlinuxarm.org/os/ArchLinuxARM-odroid-c1-latest.tar.gz
fi

log 'clear disk'
dd if=/dev/zero of=$1 bs=1M count=32
sync

log 'creating partitions'
fdisk $disk <<EOF
o
n
p
1

+4G
n
p
2


p
w
EOF
sync
partprobe

log 'creating filesystems'
mkfs.ext4 -F -O ^metadata_csum,^64bit "$rootpart"
mkfs.ext4 -F -O ^metadata_csum,^64bit "$rwpart"

log 'mounting partitions'
mount "$rootpart" root
mount "$rwpart" rw

log 'unpacking image'
bsdtar -xpf ArchLinuxARM-odroid-c1-latest.tar.gz -C root

log 'cleaning partitions'
rm root/etc/resolv.conf root/etc/systemd/network/*

log 'copy extras'
cp -a extra/* root/

log 'writing bootloader'
(cd root/boot; ./sd_fusing.sh "$disk")

log 'setting up packages'
systemd-nspawn -D root -P bash -s <<EOF
pacman-key --init
pacman-key --populate archlinuxarm

# install packages
yes | pacman -Sy rsync git networkmanager modemmanager mobile-broadband-provider-info usb_modeswitch python3 openssh docker

# enable custom services
systemctl enable NetworkManager ModemManager sshd docker waggle-registration waggle-reverse-tunnel waggle-supervisor-ssh waggle-firewall waggle-watchdog

# ensure ntp enabled
timedatectl set-ntp yes
EOF

log 'setting up bind mounts'
(cd root; mkdir -p wagglerw)
(cd rw; mkdir -p var/lib var/log var/tmp)
cat <<EOF > root/etc/fstab
UUID=$(partuuid $rootpart) /wagglerw ext4 errors=remount-ro,noatime,nodiratime 0 2
/wagglerw/var/lib /var/lib none bind
/wagglerw/var/log /var/log none bind
/wagglerw/var/tmp /var/tmp none bind
EOF

log 'cleaning up'
umount root
umount rw

log 'setup complete'
