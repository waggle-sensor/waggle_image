#!/usr/bin/env python
import time, os, commands, subprocess, shutil, sys, glob
from subprocess import call, check_call
import os.path
import uuid


# To copy a new public image to the download webpage, copy the waggle-id_rsa ssh key to /root/. 
# To generate a functional AoT image with private configuration, put id_rsa_waggle_aot_config and a clone of git@github.com:waggle-sensor/private_config.git in /root

# One of the most significant modifications that this script does is setting static IPs. Nodecontroller and guest node have different static IPs.


print "usage: python -u ./build_waggle_image.py 2>&1 | tee build.log"

start_time = time.time()

debug=0 # skip chroot environment if 1

build_uuid = uuid.uuid1()

waggle_image_directory = os.path.dirname(os.path.abspath(__file__))
print("### Run directory for build_waggle_image.py: %s" % waggle_image_directory)
data_directory="/root"

uuid_file = '%s/build_uuid' % data_directory
with open(uuid_file, 'w') as uuid:
  uuid.write(str(build_uuid))

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

mount_point_A="/mnt/newimage_A"
mount_point_B="/mnt/newimage_B"



is_extension_node = 0 # will be set automatically to 1 if an odroid-xu3 is detected !



if create_b_image and not os.path.isfile(change_partition_uuid_script):
    print(change_partition_uuid_script, " not found")
    sys.exit(1)



nodecontroller_etc_network_interfaces_d ='''
# interfaces(5) file used by ifup(8) and ifdown(8)
# created by Waggle autobuild

auto lo eth0
iface lo inet loopback

iface eth0 inet static
        address 10.31.81.10
        netmask 255.255.255.0
        
'''


#set static IP
guest_node_etc_network_interfaces_d = '''\
# interfaces(5) file used by ifup(8) and ifdown(8)
# created by Waggle autobuild

auto lo eth0
iface lo inet loopback

iface eth0 inet static
      address 10.31.81.51
      netmask 255.255.255.0
      #gateway 10.31.81.10

'''





def run_command(cmd, die=1):
    '''
    Will throw exception on execution error.
    '''
    print "execute: %s" % (cmd) 
    try:
        child = subprocess.Popen(['/bin/bash', '-c', cmd])
        child.wait()
    except Exception as e:
        print "Error: %s" % (str(e)) 
        if not die:
            return -1
        sys.exit(1)
    if die and child.returncode != 0:
        print "Commmand exited with return code other than zero: %s" % (str(child.returncode)) 
        sys.exit(1)
        
    return child.returncode

def run_command_f(cmd):
    '''
    Execute, wait, ignore error
    '''
    print "execute: %s" % (cmd) 
    try:
        child = subprocess.Popen(['/bin/bash', '-c', cmd])
        child.wait()
    except Exception as e:
        pass

def get_output(cmd):
    '''
    Execute, get STDOUT
    '''
    print "execute: %s" % (cmd) 
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()[0]


def write_file(filename, content):
    print "writing file "+filename
    with open(filename, "w") as text_file:
        text_file.write(content)


def write_build_script(filename, node_script_filename):
  base_build_init_script_filename = waggle_image_directory + '/scripts/base_build_init.in'
  with open(base_build_init_script_filename) as script:
    init_script = script.read()

  abs_node_script_filename = waggle_image_directory + '/scripts/' + node_script_filename
  with open(abs_node_script_filename) as script:
    node_script = script.read()

  base_build_final_script_filename = waggle_image_directory + '/scripts/base_build_final.in'
  with open(base_build_final_script_filename) as script:
    final_script = script.read()

  write_file(filename, init_script+node_script+final_script)
            

def unmount_mountpoint(mp):
    for i in ['/proc', '/dev', '/sys', '']:
        while int(get_output('mount | grep '+mp+i+' | wc -l')) != 0:
            run_command_f('umount -d '+mp+i)
            time.sleep(3)
    time.sleep(3)
    


def mount_mountpoint(device, mp):
    run_command('mount /dev/loop%dp2 %s' % (device, mp))
    run_command('mount -o bind /proc %s/proc' % (mp))
    run_command('mount -o bind /dev  %s/dev' % (mp))
    run_command('mount -o bind /sys  %s/sys' % (mp))
    time.sleep(3)
    
    
def check_partition(device):
    run_command('e2fsck -f -y /dev/loop{}p2'.format(device))
    



