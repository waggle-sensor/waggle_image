#!/usr/bin/python

import argparse
import commands
import os
import os.path
import shutil
import subprocess
import sys
import time

waggle_image_directory = os.path.dirname(os.path.abspath(__file__))
print("### Run directory for build_image.py: %s" % waggle_image_directory)
sys.path.insert(0, '%s/lib/python/' % waggle_image_directory)
from waggle.build import *


# To copy a new public image to the download webpage, copy the waggle-id_rsa ssh key to /root/.
# To generate a functional AoT image with private configuration, put id_rsa_waggle_aot_config and a clone of git@gith_Aub.com:waggle-sensor/private_config.git in /root

# One of the most significant modifications that this script does is setting static IPs. Nodecontroller and guest node have different static IPs.


print "usage: python -u ./build_waggle_image.py 2>&1 | tee build.log"

start_time = time.time()

debug=0 # skip chroot environment if 1

data_directory="/root"

report_file="/root/report.txt"

waggle_stock_url='http://www.mcs.anl.gov/research/projects/waggle/downloads/stock_images/'
base_images=   {
                'odroid-xu3' : {
                        'filename': "ubuntu-14.04lts-server-odroid-xu3-20150725.img",
                         'url': waggle_stock_url
                        },
                'odroid-c1' : {
                        'filename':"ubuntu-14.04.3lts-lubuntu-odroid-c1-20151020.img",
                        'url': waggle_stock_url
                    }
                }


create_b_image = 0 # will be 1 for XU3/4

change_partition_uuid_script = waggle_image_directory + '/change_partition_uuid.sh'   #'/usr/lib/waggle/waggle_image/change_partition_uuid.sh'

mount_point="/mnt/newimage"



is_extension_node = 0 # will be set automatically to 1 if an odroid-xu3 is detected !



if create_b_image and not os.path.isfile(change_partition_uuid_script):
    print(change_partition_uuid_script, " not found")
    sys.exit(1)



# install parted
if subprocess.call('hash partprobe > /dev/null 2>&1', shell=True):
    run_command('apt-get install -y parted')

# install pipeviewer
if subprocess.call('hash pv > /dev/null 2>&1', shell=True):
    run_command('apt-get install -y pv')


# clean up first
print("Unmounting lingering images.")
unmount_mountpoint(mount_point)


print("Detaching loop devices.")
time.sleep(3)
detach_loop_devices()


create_loop_devices()


odroid_model = detect_odroid_model()

if not odroid_model:
    sys.exit(1)


if odroid_model == "odroid-xu3":
    is_extension_node = 1
    create_b_image = 1


date_today=get_output('date +"%Y%m%d"').rstrip()

if is_extension_node:
    image_type = "extension_node"
else:
    image_type = "nodecontroller"


print "image_type: ", image_type

new_image_base="waggle-base-%s-%s-%s" % (image_type, odroid_model, date_today)
new_image_prefix="%s/%s" % (data_directory, new_image_base)
new_image="%s.img" % (new_image_prefix)
new_image_xz = new_image + '.xz'

os.chdir(data_directory)


try:
    base_image = base_images[odroid_model]['filename']
except:
    print "image %s not found" % (odroid_model)
    sys.exit(1)

base_image_xz = base_image + '.xz'

###### TIMING ######
init_setup_time = time.time()
print("Initial Setup Duration: %ds" % (init_setup_time - start_time))
####################

if not os.path.isfile(base_image_xz):
    run_command('wget '+ base_images[odroid_model]['url'] + base_image_xz)

###### TIMING ######
image_fetch_time = time.time()
print("Base Image Fetch Duration: %ds" % (image_fetch_time - init_setup_time))
####################

try:
    os.remove(new_image_xz)
except:
    pass

print("Copying file %s to %s ..." % (base_image_xz, new_image_xz))
shutil.copyfile(base_image_xz, new_image_xz)

###### TIMING ######
image_copy_time = time.time()
print("Base Image Copy Duration: %ds" % (image_copy_time - image_fetch_time))
####################

print("Uncompressing file %s ..." % new_image_xz)
run_command('unxz ' + new_image_xz)

###### TIMING ######
image_unpack_time = time.time()
print("New Image Unpacking Duration: %ds" % (image_unpack_time - image_copy_time))
####################

#
# LOOP DEVICES HERE
#

start_block_boot, start_block_data = attach_loop_devices(new_image, None, None)


