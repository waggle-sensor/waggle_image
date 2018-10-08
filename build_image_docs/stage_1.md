### Process:

The raw Ubuntu minimal image available from [hardkernel](https://odroid.in/ubuntu_16.04lts/) is a raw disk image with the rootfs set to about 1.5GB ext partition. Based on the current package list, the `Stage 0` image's rootfs should be extended to 2.1 GB. The process for it under Linux is described using an example XU4 image here (follow the same process for the C1+ image)-

#### 1. Pre-installation step

```bash
sudo apt-get install gparted
cd <image directory where stage0 folder is located>
```

#### 2. Unzip the downloaded raw image and move the compressed image to a backup directory (example shows XU4 HK image)

```bash
mkdir -p stage1
cd stage1
cp ../stage0/stage0_c1+.img.xz .
unxz stage0_c1+.img.xz
mv stage0_c1+.img stage1_c1+.img
```

#### 3. Extend the image with 1GB of empty space

```bash
dd if=/dev/zero bs=1M count=700 » stage1_c1+.img
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
sudo losetup /dev/loop0 stage1_c1+.img
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
fdisk -l stage1_c1+.img
```

It should list two image under the *device* column.

#### 9. Lastly, compresss the image to the *xz* extension for use by the waggle image creation scripts

```bash
xz -1 stage1_c1+.img
```
