#!/usr/bin/env python
import time, os, commands, subprocess, shutil, sys, glob
from subprocess import call, check_call
import os.path


# One of the most significant modifications that this script does is setting static IPs. Nodecontroller and guest node have different static IPs.


print "usage: python -u ./build_waggle_image.py 2>&1 | tee build.log"


debug=1 # skip chroot environment if 1

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

change_partition_uuid_script = os.path.abspath(os.path.curdir) + '/change_partition_uuid.sh'   #'/usr/lib/waggle/waggle_image/change_partition_uuid.sh'

mount_point_A="/mnt/newimage_A"
mount_point_B="/mnt/newimage_B"



is_extension_node = 0 # will be set automatically to 1 if an odroid-xu3 is detected !



if create_b_image and not os.path.isfile(change_partition_uuid_script):
    print change_partition_uuid_script, " not found"
    sys.exit(1)

if not os.path.isfile( data_directory+ '/waggle-id_rsa'):
    print data_directory+ '/waggle-id_rsa not found. Disable this check in the script to continue anyway.' 
    sys.exit(1)


###                              ###
###  Script for chroot execution ###
###                              ###

#TODO move everything into scripts

base_build_init_script = '''\
#!/bin/bash
set -x
set -e

###locale
locale-gen "en_US.UTF-8"
dpkg-reconfigure locales

### timezone 
echo "Etc/UTC" > /etc/timezone 
dpkg-reconfigure --frontend noninteractive tzdata

# because of "Failed to fetch http://ports.ubuntu.com/... ...Hash Sum mismatch"
#rm -rf /var/lib/apt/lists/*
touch -t 1501010000 /var/lib/apt/lists/*
rm -f /var/lib/apt/lists/partial/*
apt-get clean
apt-get update



mkdir -p /etc/waggle/
echo "10.31.81.10" > /etc/waggle/node_controller_host

# Packages are installed via waggle_image/install_dependencies.sh
set -e


# Every waggle image needs this repository
mkdir -p /usr/lib/waggle/
cd /usr/lib/waggle/
if [ ! -e waggle_image ] ; then
  # this repor should already have been checked out earlier.
  git clone https://github.com/waggle-sensor/waggle_image.git
fi
cd waggle_image

./scripts/remove_packages.sh
./install_dependencies.sh
./configure


# make sure serial console requires password
sed -i -e 's:exec /bin/login -f root:exec /bin/login:' /bin/auto-root-login

'''


base_build_final_script='''\


### kill X processses
set +e
killall -u lightdm -9



### username
export odroid_exists=$(id -u odroid > /dev/null 2>&1; echo $?)
export waggle_exists=$(id -u waggle > /dev/null 2>&1; echo $?)

# rename existing user odroid to waggle
if [ ${{odroid_exists}} == 0 ] && [ ${{waggle_exists}} != 0 ] ; then
  echo "I will kill all processes of the user \"odroid\" now."
  sleep 1
  killall -u odroid -9
  sleep 2

  set -e

  #This will change the user's login name. It requires you logged in as another user, e.g. root
  usermod -l waggle odroid

  # real name
  usermod -c "waggle user" waggle

  #change home directory
  usermod -m -d /home/waggle/ waggle

  set +e
fi

# create new user waggle
if [ ${{odroid_exists}} != 0 ] && [ ${{waggle_exists}} != 0 ] ; then
  
  
  set -e
  
  adduser --disabled-password --gecos "" waggle

  # real name
  usermod -c "waggle user" waggle


  set +e
fi


# verify waggle user has been created
set +e
id -u waggle > /dev/null 2>&1
if [ $? -ne 0 ]; then 
  echo "error: unix user waggle was not created"
  exit 1 
fi


# check if odroid group exists
getent group odroid > /dev/null 2>&1
if [ $? -eq 0 ]; then 
  echo "\"odroid\" group exists, will rename it to \"waggle\""
  groupmod -n waggle odroid || exit 1 
else
  getent group waggle > /dev/null 2>&1 
  if [ $? -eq 0 ]; then 
    echo "Neither waggle nor odroid group exists. Will create odroid group."
    addgroup waggle
  fi
fi



# verify waggle group has been created
getent group waggle > /dev/null 2>&1 
if [ $? -ne 0 ]; then 
  echo "error: unix group waggle was not created"
  exit 1 
fi

echo "adding user waggle to group waggle"
adduser waggle waggle

echo "sudo access for user waggle"
adduser waggle sudo

set -e


### disallow root access
sed -i 's/\(PermitRootLogin\) .*/\\1 no/' /etc/ssh/sshd_config

### default password
echo waggle:waggle | chpasswd
echo root:waggle | chpasswd

### Remove ssh host files. Those will be recreated by the /etc/rc.local script by default.
rm -f /etc/ssh/ssh_host*


# set AoT_key
mkdir -p /home/waggle/.ssh/
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCsYPMSrC6k33vqzulXSx8141ThfNKXiyFxwNxnudLCa0NuE1SZTMad2ottHIgA9ZawcSWOVkAlwkvufh4gjA8LVZYAVGYHHfU/+MyxhK0InI8+FHOPKAnpno1wsTRxU92xYAYIwAz0tFmhhIgnraBfkJAVKrdezE/9P6EmtKCiJs9At8FjpQPUamuXOy9/yyFOxb8DuDfYepr1M0u1vn8nTGjXUrj7BZ45VJq33nNIVu8ScEdCN1b6PlCzLVylRWnt8+A99VHwtVwt2vHmCZhMJa3XE7GqoFocpp8TxbxsnzSuEGMs3QzwR9vHZT9ICq6O8C1YOG6JSxuXupUUrHgd AoT_key" >> /home/waggle/.ssh/authorized_keys
chmod 700 /home/waggle/.ssh/
chmod 600 /home/waggle/.ssh/authorized_keys
chown waggle:waggle /home/waggle/.ssh/ /home/waggle/.ssh/authorized_keys


### mark image for first boot 

touch /root/first_boot
touch /root/do_resize
touch /root/do_recovery

rm -f /etc/network/interfaces.d/*
rm -f /etc/udev/rules.d/70-persistent-net.rules 

### for paranoids
echo > /root/.bash_history
echo > /home/waggle/.bash_history

set +e
# monit accesses /dev/null even after leaving chroot, which makes it impossible unmount the new image
/etc/init.d/monit stop
killall monit
sleep 3


### create report

echo "image created: " > {0}
date >> {0}
echo "" >> {0}
uname -a >> {0}
echo "" >> {0}
cat /etc/os-release >> {0}
dpkg -l >> {0}



'''

