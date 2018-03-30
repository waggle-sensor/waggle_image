The raw Ubuntu minimal image available from [hardkernel] (https://odroid.in/ubuntu_16.04lts/) is a raw disk image with the rootfs 
set to about 1.5GB ext partition. This image when used as the starting point for waggle-base image building will fail as the process 
will run out of space in the raw image for installing packages. It is hence required that the root partition of the raw image be 
extended to 2.1 GB (at the time of this writing, may be further more as we add more packages). The process for it under Linux is 
described using an example XU4 image here- 

### Download raw image: 

```
$wget https://odroid.in/ubuntu_16.04lts/ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img.xz
$wget https://odroid.in/ubuntu_16.04lts/ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img.xz.md5sum
```
Check md5sum, and if it check out, 
### unzip image:

```
$unxz -k ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img.xz
$ls 
ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img.xz
ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img
```

### Extend the image with 1GB of empty space: 
```
$dd if=/dev/zero bs=1M count=1000 >> ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img
```

###  Check for loop devices currently mounted and find an available mount point:
```
$losetup -l
NAME       SIZELIMIT OFFSET AUTOCLEAR RO BACK-FILE
/dev/loop1         0      0         1  1 /var/lib/snapd/snaps/core_4017.snap
/dev/loop2         0      0         1  1 /var/lib/snapd/snaps/core_4110.snap
/dev/loop0         0      0         1  1 /var/lib/snapd/snaps/core_4206.snap
```

### Mount the new image, and probe the partitions: 
```
$losetup /dev/loop3 ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img
$partprobe /dev/loop3
```

### Use gparted to extend the second partition further into the 1GB empty space that follows it:
```
gparted /dev/loop3
```

### After finishing the extension, un-mount the loopback device:

```
$losetup -D /dev/loop3
```

### Check that the device has new extended root partition:

```
$ fdisk -l ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img
Disk ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img: 2.6 GiB, 2809135104 bytes, 5486592 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0x3cedfd53

Device                                               Boot  Start     End Sectors  Size Id Type
ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img1        2048  264191  262144  128M  c W95 FAT32 (LBA)
ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img2      264192 5486591 5222400  2.5G 83 Linux
```

### Finally compress the image for use by waggle image creation scripts: 
```
$ mv ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img.xz ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213_original.img.xz
$ xz -1 ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img
```

Use the newly created `ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img.xz` for bootstrapping the waggle image. 
