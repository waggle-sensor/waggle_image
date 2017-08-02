# Repository Summary

This repository contains scripts to create waggle disk images. The root of the repository contains the following scripts:


* build-base-image    		_Builds waggle C1+ and XU3/4 base images that contain all of the Ubuntu and Python dependencies._
* build-waggle-image  		_Builds waggle C1+ and XU3/4 Waggle images that contain the Waggle software without the AoT specific configuration._
* build-base-docker-image    		_Builds waggle C1+ and XU3/4 base Docker images that contain all of the Ubuntu and Python dependencies._
* build-waggle-docker-image  		_Builds waggle C1+ and XU3/4 Waggle Docker images that contain the Waggle software without the AoT specific configuration._
* bless-image			_Adds the AoT specific configuration to a mounted image._
* change-partition-uuid		_Changes the partition UUIDs for an unmounted image._
* mount-image  _Mount the specified .img file at the specified mount point and bind special system directories so that a chroot environment can connect to the network._
* unmount-image _Unmount the specified mount point after unbinding special system directories._
* mount-disk  _Mount the specified device at the specified mount point and bind special system directories so that a chroot environment can connect to the network._
* unmount-disk _Unmount the specified mount point after unbinding special system directories._
* rip-disk  _Produce a .img file from the specified disk device, only including the data inside the partition boundaries._
* write-waggle-image  _Write the latest image to a disk, optionally blessing it._
* santize-image  _(Experimental) remove all Waggle installation changes._
* upgrade-waggle  _(Experimental) call santize-image and then re-install the specified Waggle repositories and bless._

# How to Setup a Build Machine

ODroid images must be built on a device with the same CPU architecture, in other words they must be built on an ODroid. Currently the build scripts are written to detect the ODroid model, so there is a further restriction that C1+ and XU4 images must be built on a C1+ and XU4 respectively.

To setup an ODroid to be a build machine one must minimally 1) burn the stock Ubuntu image from Hardkernel, 2) boot the ODroid, 3) log into the ODroid, 4) install git and curl, 5) clone the waggle_image repository, and 6) install web upload and private configuration repository keys.

## Burn the Stock Ubuntu Image from Hardkernel

Dowload one of the following compressed image files depending on the ODroid model you are using as the build machine:
* http://www.mcs.anl.gov/research/projects/waggle/downloads/waggle_images/base/ubuntu-16.04-minimal-odroid-c1-20160817.img.xz
* http://www.mcs.anl.gov/research/projects/waggle/downloads/waggle_images/base/ubuntu-16.04-minimal-odroid-xu3-20160706.img.xz

Use the `unxz` utility to uncompress the image file.

Burn the image using `dd if=<image-file> of=<card-device> bs=500M status=progress`.

## Boot the Build Odroid

Insert the uSD card with the stock image that you burned in the above step. Remove any eMMC card that may be attached to the ODroid. If using an XU4, select the uSD to boot by either appropriately setting the boot select switch or shorting the white and black wires on XU4s modified for Array of Things nodes.

Connect the ODroid to the internet through the built-in Ethernet port.

Connect power to the ODroid to boot.

## Log Into the ODroid

Determine what network the ODroid is connected to and identify the IP address of the device. This can be done by using `nmap` or logging into your router and checking the DHCP allocation table.

Once you have identified the IP address of the ODroid, log into the device with `ssh root@<IP_address>`. The default password for the stock ODroid image is `odroid`. If security is a concern, the default password should be changed and ssh keys should be setup appropriately.

## Install Git and Curl

`apt install -y git curl`

## Clone the waggle_image Repository

In a location of your choosing, execute `git clone https://github.com/waggle-sensor/waggle_image.git`.

## Install Web and Private Config Repository Keys

**INTERNAL USE ONLY**

In order to upload the base image to the MCS Waggle website after building, the Waggle web ssh key file `waggle-id_rsa` must be installed in the build directory (the directory specified using the --build-dir option of the build scripts).