# guest node specific code
extension_node_build_script=base_build_init_script + '''\

echo -e "10.31.81.10\tnodecontroller" >> /etc/hosts

apt-get --no-install-recommends install -y network-manager
apt-get autoclean
apt-get autoremove -y




mkdir -p /usr/lib/waggle/
cd /usr/lib/waggle/

git clone --recursive https://github.com/waggle-sensor/plugin_manager.git
sleep 1
cd /usr/lib/waggle/plugin_manager/
scripts/install_dependencies.sh


'''+base_build_final_script

# node controller specific code
nodecontroller_build_script=base_build_init_script + '''\

echo -e "10.31.81.51\textensionnode1 extensionnode" >> /etc/hosts
for i in 2 3 4 5 ; do
  echo -e "10.31.81.5${{i}}\textensionnode${{i}}" >> /etc/hosts
done


echo -e "127.0.0.1\tnodecontroller" >> /etc/hosts

set +e


### get nodecontroller repo
if [ ! -d /usr/lib/waggle/nodecontroller ] ; then
  mkdir -p /usr/lib/waggle/
  git clone --recursive https://github.com/waggle-sensor/nodecontroller.git /usr/lib/waggle/nodecontroller
else  
  cd /usr/lib/waggle/nodecontroller
  git pull
fi

cd /usr/lib/waggle/nodecontroller
./scripts/install_dependencies.sh


### get plugin_manager repo
cd /usr/lib/waggle/
git clone --recursive https://github.com/waggle-sensor/plugin_manager.git
cd /usr/lib/waggle/plugin_manager/
scripts/install_dependencies.sh


'''+base_build_final_script


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

if not os.path.isfile(base_image_xz):
    run_command('wget '+ base_images[odroid_model]['url'] + base_image_xz)


if not os.path.isfile(base_image):
    run_command('unxz --keep '+base_image_xz)


try:
    os.remove(new_image_a)
except:
    pass

print "Copying file %s to %s ..." % (base_image, new_image_a)
shutil.copyfile(base_image, new_image_a)


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


run_command('mkdir -p {0}/usr/lib/waggle && cd {0}/usr/lib/waggle && git clone https://github.com/waggle-sensor/waggle_image.git'.format(mount_point_A))

if is_extension_node:
    local_build_script = extension_node_build_script.format(report_file)
else: 
    local_build_script = nodecontroller_build_script.format(report_file)


write_file( mount_point_A+'/root/build_image.sh',  local_build_script)

print "-------------------------\n"
print local_build_script
print "-------------------------\n"

run_command('chmod +x %s/root/build_image.sh' % (mount_point_A))

#
# CHROOT HERE
#

print "################### start of chroot ###################"

if debug == 0:
    run_command('chroot %s/ /bin/bash /root/build_image.sh' % (mount_point_A))


print "################### end of chroot ###################"


# 
# After changeroot
#
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


estimated_fs_size_blocks=int(get_output('resize2fs -P /dev/loop0p2 | grep -o "[0-9]*"') )

block_size=int(get_output('blockdev --getbsz /dev/loop0p2'))

estimated_fs_size_kb = estimated_fs_size_blocks*block_size/1024


# add 500MB
new_partition_size_kb = estimated_fs_size_kb + (1024*500)


# add 100MB
new_fs_size_kb = estimated_fs_size_kb + (1024*100)

# verify partition:
run_command('e2fsck -f -y /dev/loop0p2')


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

destroy_loop_devices()




# add size of boot partition

combined_size_kb = new_partition_size_kb+front_size_kb
combined_size_bytes = (new_partition_size_kb + front_size_kb) * 1024

# from kb to mb
blocks_to_write = combined_size_kb/1024


# write image to file
run_command('pv -per --width 80 --size %d -f %s | dd bs=1M iflag=fullblock count=%d | xz -1 --stdout - > %s.xz_part' % (combined_size_bytes, new_image_a, blocks_to_write, new_image_a))



try:
    os.remove(new_image_a_compressed)
except:
    pass

os.rename(new_image_a+'.xz_part',  new_image_a_compressed)





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


#
# Upload files to waggle download directory
#
if os.path.isfile( data_directory+ '/waggle-id_rsa'):
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
      
  