time.sleep(3)
print "first filesystem check on /dev/loop0p2"
check_partition(0)


print "execute: mkdir -p "+mount_point
try:
    os.mkdir(mount_point)
except:
    pass


mount_mountpoint(0, mount_point)


# TODO remove this test
unmount_mountpoint(mount_point)
time.sleep(3)
detach_loop_devices()
time.sleep(2)
attach_loop_devices(new_image, None, start_block_data)
print "filesystem check on /dev/loop0p2 after first mount"
check_partition(0)


mount_mountpoint(0, mount_point)

###### TIMING ######
loop_mount_time = time.time()
print("Loop Mount Duration: %ds" % (loop_mount_time - image_copy_time))
####################

run_command('mkdir -p {0}/usr/lib/waggle && cd {0}/usr/lib/waggle && git clone https://github.com/waggle-sensor/waggle_image.git'.format(mount_point))

### Copy the image build script ###
shutil.copyfile('%s/scripts/configure_base.sh' % waggle_image_directory, '%s/root/configure_base.sh' % mount_point)
run_command('chmod +x %s/root/configure_base.sh' % mount_point)


###### TIMING ######
pre_chroot_time = time.time()
print("Additional Pre-chroot Setup Duration: %ds" % (pre_chroot_time - loop_mount_time))
####################

#
# CHROOT HERE
#

print "################### start of chroot ###################"

if debug == 0:
    run_command('chroot %s/ /bin/bash /root/configure_base.sh' % (mount_point))


print "################### end of chroot ###################"


###### TIMING ######
chroot_setup_time = time.time()
print("Chroot Node Setup Duration: %ds" % (chroot_setup_time - pre_chroot_time))
####################

#
# After changeroot
#


try:
    os.remove(new_image+'.report.txt')
except:
    pass

print "copy: ", mount_point+'/'+report_file, new_image+'.report.txt'

if os.path.exists(mount_point+'/'+report_file):
    shutil.copyfile(mount_point+'/'+report_file, new_image+'.report.txt')
else:
    print "file not found:", mount_point+'/'+report_file


"""
old_partition_size_kb=int(get_output('df -BK --output=size /dev/loop0p2 | tail -n 1 | grep -o "[0-9]\+"'))
print "old_partition_size_kb: ", old_partition_size_kb
"""


unmount_mountpoint(mount_point)
time.sleep(3)
detach_loop_devices()
time.sleep(3)
attach_loop_devices(new_image, None, start_block_data)
time.sleep(3)
print "filesystem check on /dev/loop0p2 after chroot"
check_partition(0)

time.sleep(3)


###### TIMING ######
post_chroot_time = time.time()
print("Additional Post-chroot Setup Duration: %ds" % (post_chroot_time - chroot_setup_time))
####################

"""
estimated_fs_size_blocks=int(get_output('resize2fs -P /dev/loop0p2 | grep -o "[0-9]*"') )

block_size=int(get_output('blockdev --getbsz /dev/loop0p2'))

estimated_fs_size_kb = estimated_fs_size_blocks*block_size/1024


# add 500MB
new_partition_size_kb = estimated_fs_size_kb + (1024*500)


# add 100MB
new_fs_size_kb = estimated_fs_size_kb + (1024*100)
"""

###### TIMING ######
expansion_time = time.time()
print("Partition Expansion Duration: %ds" % (expansion_time - post_chroot_time))
####################

# verify partition:
run_command('e2fsck -f -y /dev/loop0p2')


###### TIMING ######
check_time = time.time()
print("Partition Check Duration: %ds" % (check_time - expansion_time))
####################

"""
sector_size=int(get_output('fdisk -lu {0} | grep "Sector size" | grep -o ": [0-9]*" | grep -o "[0-9]*"'.format(new_image)))


front_size_kb = sector_size * start_block_data/ 1024

if new_partition_size_kb < old_partition_size_kb:

    print "new_partition_size_kb is smaller than old_partition_size_kb"

    # shrink filesystem (that does not shrink the partition!)
    run_command('resize2fs -p /dev/loop0p2 %sK' % (new_fs_size_kb))


    run_command('partprobe  /dev/loop0p2')

    time.sleep(3)

    ### fdisk (shrink partition)
    # fdisk: (d)elete partition 2 ; (c)reate new partiton 2 ; specify start position and size of new partiton

    run_command('echo -e "d\n2\nn\np\n2\n%d\n+%dK\nw\n" | fdisk %s' % (start_block_data, new_partition_size_kb, new_image))



    run_command('partprobe /dev/loop0p2')

    #set +e
    #resize2fs /dev/loop0p2
    #set -e

    # does not show the new size
    #fdisk -lu ${new_image}

    # shows the new size (-b for bytes)
    #partx --show /dev/loop0p2 (fails)

    time.sleep(3)

    run_command('e2fsck -n -f /dev/loop0p2')

    #e2fsck_ok=1
    #set +e
    #while [ ${e2fsck_ok} != "0" ] ; do
    #  e2fsck -f /dev/loop0p2
    #  e2fsck_ok=$?
    #  sleep 2
    #done
    #set -e

else:
    print "new_partition_size_kb is NOT smaller than old_partition_size_kb"
"""

