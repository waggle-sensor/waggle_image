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

Determine what network the ODroid is connected to and identify the IP address of the device. This can be done by using `nmap -sn <ip_address_on_network>/24`, logging into your router and checking the DHCP allocation table.

Once you have identified the IP address of the ODroid, log into the device with `ssh root@<IP_address>`. The default password for the stock ODroid image is `odroid`. If security is a concern, the default password should be changed and ssh keys should be setup appropriately.

Alternatively you can simply attach a monitor and keyboard and login as root, again, with the default password of `odroid`. You may still need to copy files to the device. Get the IP address by running `ifconfig`.

## Install Dependencies

`apt install -y git curl`

`pip3 install tinydb`

## Clone the waggle_image Repository

In a location of your choosing, execute `git clone https://github.com/waggle-sensor/waggle_image.git`.

## Install Web and Private Config Repository Keys

**INTERNAL USE ONLY**

In order to upload the base image to the MCS Waggle website after building, the Waggle web ssh key file `waggle-id_rsa` must be installed in the build directory (the directory specified using the --build-dir option of the build scripts).

To access the Waggle private configuration repository, the deploy key file `id_rsa_waggle_aot_private_config` must be installed in `/root`. Execute `ssh -T -i /root/id_rsa_waggle_aot_config git@github.com` and answer `yes` when asked to add the host to the list of known hosts.

Consult a knowledgeable member of the Waggle team to obtain the above mentioned keys.

# Preparing a uSD Card

Attach a USB memory card reader with either an SD or eMMC. Use `blkid` or some other method to determine what the device name is of the memory card (for example, `/dev/sda`).

# How to Build a Base Image

Use the `build-base-image` script to bulid a base image listed in the build configuration database which contains all of the Ubuntu and Python package dependencies for the Waggle software. The `--build-dir=<build-dir>` option allows one to set the directory in which the stock Odroid image will be downloaded and the new base image will be assembled. The only non-option argument is the UUID of the base image. Use the `get-bases` script in the `config/` subdirectory of the waggle_image repository to get a list of the available base images. Be sure to use one with the 'armv7l' CPU architecture.

After the build process finishes, the new base image will be compressed into a `.xz` file. If, in addition, the `waggle-id_rsa` private key is in the build directory, the compressed base image will be uploaded to http://www.mcs.anl.gov/research/projects/waggle/downloads/waggle_images/base/.

Note that the name of the last base image to be uploaded is also pushed to the latest.txt file in the above mentioned downloads directory.

# How to Build a Waggle Image

The `build-waggle-image` script builds a Waggle image ontop of an existing base image. To determine the correct base image, the script queries the build configration database for the Node Controller and Edge Processor base images associated with the specified Waggle version. The `--node-controller` and `--edge-processor` options select for which node element to build the image. 

By default the script will query the database or the latest version and revision for the 'armv7l' architecture, but the options `--version` and `--revision` can be used to select any previous build that is recorded in the database. If the revision is 0, the master branch will be used for all of the software repositories (`core`, `nodecontroller`, `edge_processor`, and `plugin_manager`). If the revision is non-zero, the particular commit IDs associated with the build will be used.

To build an image from a branch, simply create a temporary branch of the waggle_image repository, add a revision of an appropriate Waggle version build using the `--branch` option of the `add-build` script, and run this script with the version and revision that match the new build configuration.

The default deployment configuration is 'Public'. This contains no organization-specific security keys, passwords, or configurations. To configure the image with a particular deployment configuration, use the `get-deployments` utility in the `config/` subdirectory of the waggle_image repository to get a list of available configurations. One can then use the `--deployment` option, passing the name of the deployment configuration (i.e. 'Public', 'AoT', etc...) as the options value. See the section above on installing the private configuration key.