def losetup(loopdev, file, offset=0):
    """
    Create single loop device
    """
    offset_option = ''
    
    if offset:
        offset_option = '-o %d ' % (offset)
        
    run_command('losetup %s %s %s' % (offset_option, loopdev, file))
    
    
    

def create_loop_devices(filename, device_number, start_block_boot, start_block_data):
    """
    Create loop devices for complete image and for the root partition
    startblock (optional) is the start of the second partition
    """
    # get partition start position
    #fdisk -lu ${base_image}
    
    loop_device = '/dev/loop'+str(device_number)
    loop_partition_1 = loop_device+'p1' # boot partition
    loop_partition_2 = loop_device+'p2' # data/root partition
    
    if not start_block_data:
        # example: fdisk -lu waggle-extension_node-odroid-xu3-20160601.img | grep "^waggle-extension_node-odroid-xu3-20160601.img2" | awk '{{print $2}}'
        start_block_data_str = get_output("fdisk -lu {0} | grep '{0}2' | awk '{{print $2}}'".format(filename))
        start_block_data=int(start_block_data_str)
        print "start_block_data: ", start_block_data

    start_block_boot_str = get_output("fdisk -lu {0} | grep '{0}1' | awk '{{print $2}}'".format(filename))
    start_block_boot=int(start_block_boot_str)
    print "start_block_boot: ", start_block_boot

    offset_boot=start_block_boot*512 
    print "offset_boot: ", offset_boot

    offset_data=start_block_data*512 
    print "offset_data: ", offset_data

    # create loop device for disk
    losetup(loop_device, filename)
    
    time.sleep(1)
    # create loop device for boot partition    
    losetup(loop_partition_1, loop_device, offset_boot)
    # create loop device for root partition    
    losetup(loop_partition_2, loop_device, offset_data)
    
    return start_block_boot, start_block_data


def destroy_loop_devices():
    for device in ('/dev/loop0', '/dev/loop1' ):
        for partition in ('p1', 'p2'):
            loop_device = device+partition
            while int(get_output('losetup '+loop_device+' | wc -l')) != 0:
                run_command_f('losetup -d '+loop_device)
                time.sleep(3)
        loop_device = device 
        while int(get_output('losetup '+loop_device+' | wc -l')) != 0:
            run_command_f('losetup -d '+loop_device)
            time.sleep(3)



def detect_odroid_model():
    odroid_model_raw=get_output("head -n 1 /media/boot/boot.ini | cut -d '-' -f 1 | tr -d '\n'")
    odroid_model=""
    
    # The XU4 is actually a XU3.
    if odroid_model_raw == "ODROIDXU":
        print "Detected device: %s" % (odroid_model_raw)
        if os.path.isfile('/media/boot/exynos5422-odroidxu3.dtb'):
            odroid_model="odroid-xu3"
            #is_extension_node = 1
        else:
            odroid_model="odroid-xu"
            print "Did not find the XU3/4-specific file /media/boot/exynos5422-odroidxu3.dtb."
            return None
            
    elif odroid_model_raw  == "ODROIDC":
        print "Detected device: %s" % (odroid_model)
        odroid_model="odroid-c1"
    else:
        print "Could not detect ODROID model. (%s)" % (odroid_model)
        return None
    
    return odroid_model
        


def min_used_minor(device_minor_used):
    for i in range(1,50):
        print i
        if not i in device_minor_used:
            return i
            
            
##################################################################################################################################################################################################################
##################################################################################################################################################################################################################
    


# clean up first

unmount_mountpoint(mount_point_A)

    
time.sleep(3)
destroy_loop_devices()



# list devices: ls -latr /dev/loop[0-9]*
# find minor number: stat -c %T /dev/loop2


# dict of minors that are already used
device_minor_used={}

for device in glob.glob('/dev/loop[0-9]*'):
    print "device: ", device
    minor=os.minor(os.stat(device).st_rdev)
    print "device minor: ", minor
    device_minor_used[minor]=1


print device_minor_used

for device in ['/dev/loop0p1', '/dev/loop0p2', '/dev/loop1p1', '/dev/loop1p2']:
    if not os.path.exists(device):
        # each loop device needs a different minor number.
        new_minor = min_used_minor(device_minor_used)
        run_command_f('mknod -m 0660 {} b 7 {}'.format(device, new_minor))
        device_minor_used[new_minor]=1



# install parted
if call('hash partprobe > /dev/null 2>&1', shell=True):
    run_command('apt-get install -y parted')

# install pipeviewer
if call('hash pv > /dev/null 2>&1', shell=True):
    run_command('apt-get install -y pv')



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

