# waggle_image

This repository contains scripts to create waggle disk images and scripts that serve basic functionality to use a waggle image.



## build_waggle_image.py
Builds waggle C1+ and XU3/4 images.


## change_partition_uuid.sh
Script to change UUID of the boot and root partitions.


## create_node_id.sh
Script to create a uniqie node identifier.


## install_dependencies.sh
Installs basic ubuntu packages needed on a waggle image.


# scripts dirctory

## detect_mac_address.sh
Detect MAC address of odroid device.

## detect_odroid_model.sh
Detect current model, e.g. C1+ vs XU3/4.

## fs_resize.sh
The initial waggle image on an SD-card or eMMC will have filesystem that does not use all available space. This script expands the file system.

## heartbeat.sh 
Generate a continious heartbeat on Odroid GPIO pins.

## remove_packages.sh
Part of the image build process. Removes unwanted packages from the stock ubuntu image.

## waggle-service.py
Script to control waggle services.

## waggle_epoch.sh
Script to retrive time from a beehive server.

## waggle_init.sh
The waggle init script.
