### Set-up Odroid Image Builder Devices:

1. Download images for C1+ and XU4 - 
```bash
wget https://odroid.in/ubuntu_16.04lts/ubuntu-16.04.3-minimal-odroid-c1-20170914.img.xz -O stage0_c1+.img.xz
wget https://odroid.in/ubuntu_16.04lts/ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img.xz -O stage0_xu4.img.xz
```
2. Extract, and dd on sd
```bash
unxz stage0_c1+.img.xz
unxz stage0_xu4.img.xz
sudo dd if=stage0_c1+.img of=/dev/sdX bs=10M
sudo sync
sudo dd if=stage0_xu4.img of=/dev/sdX bs=10M
sudo sync
```
3. Mount sd card on C1+ and XU4 and boot, **without** network. 
4. After the system shutsdown automatically the first time, reboot, **without** network. 
5. Disable **unattended-upgrades**
```bash
apt-get -y purge unattended-upgrades
```
6. Set Host-name 
```bash
hostnamectl set-hostname builder"$(cat /proc/cpuinfo | grep Hardware | cut -d ":" -f 2 | sed "s/\ //g")"
```
7. Reboot
8. Connect to Ethernet network
9. Update packages, install new packages -
```bash
apt-get update
apt-get -y upgrade
apt-get -y install git
```
10. Reboot.
11. Clone repo in /root/
```bash
git clone https://github.com/waggle-sensor/waggle_image.git
```
12. Finish setting up build machine -
```bash
cd waggle_image/bin/
./setup-build-machine
```
13. Copy credentials. 