To access the Waggle private configuration repository, the deploy key file `id_rsa_waggle_aot_private_config` must be installed in `/root`. Execute `ssh -T -i /root/id_rsa_waggle_aot_config git@github.com` and answer `yes` when asked to add the host to the list of known hosts.

Consult a knowledgeable member of the Waggle team to obtain the above mentioned keys.

# How to Build a Base Image

Use the `build-base-image` script to bulid a base image which contains all of the Ubuntu and Python package dependencies for the Waggle software. The `--build-dir=<build-dir>` option allows one to set the directory in which the stock Odroid image will be downloaded and the new base image will be assembled.

After the build process finishes, the new base image will be compressed into a `.xz` file. If in addition the `waggle-id_rsa` private key is in the build directory, the compressed base image will be uploaded to http://www.mcs.anl.gov/research/projects/waggle/downloads/waggle_images/base/.

Note that the name of the last base image to be uploaded is also pushed to the latest.txt file in the above mentioned downloads directory.

# How to Build a Waggle Image

The `build-waggle-image` script downloads the latest base image and builds a Waggle image on top of it. To download the correct base image, the script obtains the timestamp from the name of the last uploaded base image listed in the latest.txt file mentioned in the previous section. Use the optional `--branch=<branch>` option to specify a particular shared branch across all of the Waggle node software repositories (i.e. `core`, `plugin_manager`, `nodecontroller`, and `edge_processor`).

The `--target=<disk_device>` option causes the image to be automatically burned to the disk specified by <disk_device>. The `--bless` option causes this disk to be automatically configured to operate as an Array of Things node. Use the `--help` option to explore additional options such as automatic compression and uploading similar to what happens during base image building.

After the image has been built, attach a USB memory card reader with either an SD or eMMC. Use `blkid` or some other method to determine what the device name is of the memory card (for example, `/dev/sda`). The image can be written to the memory care with the following command:

`dd if=<build-dir>/<image-file> of=<card-device> bs=500M status=progress`

## Manually Configuring the Image to Work with the Array of Things

If the `--bless` option was not used, or an otherwise 'unblessed' copy of the image was burned to a disk, the disk will not be configured to register with the AoT Beehive cloud server or interoperate with the AoT AT&T celular network. The image will also have default passwords for the `waggle` and `root` users (both `waggle`). To configure the image to work with the Array of Things infrastructure we must 'bless' the image.

To bless the image, first place the AoT configuration private key (`id_rsa_waggle_aot_config`) in `/root` or some other secure location on your build Odroid. Then mount the data partition (second partition) to some directory, say, `/media/rootfs`. For example,

`mount /dev/sda2 /media/rootfs`.

Then execute the following command to configure the image for AoT (assumes the key is in `/root`):

`bless-image /media/rootf`

To select a different key path use the `--key=<key-path>` option. One can also change some of the default configuration steps for, say, partially configuring a node for a collaborator using various options (use `--help` to obtain a list).

Be sure to unmount the data partition when you're done:

`umount /media/rootfs`

## Changing the Partition UUIDs

To avoid a UUID collision between an SD and eMMC attached to the same Odroid, one of the card's partition UUIDs must be changed. Normally this is not a problem as the file system on the uSD card is copied to the eMMC and the eMMC partition UUID is changed automatically when the Waggle software first initializes. To change the UUID manually, use the following command (assuming the card device is /dev/sda):

`change-partition-uuid /dev/sda`

# Making Copies of Blessed Disk Images

To make multiple copies of a blessed disk image, the uSD card can be replicated using a card duplicator. Alternatively the blessed disk image can be ripped using the `rip-disk` utility and burned manually as needed. Yet another option is to mount an unblessed image using the `mount-image` utility, bless it using the `bless-image` utility, and then transfer the blessed image file to another computer using `scp`. In this last case, you may want to consider compressing the image using, for example, `xz`.
