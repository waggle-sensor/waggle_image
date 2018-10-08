### Process:

The raw Ubuntu minimal image available from [hardkernel](https://odroid.in/ubuntu_16.04lts/) is a raw disk image with the rootfs set to about 1.5GB ext partition. Based on the current package list, the `Stage 0` image's rootfs should be extended to 2.1 GB. The process for it under Linux is described using an example C1+ image here (follow the same process for the XU4 image)-

#### 1. Pre-installation step-

```bash
sudo apt-get install gparted parted
cd <image directory where stage0 folder is located>
```

#### 2. Unzip the downloaded raw image-

```bash
mkdir -p stage1
cd stage1
cp ../stage0/stage0_c1+.img.xz .
unxz stage0_c1+.img.xz
mv stage0_c1+.img stage1_c1+.img
```

#### 3. Extend the image with 700MB of empty space-

```bash
dd if=/dev/zero bs=1M count=700 >> stage1_c1+.img
```

#### 4. Mount the Image using losetup-

```bash
sudo losetup $(losetup -f) stage1_c1+.img
```

Verify that the image is mounted and note down the loop number:

```bash
$losetup -l | grep "stage1_c1+.img\|SIZELIMIT"
NAME       SIZELIMIT OFFSET AUTOCLEAR RO BACK-FILE
/dev/loop3         0      0         0  0 /home/rajesh/images/stage1/stage1_c1+.img
```

In this example, the device is `/dev/loop3`

#### 5. Expand the partition to occupy the empty space-

##### 5.1 GUI Method-

```bash
gparted /dev/loop3
```

This would open a gui window, where you drag the occupied space to occupy the *grey* unallocated space. Once the 
unallocated space has been occupied, the gparted window can be closed.

#### 5.2 Command line Method-
```bash
sudo parted --script /dev/loop3 resizepart 2 100%
sudo e2fsck -f /dev/loop3p2
sudo resize2fs /dev/loop3p2
```

#### 7. Unmount the loop devices-

```bash
sudo losetup -d /dev/loop3
```

#### 8. Now, check whether the image has the new extended partition-

```bash
fdisk -l stage1_c1+.img
```

It should list two image under the *device* column.

#### 9. Lastly, compresss the image to the *xz* extension for use by the waggle image creation scripts

```bash
xz -1 stage1_c1+.img
```

### Script:
Steps 3 to 9 are coded in the script below for easy image creation. Replace `image_file="stage1_c1+.img"` with appropriate file name.

```bash
#!/bin/bash
set -e
image_file="stage1_c1+.img"
dd if=/dev/zero bs=1M count=700 >> $image_file
available_device=$(losetup -f)
sudo losetup $available_device $image_file
losetup -l | grep "$image_file\|SIZELIMIT"
sudo parted --script $available_device resizepart 2 100%
sudo e2fsck -f $available_device"p2"
sudo resize2fs $available_device"p2"
sudo losetup -d  $available_device
if [ `fdisk -l $image_file | awk '{print $1}' | grep "stage1" | wc -l` -eq 2 ];then
    echo "Success, now compressing image"
    xz -1 -f $image_file
    echo "Stage 1 image successfully created."
else 
    echo "Unsuccessful in creating Stage 1 image. Retry manually to check for errors."
fi
```
