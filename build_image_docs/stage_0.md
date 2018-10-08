### `Stage 0` image:

The raw Ubuntu minimal image available from [hardkernel] (https://odroid.in/ubuntu_16.04lts/) is a raw disk image with the rootfs 
set to about 1.5GB partition. 

The latest minimal Ubuntu images released by Hardkernel to be used as `Stage 0` images are -

  * [Node Controller](https://odroid.in/ubuntu_16.04lts/ubuntu-16.04.3-minimal-odroid-c1-20170914.img.xz)
  * [Edge Processor](https://odroid.in/ubuntu_16.04lts/ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img.xz)

Download the images in a temporary directory on Linux Computer where you have a minimum of ~5GB of free disk space and sudo access. 

#### Download Images:
```
$ mkdir images
$cd images
$mkdir stage0
$cd stage0
$wget https://odroid.in/ubuntu_16.04lts/ubuntu-16.04.3-minimal-odroid-c1-20170914.img.xz
$wget https://odroid.in/ubuntu_16.04lts/ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img.xz
```
