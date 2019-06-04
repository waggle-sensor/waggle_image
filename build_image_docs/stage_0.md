### `Stage 0` image:

The raw Ubuntu minimal image available from [hardkernel](https://odroid.in/ubuntu_16.04lts/) is a raw disk image with the rootfs 
set to about 1.5GB partition. 

The latest minimal Ubuntu images released by Hardkernel to be used as `Stage 0` images are -

  * [Node Controller (Odroid C1+)](https://odroid.in/ubuntu_18.04lts/C0_C1/ubuntu-18.04.1-3.10-minimal-odroid-c1-20180802.img.xz)
  * [Edge Processor (Odroid XU4)](https://odroid.in/ubuntu_18.04lts/XU3_XU4_MC1_HC1_HC2/ubuntu-18.04.1-4.14-minimal-odroid-xu4-20181203.img.xz)

Download the images in a temporary directory on Linux Computer where you have a minimum of ~5GB of free disk space and sudo access. 

#### Download Images for C1+ and XU4:
```bash
mkdir images
cd images
mkdir stage0
cd stage0
wget https://odroid.in/ubuntu_18.04lts/C0_C1/ubuntu-18.04.1-3.10-minimal-odroid-c1-20180802.img.xz -O stage0_c1+.img.xz
wget https://odroid.in/ubuntu_18.04lts/XU3_XU4_MC1_HC1_HC2/ubuntu-18.04.1-4.14-minimal-odroid-xu4-20181203.img.xz -O stage0_xu4.img.xz
```
