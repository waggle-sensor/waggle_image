

These instructions explain how to build an image that can be used to build new waggle images and explains how waggle images are build.

(Argonne internal only) If you want to upload the new images to the Argonne Waggle server, you will need the private ssh key. See optional section below first.

# Prepare SD-card to build waggle images

You will have to create one SD card for C1+ and one for XU4 or for whatever device want to build new waggle images.

Either use Odroid Ubuntu image or the Waggle Ubuntu image. You will need to change the UUID of the partitions of this image. You can use this script to change the UUIDs:

https://github.com/waggle-sensor/waggle_image/blob/master/change_partition_uuid.sh

Note that for changing the UUIDs the partitons cannot be mounted. You have to use Linux (not OSX) to use the script. You should be sure not use another Linux (e.g Odroid) that also uses these UUIDs. A Linux laptop is probably the best way to run the script and change the UUIDs on your new SD card.



# Build waggle images

In sceen session, start the build process:

```bash
screen -S build
git clone https://github.com/waggle-sensor/waggle_image.git
cd waggle_image/
python -u ./build_waggle_image.py 2>&1 | tee build.log
```




# Optional: Enable upload to web server (Argonne only !)


Copy the private ssh key into the root home directory and rename it:
```bash
/root/waggle-id_rsa
```


The build script will automatically upload the images if it finds the private key.


This is the local path where the images will be copied to:
```bash
/mcs/www.mcs.anl.gov/research/projects/waggle/downloads/waggle_images/
```


