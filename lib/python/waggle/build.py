import glob
import os
import subprocess
import sys
import time

def run_command(cmd, die=1):
    '''
    Will throw exception on execution error.
    '''
    print("execute: %s" % cmd)
    try:
        child = subprocess.Popen(['/bin/bash', '-c', cmd])
        child.wait()
    except Exception as e:
        print("Error: %s" % str(e))
        if not die:
            return -1
        sys.exit(1)
    if die and child.returncode != 0:
        print("Commmand exited with return code other than zero: %s" % str(child.returncode))
        sys.exit(1)

    return child.returncode

def run_command_f(cmd):
    '''
    Execute, wait, ignore error
    '''
    print("execute: %s" % cmd)
    try:
        child = subprocess.Popen(['/bin/bash', '-c', cmd])
        child.wait()
    except Exception:
        pass

def get_output(cmd):
    '''
    Execute, get STDOUT
    '''
    print("execute: %s" % cmd)
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()[0]


def write_file(filename, content):
    print("writing file "+filename)
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



def used_device_minors():
  device_minor_used={}

  # list devices: ls -latr /dev/loop[0-9]*
  # find minor number: stat -c %T /dev/loop2
  for device in glob.glob('/dev/loop[0-9]*'):
      print "device: ", device
      minor=os.minor(os.stat(device).st_rdev)
      print "device minor: ", minor
      device_minor_used[minor]=1
  return device_minor_used


def min_used_minor(device_minor_used):
    for i in range(1,50):
        print(i)
        if not i in device_minor_used:
            return i


def create_loop_devices():
  # dict of minors that are already used
  device_minor_used = used_device_minors()
  print device_minor_used

  for device in ['/dev/loop0p1', '/dev/loop0p2', '/dev/loop1p1', '/dev/loop1p2']:
      if not os.path.exists(device):
          # each loop device needs a different minor number.
          new_minor = min_used_minor(device_minor_used)
          # mknod [OPTION]... NAME TYPE [MAJOR MINOR]
          run_command_f('mknod -m 0660 {} b 7 {}'.format(device, new_minor))
          device_minor_used[new_minor]=1



def losetup(loopdev, file, offset=0):
    """
    Create single loop device
    """
    offset_option = ''

    if offset:
        offset_option = '-o %d ' % (offset)

    run_command('losetup %s %s %s' % (offset_option, loopdev, file))




def attach_loop_devices(filename, device_number, start_block_data):
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
        print("start_block_data: ", start_block_data)

    start_block_boot_str = get_output("fdisk -lu {0} | grep '{0}1' | awk '{{print $2}}'".format(filename))
    start_block_boot=int(start_block_boot_str)
    print("start_block_boot: ", start_block_boot)

    offset_boot=start_block_boot*512
    print("offset_boot: ", offset_boot)

    offset_data=start_block_data*512
    print("offset_data: ", offset_data)

    # create loop device for disk
    losetup(loop_device, filename)

    time.sleep(1)
    # create loop device for boot partition
    losetup(loop_partition_1, loop_device, offset_boot)
    # create loop device for root partition
    losetup(loop_partition_2, loop_device, offset_data)

    return start_block_boot, start_block_data


def detach_loop_devices():
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
    odroid_model_raw = get_output('cat /proc/cpuinfo | grep Hardware | grep -o "[^ ]*$"').rstrip()
    print("Detected device: %s" % odroid_model_raw)

    odroid_model = ''
    if odroid_model_raw == "ODROID-XU3":
      # The XU4 is actually a XU3.
      odroid_model = 'odroid-xu3'
    elif odroid_model_raw == "ODROIDC":
      odroid_model = 'odroid-c1'
    else:
      print("Could not detect ODROID model. (%s)" % odroid_model)
      return None

    return odroid_model

