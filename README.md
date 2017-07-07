# Repository Summary

This repository contains scripts to create waggle disk images. The root of the repository contains the following scripts:


* build-base-image    		_Builds waggle C1+ and XU3/4 base images that contain all of the Ubuntu and Python dependencies._
* build-waggle-image  		_Builds waggle C1+ and XU3/4 Waggle images that contain the Waggle software without the AoT specific configuration._
* bless-image			_Adds the AoT specific configuration to a mounted image._
* change-partition-uuid		_Changes the partition UUIDs for an unmounted image._


# How to Build a Base Image

Use the `build-base-image` script to bulid a base image which contains all of the Ubuntu and Python package dependencies for the Waggle software. The `--build-dir=<build-dir>` option allows one to set the directory in which the stock Odroid image will be downloaded and the new base image will be assembled.

After the build process finishes, the new base image will be compressed into a `.xz` file. If in addition the `waggle-id_rsa` private key is in the build directory, the compressed base image will be uploaded to http://www.mcs.anl.gov/research/projects/waggle/downloads/waggle_images/base/.

Note that the name of the last base image to be uploaded is also pushed to the latest.txt file in the above mentioned downloads directory.

# How to Build a Waggle Image

The `build-waggle-image` script downloads the latest base image and builds a Waggle image on top of it. To download the correct base image, the script obtains the timestamp from the name of the last uploaded base image listed in the latest.txt file mentioned in the previous section. Use the optional `--branch=<branch>` option to specify a particular shared branch across all of the Waggle node software repositories (i.e. `core`, `plugin_manager`, `nodecontroller`, and `edge_processor`). Use the `--help` option to explore additional options such as automatic compression and uploading similar to what happens during base image building.

After the image has been built, attach a USB memory card reader with either an SD or eMMC. Use `blkid` or some other method to determine what the device name is of the memory card (for example, `/dev/sda`). The image can be written to the memory care with the following command:

`dd if=<build-dir>/<image-file> of=<card-device> bs=500M status=progress`

## Configuring the Image to Work with the Array of Things

At this point the image will not be configured to register with a particular cloud server such as Beehive or interoperate with the AoT AT&T celular network. The image will also also have default passwords for the `waggle` and `root` users (both `waggle`). To configure the image to work with the Array of Things infrastructure we must 'bless' the image.

To bless the image, first place the AoT configuration private key (`id_rsa_waggle_aot_config`) in `/root` or some other secure location on your build Odroid. Then mount the data partition (second partition) to some directory, say, `/media/rootfs`. For example,

`mount /dev/sda2 /media/rootfs`.

Then execute the following command to configure the image for AoT (assumes the key is in `/root`):

`bless-image /media/rootf`

To select a different key path use the `--key=<key-path>` option. One can also change some of the default configuration steps for, say, partially configuring a node for a collaborator using various options (use `--help` to obtain a list).

Be sure to unmount the data partition when you're done:

`umount /media/rootfs`

## Changing the Partition UUIDs

To avoid a UUID collision between an SD and eMMC attached to the same Odroid, one of the card's partition UUIDs must be changed. To do this use the following command (assuming the card device is /dev/sda):

`change-partition-uuid /dev/sda`

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