The `--target=<disk_device>` option causes the image to be automatically burned to the disk specified by <disk_device>. If this option is used the deployment configuration will be applied only to the disk image, and not the image file that was built. This allows for the image file to be burned to a different disk for applying a different deployment configuration. The script `write-waggle-image` can be used for this purpose, although it has not currently been updated to take advantage of the build configuration database.

Use the `--help` option to explore additional options such as automatic compression and uploading similar to what happens during base image building.

To manually write an image to disk use the following command:

`dd if=<build-dir>/<image-file> of=<card-device> bs=500M status=progress`

## Manually Configuring the Image to Work with the Array of Things

_Note: the `bless-image` script has not currently been update to take advantage of the build configuration database._

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

# Docker Images

The scripts `build-base-docker-image` and `build-waggle-docker-image` can be used in a similar way to the disk image build scripts to create Docker images. _Currently the Docker build scripts do not support adding deployment configurations._

# OpenCV 3.2.0

Currently there are no OpenCV library and contrib packages that can be installed on the XU4 via APT. We must, therefore, manually build OpenCV Debian packages. The latest packages that we have tested with our code are committed to the repository under `var/cache/apt/archives/`. These are installed when building the XU4 base image along with the Ubuntu and Python dependencies.

## Dependencies

The opencv libraries are compiled with a 32-bit ARM architecture. The libraries require the following extra dependencies:

```
libavcodec-ffmpeg56 (>= 7:2.4) | libavcodec-ffmpeg-extra56 (>= 7:2.4)
libavformat-ffmpeg56 (>= 7:2.4)
libavutil-ffmpeg54 (>= 7:2.4)
libc6 (>= 2.4)
libcairo2 (>= 1.2.4)
libgcc1 (>= 1:4.0)
libgdk-pixbuf2.0-0 (>= 2.22.0)
libglib2.0-0 (>= 2.31.8)
libgtk-3-0 (>= 3.0.0)
libpng12-0 (>= 1.2.13-4)
libstdc++6 (>= 5.2)
libswscale-ffmpeg3 (>= 7:2.4)
zlib1g (>= 1:1.1.4)
```

To install these in one line,
`apt-get install libavcodec-ffmpeg56 libavformat-ffmpeg56 libavutil-ffmpeg54 libc6 libcairo2 libgcc1 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libpng12-0 libstdc++6 libswscale-ffmpeg3 zlib1g`

The `numpy` Python module is also required.

## Building the Packages

The following procedure can be used to compile OpenCV 3.2.0 and build Debian packages.

Run the following commands to initialize the build configuration:
```bash
cd <OPENCV_SOURCE_DIRECTORY>
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D BUILD_PACKAGE=ON \
    -D CPACK_BINARY_DEB:BOOL=ON \
    -D INSTALL_PYTHON_EXAMPLES=ON \
    -D INSTALL_C_EXAMPLES=OFF \
    -D OPENCV_EXTRA_MODULES_PATH=/PATH/TO/opencv_contrib-3.2.0/modules \
    -D PYTHON_EXECUTABLE=/usr/bin/python3 \
    -D BUILD_EXAMPLES=ON ..
```

After the `cmake` command is executed, make sure that `CPackConfig.cmake` file contains the correct package version. An incorrect or unknown version may result in failure of installation. In CPackConfig.make find `CPACK_PACKAGE_VERSION` and change the value from "unknown" to "3.2.0".

As root, run `make package`.

Check that the `Opencv-unknown-${ARCH}-*.deb` packages exist.

## OpenCL Support

The package enables use of OpenCL, but OpenCL libraries need to be installed separately from this packages. For c++ developers, add the path of OpenCL libraries to `LD_LIBRARY_PATH` variable and for python developers do the following

```bash
$ python3
>>> import sys
>>> sys.path.append('<OPENCL_PATH>')
>>> import cv2
>>> cv2.ocl.haveOpenCL()
True
>>> cv2.ocl.setUseOpenCL()
>>> cv2.ocl.useOpenCL()
True
```