new_image_base="waggle-%s-%s-%s" % (image_type, odroid_model, date_today) 
new_image_prefix="%s/%s" % (data_directory, new_image_base)
new_image_a="%s.img" % (new_image_prefix)
new_image_a_compressed = new_image_a+'.xz'

new_image_b="%s_B.img" % (new_image_prefix)

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

if not os.path.isfile(base_image):
    run_command('unxz --keep '+base_image_xz)

###### TIMING ######
image_unpack_time = time.time()
print("Base Image Unpacking Duration: %ds" % (image_unpack_time - image_fetch_time))
####################

try:
    os.remove(new_image_a)
except:
    pass

print "Copying file %s to %s ..." % (base_image, new_image_a)
shutil.copyfile(base_image, new_image_a)

###### TIMING ######
image_copy_time = time.time()
print("Base Image Copy Duration: %ds" % (image_copy_time - image_unpack_time))
####################

#
# LOOP DEVICES HERE
#

start_block_boot, start_block_data = create_loop_devices(new_image_a, 0, None, None)



time.sleep(3)
print "first filesystem check on /dev/loop0p2"
check_partition(0)



print "execute: mkdir -p "+mount_point_A
try: 
    os.mkdir(mount_point_A)
except:
    pass


print "execute: mkdir -p "+mount_point_B
try: 
    os.mkdir(mount_point_B)
except:
    pass


mount_mountpoint(0, mount_point_A)


# TODO remove this test
unmount_mountpoint(mount_point_A)
time.sleep(3)
destroy_loop_devices()
time.sleep(2)
create_loop_devices(new_image_a, 0,  None, start_block_data)
print "filesystem check on /dev/loop0p2 after first mount"
check_partition(0)



mount_mountpoint(0, mount_point_A)

###### TIMING ######
loop_mount_time = time.time()
print("Loop Mount Duration: %ds" % (loop_mount_time - image_copy_time))
####################

shutil.copyfile(uuid_file, mount_point_A+uuid_file)

run_command('mkdir -p {0}/usr/lib/waggle && cd {0}/usr/lib/waggle && git clone https://github.com/waggle-sensor/waggle_image.git'.format(mount_point_A))

### Create the image build script ###
if is_extension_node:
    local_build_script_in = 'extension_node_build.in'
else:
    local_build_script_in = 'nodecontroller_build.in'
write_build_script('%s/root/build_image.sh' % (mount_point_A), local_build_script_in)

print "-------------------------\n"
with open('%s/root/build_image.sh' % (mount_point_A)) as local_build_script:
  for line in local_build_script:
    print(line)
print "-------------------------\n"

run_command('chmod +x %s/root/build_image.sh' % (mount_point_A))

configure_aot = False
if os.path.exists('/root/id_rsa_waggle_aot_config') and run_command('ssh -T git@github.com', die=False) == 1:
  configure_aot = True
  print "################### AoT Configuration Enabled ###################"


if configure_aot:
  try:
    # clone the private_config repository
    run_command('git clone git@github.com:waggle-sensor/private_config.git', die=False)

    # allow the node setup script to change the root password to the AoT password
    shutil.copyfile('/root/id_rsa_waggle_aot_config', '%s/root/id_rsa_waggle_aot_config' % (mount_point_A))
    shutil.copyfile('/root/private_config/encrypted_waggle_password', '%s/root/encrypted_waggle_password' % (mount_point_A))

    # allow the node the register in the field
    shutil.copyfile('/root/private_config/id_rsa_waggle_aot_registration', '%s/root/id_rsa_waggle_aot_registration' % (mount_point_A))
  except Exception as e:
    print("Error in private AoT configuration: %s" % str(e))
    pass


###### TIMING ######
pre_chroot_time = time.time()
print("Additional Pre-chroot Setup Duration: %ds" % (pre_chroot_time - loop_mount_time))
####################

#
# CHROOT HERE
#

print "################### start of chroot ###################"

if debug == 0:
    run_command('chroot %s/ /bin/bash /root/build_image.sh' % (mount_point_A))


print "################### end of chroot ###################"


###### TIMING ######
chroot_setup_time = time.time()
print("Chroot Node Setup Duration: %ds" % (chroot_setup_time - pre_chroot_time))
####################

# 
# After changeroot
#

