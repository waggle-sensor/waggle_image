



If you want to upload the new images to the Argonne Waggle server, you will need the private ssh key. See instruction below first.


# build image

In sceen session, start the build process:

```bash
screen -S build
cd waggle_image/
python -u ./build_waggle_image.py 2>&1 | tee build.log
```




# upload to web server


Copy the private ssh key into the root home directory and rename it:
```bash
/root/waggle-id_rsa
```


The build script will automatically upload the images if it finds the private key.


This is the local path where the images will be copied to:
```bash
/mcs/www.mcs.anl.gov/research/projects/waggle/downloads/waggle_images/
```


