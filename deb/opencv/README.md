# Opencv 3.2.0 library along with a opencv 3.2.0 contrib (extra modules) and python3 interface

The opencv libraries are compiled in 32-bit ARM architecture. The libraries require some dependencies...

```
libavcodec-ffmpeg56 (>= 7:2.4) | libavcodec-ffmpeg-extra56 (>= 7:2.4)
libavformat-ffmpeg56 (>= 7:2.4)
libavutil-ffmpeg54 (>= 7:2.4)
libc6 (>= 2.4)
libcairo2 (>= 1.2.4)
libgcc1 (>= 1:4.0)
libgdk-pixbuf2.0-0 (>= 2.22.0)
libglib2.0-0 (>= 2.31.8)
libgtk-3-0 (>= 3.0.0)
libpng12-0 (>= 1.2.13-4)
libstdc++6 (>= 5.2)
libswscale-ffmpeg3 (>= 7:2.4)
zlib1g (>= 1:1.1.4)

# to install these in one line
apt-get install libavcodec-ffmpeg56 libavformat-ffmpeg56 libavutil-ffmpeg54 libc6 libcairo2 libgcc1 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libpng12-0 libstdc++6 libswscale-ffmpeg3 zlib1g
```

To install the opencv libraries...

```bash
dpkg -i Opencv-unknown-${ARCH}-*.deb

# install all dependencies (if the depencencies are not yet installed)
apt-get update
apt-get install -f
apt-get autoremove

# install numpy for python3 wrapper library
pip3 install numpy
```

# Compiling and making opencv packages

- In order to compile opencv and make debian packages additional cmake options are needed.

```bash
cd /OPENCV/SOURCE/DIR
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D BUILD_PACKAGE=ON \
    -D CPACK_BINARY_DEB:BOOL=ON \
    -D INSTALL_PYTHON_EXAMPLES=ON \
    -D INSTALL_C_EXAMPLES=OFF \
    -D OPENCV_EXTRA_MODULES_PATH=/PATH/TO/opencv_contrib-3.2.0/modules \
    -D PYTHON_EXECUTABLE=/usr/bin/python3 \
    -D BUILD_EXAMPLES=ON ..
```

- After the `cmake` command is executed, make sure that `CPackConfig.cmake` file contains correct package version; incorrect or unknown version may result in failure of installation. In CPackConfig.make find `CPACK_PACKAGE_VERSION` and change the value from "unknown" to "3.2.0".

- Run `make package` (with superuser)
- Check `Opencv-unknown-${ARCH}-*.deb` packages exist

# Notes
* The package enables use of OpenCL, but OpenCL libraries need to be installed separately from this packages. For c++ developers, add the path of OpenCL libraries to LD_LIBRARY_PATH variable and for python developers do the following

```bash
$ python3
>>> import sys
>>> sys.path.append('/PATH/TO/OPENCL/')
>>> import cv2
>>> cv2.ocl.haveOpenCL()
True
>>> cv2.ocl.setUseOpenCL()
>>> cv2.ocl.useOpenCL()
True
```
