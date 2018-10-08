<!--
waggle_topic=IGNORE
-->

# How to Add Packages to Base image
Ubuntu, debian, or pip packages can be added and installed when building base image for Waggle system. 

## Add package to the build system
_NOTE: before adding, please use `config/get-dependencies` to make sure the package being added does not exist_

There are two cases of adding a package,
1) The package is natively available from Ubuntu system such that the build system can reach

Use `add-dependency` under `config`,

```
$ cd config
# TYPE can be one of [apt, python2, python3, deb]
$ ./add-dependency PACKAGE_NAME TYPE
```

2) The package is not reachable from Ubuntu system or a custom (modified) package needs to be installed

Place the package under `var/cache/apt/archives` if the package can be installed by `apt` or `dpkg`.<br>
Place the package under `var/cache/pip3/archives` if the package can be installed by `pip3`<br>
And then, do
```
$ cd config
# TYPE can be one of [apt, python2, python3, deb]
# IMPORTANT: PACKAGE_NAME INCLUDES EXTENSION (e.g., v4l2-0.2.tar.gz), NOT JUST v4l2
$ ./add-dependency PACKAGE_NAME TYPE
```

## Add packages to base image
Once all necessary packages are added to build system, you can configure a base image with the packages you select. To do,

```
$ cd config
# List of dependencies can be created manually or extended from existing base images
# Retrieve dependencies from 2.9.0-1 EP base image
$ EXISTING_DEPENDENCY_LIST=$(./get-build-dependencies --ep --version=2.9.0 --revision=1 --architecture=armv7l)
# Add package PACKAGE_A:TYPE (e.g., usbtop:apt)
$ EXISTING_DEPENDENCY_LIST=$EXISTING_DEPENDENCY_LIST,PACKAGE_NAME_A:TYPE
# Create uuid
$ UUID=$(uuidgen)
# For Nodecontroller use nc in element, ep for Edge Processor
$ ./add-base --element=[nc, ep] --architecture=armv7l --dependencies=$EXISTING_DEPENDENCY_LIST --date=2018-03-30 --uuid=$UUID
# Print if the base is added correctly
$ ./get-bases -c
...
7 Edge Processor (armv7l) 2018-03-30 - 77c1857d-4ce5-4b24-b15c-4925baca7059:
htop:apt,iotop:apt,iftop:apt,bwm-ng:apt,screen:apt,git:apt,python-dev:apt,python-pip:apt,python3-dev:apt,python3-pip:apt,dosfstools:apt,parted:apt,bash-completion:apt,v4l-utils:apt,network-manager:apt,usbutils:apt,nano:apt,stress-ng:apt,rabbitmq-server:apt,python-psutil:apt,python3-psutil:apt,fswebcam:apt,alsa-utils:apt,portaudio19-dev:apt,libavcodec-ffmpeg56:apt,libavformat-ffmpeg56:apt,libavutil-ffmpeg54:apt,libc6:apt,libcairo2:apt,libgdk-pixbuf2.0-0:apt,libglib2.0-0:apt,libpng12-0:apt,libstdc++6:apt,libswscale-ffmpeg3:apt,zlib1g:apt,libhdf5-10:apt,libjasper1:apt,libvtk6.2:apt,tabulate:python3,pika:python3,tinydb:python3,pyaudio:python3,numpy:python3,OpenCV-3.4.1-armv7l-dev.deb:deb,OpenCV-3.4.1-armv7l-libs.deb:deb,OpenCV-3.4.1-armv7l-main.deb:deb,OpenCV-3.4.1-armv7l-python.deb:deb,lsof:apt,piexif:python3,libv4l-dev:apt,libdc1394-22:apt,libgtk2.0-0:apt,v4l2-0.2.tar.gz:python3,gcc-8-base_8-20180424-0ubuntu1~16.04.1_armhf.deb:deb,tensorflow-1.8.0-cp35-none-any.whl:python3,libc6_2.23-0ubuntu10_armhf.deb:deb,libgcc1_1%3a8-20180424-0ubuntu1~16.04.1_armhf.deb:deb,libstdc++6_8-20180424-0ubuntu1~16.04.1_armhf.deb:deb,mali-fbdev:apt
```