###### TIMING ######
check2_time = time.time()
print("Conditional Partition Check Duration: %ds" % (check2_time - check_time))
####################

print "check boot partition"
run_command_f('fsck.vfat -py /dev/loop0p1')

detach_loop_devices()




"""
# add size of boot partition

combined_size_kb = new_partition_size_kb+front_size_kb
combined_size_bytes = (new_partition_size_kb + front_size_kb) * 1024

# from kb to mb
blocks_to_write = combined_size_kb/1024
"""

###### TIMING ######
check3_time = time.time()
print("Boot Partition Check Duration: %ds" % (check3_time - check2_time))
####################


"""
# write image to file
run_command('pv -per --width 80 --size %d -f %s | dd bs=1M iflag=fullblock count=%d | xz -1 --stdout - > %s.xz_part' % (combined_size_bytes, new_image, blocks_to_write, new_image))
"""

###### TIMING ######
image_write_time = time.time()
print("New Image Write Duration: %ds" % (image_write_time - check3_time))
####################

"""
# test if file was compressed correctly
run_command('unxz -t %s.xz_part' % format(new_image))
"""

try:
    os.remove(new_image_xz)
except:
    pass

"""
os.rename(new_image+'.xz_part',  new_image_xz)
"""

run_command('xz -1 %s' % new_image)


###### TIMING ######
bimage_time = time.time()
print("\"B\" Image Creation Duration: %ds" % (bimage_time - image_write_time))
####################

#
# Upload files to waggle download directory
#
if os.path.isfile( data_directory+ '/waggle-id_rsa'):
    remote_path = '/mcs/www.mcs.anl.gov/research/projects/waggle/downloads/waggle_images/base/'.format(image_type, odroid_model)
    scp_target = 'waggle@terra.mcs.anl.gov:' + remote_path
    run_command('md5sum $(basename {0}.xz) > {0}.xz.md5sum'.format(new_image) )


    cmd = 'scp -o "StrictHostKeyChecking no" -v -i {0}/waggle-id_rsa {1}.xz {1}.xz.md5sum {2}'.format(data_directory, new_image, scp_target)

    count = 0
    while 1:
        count +=1
        if (count >= 10):
            print "error: scp failed after 10 trys\n"
            sys.exit(1)

        cmd_return = 1
        print "execute: ", cmd
        try:
            child = subprocess.Popen(['/bin/bash', '-c', cmd])
            child.wait()
            cmd_return = child.returncode

        except Exception as e:
            print "Error: %s" % (str(e))
            cmd_return = 1

        if cmd_return == 0:
            break

        time.sleep(10)


    run_command('echo "{0}" > {1}/latest.txt'.format(new_image_base +".img.xz", data_directory))
    run_command('scp -o "StrictHostKeyChecking no" -i {0}/waggle-id_rsa {0}/latest.txt {1}/'.format(data_directory, scp_target))


    if os.path.isfile( new_image+'.report.txt'):
        run_command('scp -o "StrictHostKeyChecking no" -v -i {0}/waggle-id_rsa {1}.report.txt {2}'.format(data_directory, new_image,scp_target))


    if os.path.isfile( new_image+'.build_log.txt'):
        run_command('scp -o "StrictHostKeyChecking no" -v -i {0}/waggle-id_rsa {1}.build_log.txt {2}'.format(data_directory, new_image,scp_target))

###### TIMING ######
upload_time = time.time()
print("Image Upload Duration: %ds" % (upload_time - bimage_time))
####################

###### TIMING ######
end_time = time.time()
print("Build Duration: %ds" % (end_time - start_time))
####################
