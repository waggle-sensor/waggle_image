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

baseurl="http://os.archlinuxarm.org/os/ArchLinuxARM-odroid-c1-latest.tar.gz"
disk="$1"
rootpart="$disk"1
rwpart="$disk"2
rootmount=$(pwd)/mnt/root
rwmount=$(pwd)/mnt/rw

log 'starting setup'

# ensure mountpoints exists and nothing is currently using them
mkdir -p $rootmount $rwmount
umount -f $rootmount $rwmount

if test -e base.tar.gz; then
    log 'using cached image'
else
    log 'pulling image'
    if ! wget "$baseurl" -O base.tar.gz; then
        fatal 'failed to pull arch image'
    fi
fi

log 'erase disk'

if ! dd if=/dev/zero of=$1 bs=1M count=32 && sync; then
    fatal 'failed to erase disk'
fi

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

if ! mkfs.ext4 -F -O ^metadata_csum,^64bit "$rootpart"; then
    fatal 'failed to create root fs'
fi

if ! mkfs.ext4 -F -O ^metadata_csum,^64bit "$rwpart"; then
    fatal 'failed to create rw fs'
fi

log 'mounting partitions'
mount "$rootpart" $rootmount
mount "$rwpart" $rwmount

log 'unpacking image'
bsdtar -xpf base.tar.gz -C $rootmount

log 'cleaning partitions'
rm $rootmount/etc/resolv.conf $rootmount/etc/systemd/network/*

log 'copy extras'
cp -a extra/* $rootmount

log 'setting up bootloader'
(cd $rootmount/boot; ./sd_fusing.sh "$disk")

log 'setting up system'
systemd-nspawn -D $rootmount --bind $rwmount:/wagglerw -P bash -s <<EOF
pacman-key --init
pacman-key --populate archlinuxarm

# install packages
yes | pacman -Sy rsync git networkmanager modemmanager mobile-broadband-provider-info usb_modeswitch python3 openssh docker

# enable custom services
systemctl enable NetworkManager ModemManager sshd docker waggle-registration waggle-reverse-tunnel waggle-supervisor-ssh waggle-firewall waggle-watchdog

# generate ssh host keys
ssh-keygen -N '' -f /etc/ssh/ssh_host_dsa_key -t dsa
ssh-keygen -N '' -f /etc/ssh/ssh_host_ecdsa_key -t ecdsa -b 521
ssh-keygen -N '' -f /etc/ssh/ssh_host_ed25519_key -t ed25519
ssh-keygen -N '' -f /etc/ssh/ssh_host_rsa_key -t rsa -b 2048

# prepare for bind mounts
mkdir -p /var/lib /var/log /var/tmp /etc/docker /etc/waggle
touch /etc/hostname

mkdir -p /wagglerw/var/lib /wagglerw/var/log /wagglerw/var/tmp /wagglerw/etc/docker /wagglerw/etc/waggle
touch /wagglerw/etc/hostname
EOF

cat <<EOF > $rootmount/etc/fstab
UUID=$(partuuid $rootpart) / ext4 ro,nosuid,nodev,nofail,noatime,nodiratime 0 1
UUID=$(partuuid $rwpart) /wagglerw ext4 errors=remount-ro,noatime,nodiratime 0 2
/wagglerw/var/lib /var/lib none bind
/wagglerw/var/log /var/log none bind
/wagglerw/var/tmp /var/tmp none bind
/wagglerw/etc/docker /etc/docker none bind
/wagglerw/etc/hostname /etc/hostname none bind
/wagglerw/etc/waggle /etc/waggle none bind
EOF

log 'cleaning up'
umount $rootmount $rwmount

log 'setup complete'
