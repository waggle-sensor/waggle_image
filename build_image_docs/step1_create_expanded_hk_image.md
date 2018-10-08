### Hardkernel Odroid Image

Here, the process of building a Hardkernel Odroid Image has been described. The steps listed here are only needed, if any 
image after all the pre-processing has not been provided. This section can be thought of any auxillary section which 
can be skipped in future once the Waggle team decide to provide pre-configured images with all the modifications.

To perform the various steps listed below, download an odroid image from the 
[hardkernel](https://odroid.in/ubuntu_16.04lts/ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img.xz). The image provided 
on the hardkernel server is a raw image with the rootfs set to 1.5GB ext partition. 
For building the beehive-node, the partition size has to be expanded in order to install the 
required packages. The following steps describe the required steps for expanding the size of the 
partition. In order to follow the steps described below, the user needs administrator access to the computer as 
few steps require `sudo`.

1. Pre-installation step

```bash
sudo apt-get install gparted
wget https://odroid.in/ubuntu_16.04lts/ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img.xz
```

2. Unzip the downloaded raw image and move the compressed image to a backup directory

```bash
unxz -k ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img.xz
mkdir backup
mv ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img.xz backup/ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img.xz
```

3. Extend the image with 1GB of empty space

```bash
dd if=/dev/zero bs=1M count=1000 » ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img
```

4. Check for the loop device that are currently mounted, and find a loop device that is currently available.

```bash
losetup -l
```

If the output of the above command is nothing, then use the following command

```bash
losetup -f
```

This would return an output like `/dev/loop0`.

5. Mount the image onto the loop device obtained from above.

```bash
sudo losetup /dev/loop0 ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img
```

The documentation given on the github repository of waggle-image, above command is executed without `sudo`. While testing, 
it was found that this would not work without `sudo`.

6. Once the image has been mounted onto the loop device, use `gparted` to expand the partition to occupy the 
empty space.

```bash
gparted /dev/loop0
```

This would open a gui window, where you drag the occupied space to occupy the *grey* unallocated space. Once the 
unallocated space has been occupied, the gparted window can be closed.

7. Unmount the loop devices

```bash
sudo losetup -D
```

8. Now, check whether the image has the new extended partition.

```bash
fdisk -l ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img
```

It should list two image under the *device* column.

7. Lastly, compresss the image to the *xz* extension for use by the waggle image creation scripts

```bash
xz -1 ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img
```
