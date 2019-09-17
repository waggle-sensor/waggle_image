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

log starting setup

disk="$1"

# ensure nothing is currently using mountpoint
umount root

if test -e ArchLinuxARM-odroid-c1-latest.tar.gz; then
        log using cached image
else
        log pulling image
        wget http://os.archlinuxarm.org/os/ArchLinuxARM-odroid-c1-latest.tar.gz
fi

log clear disk
dd if=/dev/zero of=$disk bs=1M count=8
sync

log creating partitions
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

rootpart="$disk"1
datapart="$disk"2

log creating filesystems
mkfs.ext4 -F -O ^metadata_csum,^64bit "$rootpart"
mkfs.ext4 -F -O ^metadata_csum,^64bit "$datapart"

mkdir -p root
mount "$rootpart" root

log unpacking image
bsdtar -xpf ArchLinuxARM-odroid-c1-latest.tar.gz -C root

log cleaning partitions
rm root/etc/resolv.conf root/etc/systemd/network/*

log copy extras
cp -a extra/* root/

log writing bootloader
(cd root/boot; ./sd_fusing.sh "$disk")

log setting up packages
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

# UUID=$(partuuid $rootpart) / ext4    ${root_mode},nosuid,nodev,nofail,noatime,nodiratime            0 1

mkdir root/wagglerw

cat <<EOF > root/etc/fstab
UUID=$(partuuid $rootpart) /wagglerw ext4 errors=remount-ro,noatime,nodiratime 0 2
EOF


umount root

log setup complete
