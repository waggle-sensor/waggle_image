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

log 'erase disk'
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
# TODO bind mount all mount points at build time!
systemd-nspawn -D root -P bash -s <<EOF
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
EOF

# TODO how about we just bind mount /etc and /var with a known working failsafe
log 'setting up bind mounts'
(
cd root
mkdir -p wagglerw
mkdir -p var/lib var/log var/tmp etc/docker
touch etc/hostname
)

(
cd rw
mkdir -p var/lib var/log var/tmp etc/docker
touch etc/hostname
)

cat <<EOF > root/etc/fstab
UUID=$(partuuid $rootpart) / ext4 ro,nosuid,nodev,nofail,noatime,nodiratime 0 1
UUID=$(partuuid $rwpart) /wagglerw ext4 errors=remount-ro,noatime,nodiratime 0 2
/wagglerw/var/lib /var/lib none bind
/wagglerw/var/log /var/log none bind
/wagglerw/var/tmp /var/tmp none bind
/wagglerw/etc/docker /etc/docker none bind
/wagglerw/etc/hostname /etc/hostname none bind
EOF

log 'cleaning up'
umount root
umount rw

log 'setup complete'
