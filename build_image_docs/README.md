<!--
waggle_topic=ignore
-->
# Image Building Process:

Building a Linux Image for Waggle nodes involves a 4 step process - 
```
  1. Fetch Hardkernel Odroid Image - fetch file from Hardkernel image portal.  
  2. Expand Hardkernel Odroid Image  - mount and grow the hardkernel image to add new software packages. 
  3. Create Base Image - add the required software packages. 
  4. Create Waggle Image - add waggle specific repositories, tools and configure beehive-server details and add beehive-server certs 
```
# Steps: 

## 1. Fetch Hardkernel Odroid Image: 

The C1+ (Node Controller) and XU4 are built around the latest minimal Ubuntu image released by Hardkernel. The current version of the 
images are - 

  * [Node Controller](https://odroid.in/ubuntu_16.04lts/ubuntu-16.04.3-minimal-odroid-c1-20170914.img.xz)
  * [Edge Processor](https://odroid.in/ubuntu_16.04lts/ubuntu-16.04.3-4.14-minimal-odroid-xu4-20171213.img.xz)

## 2. Expand Hardkernel Odroid Image: 

The step by step process for creating the edpanded raw image is available [here](https://github.com/waggle-sensor/waggle_image/blob/master/expand_hardkernel_odroid_image.md.md). 