if configure_aot:
  # install a copy of wvdial.conf with the AoT secret APN
  shutil.copyfile('/root/private_config/wvdial.conf', '%s/etc/wvdial.conf' % (mount_point_A))

  # remove temporary password setup files from image
  os.remove('%s/root/id_rsa_waggle_aot_config' % (mount_point_A))
  os.remove('%s/root/encrypted_waggle_password' % (mount_point_A))

  # remove the private_config repository
  shutil.rmtree('/root/private_config')
else:
  # copy the default, unconfigured wvdial.conf file
  shutil.copyfile(waggle_image_directory + '/device_rules/wwan_modems/wvdial.conf', '%s/etc/wvdial.conf' % (mount_point_A))


try:
    os.remove(new_image_a+'.report.txt')
except:
    pass

print "copy: ", mount_point_A+'/'+report_file, new_image_a+'.report.txt'

if os.path.exists(mount_point_A+'/'+report_file):
    shutil.copyfile(mount_point_A+'/'+report_file, new_image_a+'.report.txt')
else:
    print "file not found:", mount_point_A+'/'+report_file




if is_extension_node:
    write_file(mount_point_A+'/etc/network/interfaces', guest_node_etc_network_interfaces_d)
else:
    write_file(mount_point_A+'/etc/network/interfaces', nodecontroller_etc_network_interfaces_d)






old_partition_size_kb=int(get_output('df -BK --output=size /dev/loop0p2 | tail -n 1 | grep -o "[0-9]\+"'))
print "old_partition_size_kb: ", old_partition_size_kb


unmount_mountpoint(mount_point_A)
time.sleep(3)
destroy_loop_devices()
time.sleep(3)
create_loop_devices(new_image_a, 0,  None, start_block_data)
time.sleep(3)
print "filesystem check on /dev/loop0p2 after chroot"
check_partition(0)

time.sleep(3)


###### TIMING ######
post_chroot_time = time.time()
print("Additional Post-chroot Setup Duration: %ds" % (post_chroot_time - chroot_setup_time))
####################

estimated_fs_size_blocks=int(get_output('resize2fs -P /dev/loop0p2 | grep -o "[0-9]*"') )

block_size=int(get_output('blockdev --getbsz /dev/loop0p2'))

estimated_fs_size_kb = estimated_fs_size_blocks*block_size/1024


# add 500MB
new_partition_size_kb = estimated_fs_size_kb + (1024*500)


# add 100MB
new_fs_size_kb = estimated_fs_size_kb + (1024*100)

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

sector_size=int(get_output('fdisk -lu {0} | grep "Sector size" | grep -o ": [0-9]*" | grep -o "[0-9]*"'.format(new_image_a)))


front_size_kb = sector_size * start_block_data/ 1024

if new_partition_size_kb < old_partition_size_kb: 

    print "new_partition_size_kb is smaller than old_partition_size_kb"

    # shrink filesystem (that does not shrink the partition!)
    run_command('resize2fs -p /dev/loop0p2 %sK' % (new_fs_size_kb))


    run_command('partprobe  /dev/loop0p2')

    time.sleep(3)

    ### fdisk (shrink partition)
    # fdisk: (d)elete partition 2 ; (c)reate new partiton 2 ; specify start position and size of new partiton

    run_command('echo -e "d\n2\nn\np\n2\n%d\n+%dK\nw\n" | fdisk %s' % (start_block_data, new_partition_size_kb, new_image_a))



    run_command('partprobe /dev/loop0p2')

    #set +e
    #resize2fs /dev/loop0p2
    #set -e

    # does not show the new size
    #fdisk -lu ${new_image_a}

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

###### TIMING ######
check2_time = time.time()
print("Conditional Partition Check Duration: %ds" % (check2_time - check_time))
####################

print "check boot partition"
run_command_f('fsck.vfat -py /dev/loop0p1')

destroy_loop_devices()




# add size of boot partition

combined_size_kb = new_partition_size_kb+front_size_kb
combined_size_bytes = (new_partition_size_kb + front_size_kb) * 1024

# from kb to mb
blocks_to_write = combined_size_kb/1024

###### TIMING ######
check3_time = time.time()
print("Boot Partition Check Duration: %ds" % (check3_time - check2_time))
####################


# write image to file
run_command('pv -per --width 80 --size %d -f %s | dd bs=1M iflag=fullblock count=%d | xz -1 --stdout - > %s.xz_part' % (combined_size_bytes, new_image_a, blocks_to_write, new_image_a))

###### TIMING ######
image_write_time = time.time()
print("New Image Write Duration: %ds" % (image_write_time - check3_time))
####################

