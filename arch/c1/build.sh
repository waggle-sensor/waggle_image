#!/bin/bash -u
# Arch Linux Reference
# https://archlinuxarm.org/platforms/armv7/amlogic/odroid-c1

cd $(dirname $0) && source ../lib.sh

log "starting setup"

rootmount="$1/root"
rwmount="$1/rw"

mkdir -p "$rootmount" "$rwmount"

download_file "http://os.archlinuxarm.org/os/ArchLinuxARM-odroid-c1-latest.tar.gz" "base.tar.gz"

log "unpacking image"
bsdtar -xpf base.tar.gz -C $rootmount

log "cleaning image"
rm $rootmount/etc/resolv.conf $rootmount/etc/systemd/network/*

log "copy extras"
cp -a extra/* $rootmount

log "setting up system"
(
cd "$1"

systemd-nspawn -D $PWD/root --bind $PWD/rw:/wagglerw --bind /usr/bin/qemu-arm-static bash -s <<EOF
# setup pacman trust
pacman-key --init
pacman-key --populate archlinuxarm

# install packages
while ! yes | pacman --disable-download-timeout -Sy uboot-tools rsync git openbsd-netcat networkmanager modemmanager mobile-broadband-provider-info usb_modeswitch python3 openssh docker screen; do
    echo "failed to install packages. retrying..."
    sleep 3
done

# enable custom services
systemctl enable NetworkManager ModemManager sshd docker waggle-registration waggle-reverse-tunnel waggle-supervisor-ssh waggle-firewall waggle-heartbeat waggle-watchdog

# generate ssh host keys - TODO let system generate these
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
)

log "generate build info"
cat <<EOF > $rootmount/build.json
{
    "build_time": "$(utctimestamp)",
    "build_host": "$(hostname)",
    "device": "ODROID C1+"
}
EOF

log "cleaning up"
umount $rootmount $rwmount

log "setup complete"
