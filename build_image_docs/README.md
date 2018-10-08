<!--
waggle_topic=ignore
-->
## Linux images for Single Board Computers in Waggle Nodes: 

The waggle nodes currently use [Hardkernel(HK)](https://www.hardkernel.com/main/shop/good_list.php?lang=en) supplied [C1+](https://www.hardkernel.com/main/products/prdt_info.php?g_code=G143703355573) and [XU4](https://www.hardkernel.com/main/products/prdt_info.php?g_code=G143452239825) single board computers as Nodecontroller and Edge-processor respectively. These systems run a Linux operating system based on Ubuntu distribution. This repository deals with creating working versions of the Linux images (`Stage 3` below) for the C1+ and XU4 devices deployed in Waggle Nodes. 

### Image Building Steps:

The Linux images for the waggle SBCs is built in several stages, each outputting a Linux image. The process is performed in stages as building new images does not always require the rebuilding all the preceeding stages. To begin, here are the various images - 

  1. **Stage 0:** Fetch Ubuntu Minimal Image for the Hard Kernel Single Board Computer (SBC).  
  2. **Stage 1:** Create expanded Image for C1+ and XU4 from `Stage 0`.
  3. **Stage 2:** Add new software packages to the `Stage 1`.
  4. **Stage 3:** Create deployable Image from `Stage 2` by adding waggle and project specific configurations and credentials. 

### Rebuilding Various Images: 

1. A new Image build for C1+ and XU4 is started from `Stage 0` when HK releases a new Ubuntu Minimal Image (based on 
new Ubuntu release/kernel). This is followed by building `Stage 1`, `Stage 2` and `Stage 3` for the SBC. 
2. `Stage 3` is built for each project based on the configuration and credential requirements. 
3. `Stage 2` is built when new software packages are needed for the node.
4. `Stage 1` is built when `Stage 2`  cannot be built with existing `Stage 1` due to space constraints.

 