# test if file was compressed correctly
run_command('unxz -t %s.xz_part' % format(new_image_a))

try:
    os.remove(new_image_a_compressed)
except:
    pass

os.rename(new_image_a+'.xz_part',  new_image_a_compressed)


###### TIMING ######
compression_check_time = time.time()
print("New Image Compression Check Duration: %ds" % (compression_check_time - image_write_time))
####################




# create second dd with different UUIDs
if create_b_image:
    
    
    if not os.path.isfile(change_partition_uuid_script):
        print change_partition_uuid_script, " not found"
        sys.exit(1)
    
    try:
        os.remove(new_image_b+'.part')
    except:
        pass
    
    #copy image a to b
    run_command('pv -per --width 80 --size %d -f %s | dd bs=1M iflag=fullblock count=%d  > %s.part' % (combined_size_bytes, new_image_a, blocks_to_write, new_image_b))
    
    # delete old b if it exists
    try:
        os.remove(new_image_b)
    except:
        pass

    try:
        os.remove(new_image_b+'.xz')
    except:
        pass

    
    os.rename(new_image_b+'.part',  new_image_b)
    
    # create loop device
    create_loop_devices(new_image_b, 1,  None, None)
    
    # change UUID
    run_command(change_partition_uuid_script+ ' /dev/loop1')
    
    
    # the recovery image on the eMMC needs space:
    
    new_image_a_compressed_size = os.path.getsize(new_image_a_compressed)
    new_image_a_compressed_size_mb = new_image_a_compressed_size / 1048576
    
    # increase partition size again
    run_command('dd if=/dev/zero bs=1MiB of={} conv=notrunc oflag=append count={}'.format(new_image_b, new_image_a_compressed_size_mb+50))
    time.sleep(1)
    
    
    # verify file system
    run_command('e2fsck -f -y /dev/loop1p2')
    
    time.sleep(1)
    
    # make filesystem use new space
    run_command('resize2fs /dev/loop1p2')
    time.sleep(1)
    
    
    # compress 
    run_command('xz -1 '+new_image_b)
    
    
    #run_command('pv -per --width 80 --size %d -f %s | dd bs=1M iflag=fullblock count=%d | xz -1 --stdout - > %s.xz_part' % (combined_size_bytes, new_image_a, blocks_to_write, new_image_b))
    #os.rename(new_image_b+'.xz_part',  new_image_b+'.xz')    


###### TIMING ######
bimage_time = time.time()
print("\"B\" Image Creation Duration: %ds" % (bimage_time - compression_check_time))
####################

#
# Upload files to waggle download directory
#
if not configure_aot and os.path.isfile( data_directory+ '/waggle-id_rsa'):
    remote_path = '/mcs/www.mcs.anl.gov/research/projects/waggle/downloads/waggle_images/{0}/{1}/'.format(image_type, odroid_model)
    scp_target = 'waggle@terra.mcs.anl.gov:' + remote_path
    run_command('md5sum $(basename {0}.xz) > {0}.xz.md5sum'.format(new_image_a) ) 
    
    
    cmd = 'scp -o "StrictHostKeyChecking no" -v -i {0}/waggle-id_rsa {1}.xz {1}.xz.md5sum {2}'.format(data_directory, new_image_a, scp_target)
    
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
  
    if os.path.isfile( new_image_b+'.xz'):
        # upload second image with different UUID's
        run_command( 'md5sum $(basename {0}.xz) > {0}.xz.md5sum'.format(new_image_b))
        run_command('scp -o "StrictHostKeyChecking no" -v -i {0}/waggle-id_rsa {1}.xz {1}.xz.md5sum {2}'.format(data_directory, new_image_b, scp_target))

  
    if os.path.isfile( new_image_a+'.report.txt'): 
        run_command('scp -o "StrictHostKeyChecking no" -v -i {0}/waggle-id_rsa {1}.report.txt {2}'.format(data_directory, new_image_a,scp_target))
      
  
    if os.path.isfile( new_image_a+'.build_log.txt'): 
        run_command('scp -o "StrictHostKeyChecking no" -v -i {0}/waggle-id_rsa {1}.build_log.txt {2}'.format(data_directory, new_image_a,scp_target))

###### TIMING ######
upload_time = time.time()
print("Image Upload Duration: %ds" % (upload_time - bimage_time))
####################

###### TIMING ######
end_time = time.time()
print("Build Duration: %ds" % (end_time - start_time))
####################
