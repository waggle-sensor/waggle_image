#!/usr/bin/python3

import argparse
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

debug=0 # skip chroot environment if 1

def get_base_image_filename(build_directory, odroid_model):
    is_extension_node = 0 # will be set automatically to 1 if an odroid-xu3 is detected !


    if odroid_model == "odroid-xu3":
        is_extension_node = 1
        create_b_image = 1


    date_today=get_output('date +"%Y%m%d"').rstrip().decode()

    if is_extension_node:
        image_type = "extension_node"
    else:
        image_type = "nodecontroller"

    print("image_type: ", image_type)

    base_image_base="waggle-base-%s-%s-%s" % (image_type, odroid_model, date_today)
    base_image_prefix="%s/%s" % (build_directory, base_image_base)
    return "%s.img" % (base_image_prefix)

def setup_mount_point(mount_point):
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

def mount_new_image(base_image, mount_point, odroid_model):
    waggle_stock_url='http://www.mcs.anl.gov/research/projects/waggle/downloads/waggle_images/base/'
    stock_images=   {
                    'odroid-xu3' : {
                            'filename': "ubuntu-16.04-minimal-odroid-xu3-20160706.img",
                             'url': waggle_stock_url
                            },
                    'odroid-c1' : {
                            'filename':"ubuntu-16.04-minimal-odroid-c1-20160817.img",
                            'url': waggle_stock_url
                        }
                    }

    base_image_xz = base_image + '.xz'

    try:
        stock_image = stock_images[odroid_model]['filename']
    except:
        print("image %s not found" % (odroid_model))
        sys.exit(1)

    stock_image_xz = stock_image + '.xz'

    if not os.path.isfile(stock_image_xz):
        run_command('wget '+ stock_images[odroid_model]['url'] + stock_image_xz)

    try:
        os.remove(base_image_xz)
    except:
        pass

    if not os.path.isfile(base_image_xz):
        print("Copying file %s to %s ..." % (stock_image_xz, base_image_xz))
        shutil.copyfile(stock_image_xz, base_image_xz)

    if not os.path.isfile(base_image):
        print("Uncompressing file %s ..." % base_image_xz)
        run_command('unxz ' + base_image_xz)

    #
    # LOOP DEVICES HERE
    #

    start_block_boot, start_block_data = attach_loop_devices(base_image, 0, None)

    time.sleep(3)
    print("first filesystem check on /dev/loop0p2")
    check_data_partition()

    print("execute: mkdir -p "+mount_point)
    try:
        os.mkdir(mount_point)
    except:
        pass

    mount_mountpoint(0, mount_point)

    return (start_block_boot, start_block_data)

def stage_image_build_script(waggle_image_directory, mount_point):
    run_command('mkdir -p {0}/usr/lib/waggle && cd {0}/usr/lib/waggle && git clone https://github.com/waggle-sensor/waggle_image.git'.format(mount_point))

    ### Copy the image build script ###
    #shutil.copyfile('%s/scripts/configure_base.sh' % waggle_image_directory, '%s/root/configure_base.sh' % mount_point)
    #run_command('chmod +x %s/root/configure_base.sh' % mount_point)

def build_image(mount_point):
    if debug == 0:
        run_command('chroot %s/ /bin/bash /usr/lib/waggle/waggle_image/scripts/install_dependencies.sh' % (mount_point))

def generate_report(build_directory, mount_point):
    report_file = "{}/report.txt".format(build_directory)

    try:
        os.remove(base_image+'.report.txt')
    except:
        pass

    print("copy: ", mount_point+'/'+report_file, base_image+'.report.txt')

    if os.path.exists(mount_point+'/'+report_file):
        shutil.copyfile(mount_point+'/'+report_file, base_image+'.report.txt')
    else:
        print("file not found:", mount_point+'/'+report_file)

def unmount_image(mount_point):
    unmount_mountpoint(mount_point)
    time.sleep(3)
    detach_loop_devices()
    time.sleep(3)

def compress_image(base_image):
    base_image_xz = base_image + '.xz'
    try:
        os.remove(base_image_xz)
    except:
        pass

    run_command('xz -1 %s' % base_image)

def upload_image(build_directory, base_image):
    if not os.path.isfile( build_directory+ '/waggle-id_rsa'):
        return
    remote_path = '/mcs/www.mcs.anl.gov/research/projects/waggle/downloads/waggle_images/base/'
    scp_target = 'waggle@terra.mcs.anl.gov:' + remote_path
    run_command('md5sum $(basename {0}.xz) > {0}.xz.md5sum'.format(base_image) )


    cmd = 'scp -o "StrictHostKeyChecking no" -v -i {0}/waggle-id_rsa {1}.xz {1}.xz.md5sum {2}'.format(build_directory, base_image, scp_target)

    count = 0
    while 1:
        count +=1
        if (count >= 10):
            print("error: scp failed after 10 trys\n")
            sys.exit(1)

        cmd_return = 1
        print("execute: ", cmd)
        try:
            child = subprocess.Popen(['/bin/bash', '-c', cmd])
            child.wait()
            cmd_return = child.returncode

        except Exception as e:
            print("Error: %s" % (str(e)))
            cmd_return = 1

        if cmd_return == 0:
            break

        time.sleep(10)


    run_command('echo "{0}" > {1}/latest.txt'.format(base_image_base +".img.xz", build_directory))
    run_command('scp -o "StrictHostKeyChecking no" -i {0}/waggle-id_rsa {0}/latest.txt {1}/'.format(build_directory, scp_target))


    if os.path.isfile( base_image+'.report.txt'):
        run_command('scp -o "StrictHostKeyChecking no" -v -i {0}/waggle-id_rsa {1}.report.txt {2}'.format(build_directory, base_image,scp_target))


    if os.path.isfile( base_image+'.build_log.txt'):
        run_command('scp -o "StrictHostKeyChecking no" -v -i {0}/waggle-id_rsa {1}.build_log.txt {2}'.format(build_directory, base_image,scp_target))

def main():
    # To copy a new public image to the download webpage, copy the waggle-id_rsa ssh key to /root/.
    # To generate a functional AoT image with private configuration, put id_rsa_waggle_aot_config and a clone of git@gith_Aub.com:waggle-sensor/private_config.git in /root

    # One of the most significant modifications that this script does is setting static IPs. Nodecontroller and guest node have different static IPs.


    print("usage: python -u ./build_stock_image.py 2>&1 | tee build.log")


    create_b_image = 0 # will be 1 for XU3/4

    change_partition_uuid_script = waggle_image_directory + 'scripts/change-partition-uuid'   #'/usr/lib/waggle/waggle_image/change_partition_uuid.sh'

    build_directory = "/root"

    mount_point = "/mnt/newimage"

    odroid_model = detect_odroid_model()

    if not odroid_model:
        sys.exit(1)

    base_image = get_base_image_filename(build_directory, odroid_model)

    setup_mount_point(mount_point)

    os.chdir(build_directory)

    start_block_boot, start_block_data = mount_new_image(base_image, mount_point, odroid_model)

    stage_image_build_script(waggle_image_directory, mount_point)

    build_image(mount_point)

    generate_report(build_directory, mount_point)

    unmount_image(mount_point)

    attach_loop_devices(base_image, 0, start_block_boot)

    print("check boot partition")
    check_boot_partition()

    print("filesystem check on /dev/loop0p2 after chroot")
    check_data_partition()

    detach_loop_devices()

    compress_image(base_image)

    upload_image(build_directory, base_image)

if __name__ == '__main__':
    main()
