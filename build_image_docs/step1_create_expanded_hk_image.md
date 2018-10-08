### Process:

The raw Ubuntu minimal image available from [hardkernel] (https://odroid.in/ubuntu_16.04lts/) is a raw disk image with the rootfs set to about 1.5GB ext partition. This image when used as the starting point for waggle-base image building will fail as the process will run out of space in the raw image for installing packages. It is hence required that the root partition of the raw image be extended to 2.1 GB (at the time of this writing, may be further more as we add more packages). The process for it under Linux is described using an example XU4 image here-

#### 0. Fetch Hardkernel Odroid Image: 

The C1+ (Node Controller) and XU4 are built around the latest minimal Ubuntu image released by Hardkernel. The current version of the 
images are - 

  * [Node Controller](https://odroid.in/ubuntu_16.04lts/ubuntu-16.04.3-minimal-odroid-c1-20170914.img.xz)
  * [Edge Processor](https://odroid.in/ubuntu_16.04lts/ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img.xz)

#### 1. Pre-installation step

```bash
sudo apt-get install gparted
```

#### 2. Unzip the downloaded raw image and move the compressed image to a backup directory (example shows XU4 HK image)

```bash
unxz -k ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img.xz
mkdir backup
mv ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img.xz backup/ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img.xz
```

#### 3. Extend the image with 1GB of empty space

```bash
dd if=/dev/zero bs=1M count=1000 » ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img
```

#### 4. Check for the loop device that are currently mounted, and find a loop device that is currently available.

```bash
losetup -l
```

If the output of the above command is nothing, then use the following command

```bash
losetup -f
```

This would return an output like `/dev/loop0`.

#### 5. Mount the image onto the loop device obtained from above.

```bash
sudo losetup /dev/loop0 ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img
```

The documentation given on the github repository of waggle-image, above command is executed without `sudo`. While testing, 
it was found that this would not work without `sudo`.

#### 6. Once the image has been mounted onto the loop device, use `gparted` to expand the partition to occupy the empty space.

```bash
gparted /dev/loop0
```

This would open a gui window, where you drag the occupied space to occupy the *grey* unallocated space. Once the 
unallocated space has been occupied, the gparted window can be closed.

#### 7. Unmount the loop devices

```bash
sudo losetup -D
```

#### 8. Now, check whether the image has the new extended partition.

```bash
fdisk -l ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img
```

It should list two image under the *device* column.

#### 9. Lastly, compresss the image to the *xz* extension for use by the waggle image creation scripts

```bash
xz -1 ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img
```
