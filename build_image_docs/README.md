<!--
waggle_topic=ignore
-->
## Linux images for Single Board Computers in Waggle Nodes: 

The waggle nodes currently use [Hardkernel](https://www.hardkernel.com/main/shop/good_list.php?lang=en) (HK) supplied [C1+](https://www.hardkernel.com/main/products/prdt_info.php?g_code=G143703355573) and [XU4](https://www.hardkernel.com/main/products/prdt_info.php?g_code=G143452239825) single board computers as Nodecontroller and Edge-processor respectively. These systems run a Linux operating system based on Ubuntu distribution. This repository deals with creating working versions of the Linux images (`Stage 3` below) for the C1+ and XU4 devices deployed in Waggle Nodes. 

### Image Building Steps:

The Linux images for the waggle SBCs is built in several stages, each creating a Linux image. The process is performed in stages as building new images does not always require the rebuilding all the preceeding stages. To begin, here are the various images - 

  1. [**Stage 0:**](https://github.com/waggle-sensor/waggle_image/blob/master/build_image_docs/stage_0.md) Fetch Ubuntu Minimal Image for the Hard Kernel Single Board Computer (SBC).  
  2. [**Stage 1:**](https://github.com/waggle-sensor/waggle_image/blob/master/build_image_docs/stage_1.md) Create expanded Image for C1+ and XU4 from `Stage 0`.
  3. [**Stage 2:**](https://github.com/waggle-sensor/waggle_image/blob/master/build_image_docs/stage_2.md) Add new software packages to the `Stage 1`.
  4. [**Stage 3:**](https://github.com/waggle-sensor/waggle_image/blob/master/build_image_docs/stage_3.md) Create deployable Image from `Stage 2` by adding waggle and project specific configurations and credentials. 

### Rebuilding Various Images: Why and when? 

1. A new Image build for C1+ and XU4 is started from `Stage 0` when HK releases a new Ubuntu Minimal Image (based on 
new Ubuntu release/kernel). This is followed by building `Stage 1`, `Stage 2` and `Stage 3` for the SBC. 
2. `Stage 3` is built for each project based on the configuration and credential requirements. 
3. `Stage 2` is built when new software packages are needed for the node.
4. `Stage 1` is built when `Stage 2`  cannot be built with existing `Stage 1` due to space constraints.

###  Building Images on an Odroid: 

  1. The [first step](https://github.com/waggle-sensor/waggle_image/blob/master/build_image_docs/builder-odroids.md) in the process, a one-time set-up, is standing up the builder Odroids. 
  2. Step 2: Build images using scripts in [bin directory](https://github.com/waggle-sensor/waggle_image/tree/master/bin) - 
  For C1+ (using the latest Tag  and latest Stage 2 build):
  ```bash
  cd /root/waggle_images/bin
  ./rebuild-image-space && ./build-stage0-image && ./build-stage1-image && ./build-stage2-image a9024069-8e15-4946-a8da-2bc9dad8ccb0 && ./build-stage3-image 2.9.0
  ```
  For XU4 (using the latest Tag  and latest Stage 2 build):
  ```bash
  cd /root/waggle_images/bin
  ./rebuild-image-space && ./build-stage0-image && ./build-stage1-image && ./build-stage2-image bf3fe9c2-cb3a-11e8-935c-e7c6eb8f24f5 && ./build-stage3-image 2.9.0
  ```
