#!/bin/bash -u
# Arch Linux Reference
# https://archlinuxarm.org/platforms/armv7/amlogic/odroid-c1

cd $(dirname $0) && source ../lib.sh

log "starting setup"

disk="$1"
rootpart="$disk"1
rwpart="$disk"2
rootmount=$(pwd)/mnt/root
rwmount=$(pwd)/mnt/rw

# ensure mountpoints exists and nothing is currently using them
mkdir -p $rootmount $rwmount
umount -f $rootmount $rwmount

download_file "http://os.archlinuxarm.org/os/ArchLinuxARM-odroid-c1-latest.tar.gz" "base.tar.gz"

setup_disk "$disk" <<EOF
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

log "creating filesystems"

if ! mkfs.ext4 -F -O ^metadata_csum,^64bit "$rootpart"; then
    fatal 'failed to create root fs'
fi

if ! mkfs.ext4 -F -O ^metadata_csum,^64bit "$rwpart"; then
    fatal 'failed to create rw fs'
fi

log "mounting partitions"
mount "$rootpart" $rootmount
mount "$rwpart" $rwmount

log "unpacking image"
bsdtar -xpf base.tar.gz -C $rootmount

log "cleaning partitions"
rm $rootmount/etc/resolv.conf $rootmount/etc/systemd/network/*

log "copy extras"
cp -a extra/* $rootmount

log "setting up bootloader"
(cd $rootmount/boot; bash sd_fusing.sh "$disk")

log "setting up system"
# TODO resolve --pipe flag between versions of nspawn
systemd-nspawn -D $rootmount --bind $rwmount:/wagglerw --bind /usr/bin/qemu-arm-static bash -s <<EOF
# setup pacman trust
pacman-key --init
pacman-key --populate archlinuxarm

# install packages
while ! yes | pacman --disable-download-timeout -Sy uboot-tools rsync git networkmanager modemmanager mobile-broadband-provider-info usb_modeswitch python3 openssh docker; do
    echo "failed to install packages. retrying..."
    sleep 3
done

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

log "generate boot.ini"
cat <<EOF > $rootmount/boot/boot.ini
ODROIDC-UBOOT-CONFIG

# Possible screen resolutions
# Uncomment only a single Line! The line with setenv written.
# At least one mode must be selected.

# setenv m "480x320p60hz"	# 480x320
# setenv m "480x800p60hz"	# 480x800
# setenv m "vga"          	# 640x480
# setenv m "480p"         	# 720x480
# setenv m "576p"         	# 720x576
# setenv m "800x480p60hz" 	# 800x480
# setenv m "800x600p60hz" 	# 800x600
# setenv m "1024x600p60hz"	# 1024x600
# setenv m "1024x768p60hz"	# 1024x768
# setenv m "1360x768p60hz" 	# 1360x768
# setenv m "1440x900p60hz"	# 1440x900
# setenv m "1600x900p60hz"	# 1600x900
# setenv m "1680x1050p60hz"	# 1680x1050
# setenv m "720p"         	# 720p 1280x720
# setenv m "800p"         	# 1280x800
# setenv m "sxga"         	# 1280x1024
# setenv m "1080i50hz"          # 1080I@50Hz
# setenv m "1080p24hz"          # 1080P@24Hz
# setenv m "1080p50hz"          # 1080P@50Hz
setenv m "1080p"                # 1080P@60Hz
# setenv m "1920x1200"    	# 1920x1200

# HDMI DVI Mode Configuration
setenv vout_mode "hdmi"
# setenv vout_mode "dvi"
# setenv vout_mode "vga"

# HDMI BPP Mode
setenv m_bpp "32"
# setenv m_bpp "24"
# setenv m_bpp "16"

# Monitor output
# Controls if HDMI PHY should output anything to the monitor
setenv monitor_onoff "false" # true or false

# HDMI Hotplug Force (HPD)
# 1 = Enables HOTPlug Detection
# 0 = Disables HOTPlug Detection and force the connected status
setenv hpd "0"

# CEC Enable/Disable (Requires Hardware Modification)
# 1 = Enables HDMI CEC
# 0 = Disables HDMI CEC
setenv cec "0"

# PCM5102 I2S Audio DAC
# PCM5102 is an I2S Audio Dac Addon board for ODROID-C1+
# Uncomment the line below to __ENABLE__ support for this Addon board.
# setenv enabledac "enabledac"

# UHS Card Configuration
# Uncomment the line below to __DISABLE__ UHS-1 MicroSD support
# This might break boot for some brand models of cards.
setenv disableuhs "disableuhs"

# Disable VPU (Video decoding engine, Saves RAM!!!)
# 0 = disabled
# 1 = enabled
setenv vpu "0"

# Disable HDMI Output (Again, saves ram!)
# 0 = disabled
# 1 = enabled
setenv hdmioutput "0"

# Default Console Device Setting
# setenv condev "console=ttyS0,115200n8"        # on serial port
# setenv condev "console=tty0"                    # on display (HDMI)
setenv condev "console=tty0 console=ttyS0,115200n8"   # on both

# Enable/Disable ODROID-VU7 Touchscreen
setenv disable_vu7 "false" # false

# CPU Max Frequency
# Possible Values: 96 192 312 408 504 600 720 816
# 1008 1200 1320 1488 1536 1632 1728 and 1824
setenv max_freq "1536"
# setenv max_freq "1632"
# setenv max_freq "1728"
# setenv max_freq "1824"

###########################################

if test "\${hpd}" = "0"; then setenv hdmi_hpd "disablehpd=true"; fi
if test "\${cec}" = "1"; then setenv hdmi_cec "hdmitx=cecf"; fi
if test "\${disable_vu7}" = "false"; then setenv hid_quirks "usbhid.quirks=0x0eef:0x0005:0x0004"; fi

# Boot Arguments
setenv bootargs "root=UUID=$(partuuid $rootpart) rootwait ro \${condev} no_console_suspend fsck.repair=yes vdaccfg=0xa000 logo=osd1,loaded,0x7900000,720p,full dmfc=3 cvbsmode=576cvbs hdmimode=\${m} m_bpp=\${m_bpp} vout=\${vout_mode} \${disableuhs} \${hdmi_hpd} \${hdmi_cec} \${enabledac} monitor_onoff=\${monitor_onoff} max_freq=\${max_freq} \${hid_quirks} fsck.repair=yes net.ifnames=0"

# Booting
fatload mmc 0:1 0x21000000 uImage
fatload mmc 0:1 0x22000000 uInitrd
fatload mmc 0:1 0x21800000 meson8b_odroidc.dtb
fdt addr 21800000

if test "\${vpu}" = "0"; then fdt rm /mesonstream; fdt rm /vdec; fdt rm /ppmgr; fi

if test "\${hdmioutput}" = "0"; then fdt rm /mesonfb; fi

bootm 0x21000000 0x22000000 0x21800000"
EOF

log "generate fstab"
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
