<!--
waggle_topic=ignore
-->
## Linux images for Single Board Computers in Waggle Nodes: 

The waggle nodes currently use [Hardkernel](https://www.hardkernel.com/main/shop/good_list.php?lang=en) (HK) supplied [C1+](https://www.hardkernel.com/main/products/prdt_info.php?g_code=G143703355573) and [XU4](https://www.hardkernel.com/main/products/prdt_info.php?g_code=G143452239825) single board computers as Nodecontroller and Edge-processor respectively. These systems run a Linux operating system based on Ubuntu distribution. This repository deals with creating working versions of the Linux images (`Stage 3` below) for the C1+ and XU4 devices deployed in Waggle Nodes. 

### Image Building Steps:

The Linux images for the waggle SBCs is built in several stages, each creating a Linux image. The process is performed in stages as building new images does not always require the rebuilding all the preceeding stages. To begin, here are the various images - 

  1. [**Stage 0:**](https://github.com/waggle-sensor/waggle_image/blob/master/build_image_docs/stage_0.md) Fetch Ubuntu Minimal Image for the Hard Kernel Single Board Computer (SBC).  
  2. [**Stage 1:**](https://github.com/waggle-sensor/waggle_image/blob/master/build_image_docs/stage_1.md) Create expanded Image for C1+ and XU4 from `Stage 0`.
  3. **Stage 2:** Add new software packages to the `Stage 1`.
  4. **Stage 3:** Create deployable Image from `Stage 2` by adding waggle and project specific configurations and credentials. 

### Rebuilding Various Images: Why and when? 

1. A new Image build for C1+ and XU4 is started from `Stage 0` when HK releases a new Ubuntu Minimal Image (based on 
new Ubuntu release/kernel). This is followed by building `Stage 1`, `Stage 2` and `Stage 3` for the SBC. 
2. `Stage 3` is built for each project based on the configuration and credential requirements. 
3. `Stage 2` is built when new software packages are needed for the node.
4. `Stage 1` is built when `Stage 2`  cannot be built with existing `Stage 1` due to space constraints.

###  Building Images on an Odroid: 

#### Set-up an Odroid Node:

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
