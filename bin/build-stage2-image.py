#!/usr/bin/env python3

import getopt
import os
import os.path
import shutil
import subprocess
import sys
import time

waggle_image_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.realpath('{}/lib/python/'.format(waggle_image_directory)))
from waggle.build import *

config_db_path = os.path.realpath('{}/configure/build_config.json'.format(waggle_image_directory))
build_config = Configuration(str(config_db_path))

debug=0 # skip chroot environment if 1

def get_base_image_filename(base):
    architecture = build_config.get_cpu_architecture(eid=base['cpu_architecture'])['name']
    if architecture != 'armv7l':
        print("Error: expected CPU architecture 'armv7l', but got '{}'".format(architecture))
        sys.exit(6)
    node_element = build_config.get_node_element(eid=base['node_element'])['name']
    waggle_stock_url=''
    stock_images=   {
                    'Edge Processor' : {
                            'filename': "stage2_xu4",
                             'url': waggle_stock_url
                            },
                    'Node Controller' : {
                            'filename':"stage2_c1+",
                            'url': waggle_stock_url
                        }
                    }

    try:
        stock_image = stock_images[node_element]['filename']
    except:
        print("{} image not found".format(node_element))
        sys.exit(1)

    base_image=stock_image

    return "{}.img".format(base_image)


#def get_base_image_filename(base):
    #node_element = build_config.get_node_element(eid=base['node_element'])['name'].replace(
        #' ', '_').lower()
    #if node_element == 'node_controller':
        #device = "c1+"
    #else:
        #device = "xu4"

    #date = base['date'].replace('-', '')

    #base_image_base="stage2_%s_%s" % (device, date)
    #return "{}.img".format(base_image_base)


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


def mount_new_image_local_uncompressed(base_image, mount_point, base):
    architecture = build_config.get_cpu_architecture(eid=base['cpu_architecture'])['name']
    if architecture != 'armv7l':
        print("Error: expected CPU architecture 'armv7l', but got '{}'".format(architecture))
        sys.exit(6)
    node_element = build_config.get_node_element(eid=base['node_element'])['name']
    waggle_stock_url=''
    stock_images=   {
                    'Edge Processor' : {
                            'filename': "stage2_xu4.img",
                             'url': waggle_stock_url
                            },
                    'Node Controller' : {
                            'filename':"stage2_c1+.img",
                            'url': waggle_stock_url
                        }
                    }

    try:
        stock_image = stock_images[node_element]['filename']
    except:
        print("{} image not found".format(node_element))
        sys.exit(1)

    base_image=stock_image
    #
    # LOOP DEVICES HERE
    #
    attach_loop_devices(base_image, 0)

    time.sleep(3)
    print("first filesystem check on /dev/loop0p2")
    check_data_partition()

    print("execute: mkdir -p "+mount_point)
    try:
        os.mkdir(mount_point)
    except:
        pass

    mount_mountpoint(0, mount_point)

def mount_new_image_local_compressed(base_image, mount_point, base):
    architecture = build_config.get_cpu_architecture(eid=base['cpu_architecture'])['name']
    if architecture != 'armv7l':
        print("Error: expected CPU architecture 'armv7l', but got '{}'".format(architecture))
        sys.exit(6)
    node_element = build_config.get_node_element(eid=base['node_element'])['name']
    waggle_stock_url='http://www.mcs.anl.gov/research/projects/waggle/downloads/waggle_images/base/'
    stock_images=   {
                    'Edge Processor' : {
                            'filename': "stage1_xu4.img",
                             'url': waggle_stock_url
                            },
                    'Node Controller' : {
                            'filename':"stage1_c1+.img",
                            'url': waggle_stock_url
                        }
                    }

    base_image_xz = base_image + '.xz'

    try:
        stock_image = stock_images[node_element]['filename']
    except:
        print("{} image not found".format(node_element))
        sys.exit(1)

    stock_image_xz = stock_image + '.xz'

    if not os.path.isfile(stock_image_xz):
        run_command('wget '+ stock_images[node_element]['url'] + stock_image_xz)

    try:
        os.remove(base_image_xz)
    except:
        pass


    if not os.path.isfile(stock_image):
        print("Uncompressing file %s ..." % stock_image_xz)
        run_command('unxz -f -k ' + stock_image_xz)
        run_command('mv %s %s'%(stock_image,base_image))

    #
    # LOOP DEVICES HERE
    #

    attach_loop_devices(base_image, 0)

    time.sleep(3)
    print("first filesystem check on /dev/loop0p2")
    check_data_partition()

    print("execute: mkdir -p "+mount_point)
    try:
        os.mkdir(mount_point)
    except:
        pass

    mount_mountpoint(0, mount_point)


def stage_image_build_script(waggle_image_directory, mount_point, branch):
    if len(branch) > 0:
        run_command('mkdir -p {0}/usr/lib/waggle && cd {0}/usr/lib/waggle && git clone -b {1} https://github.com/waggle-sensor/waggle_image.git'.format(mount_point, branch))
    else:
        run_command('mkdir -p {0}/usr/lib/waggle && cd {0}/usr/lib/waggle && git clone https://github.com/waggle-sensor/waggle_image.git'.format(mount_point))

    run_command('cd {0}/root && wget https://www.rabbitmq.com/rabbitmq-release-signing-key.asc'.format(mount_point))

    ### Copy the image build script ###
    #shutil.copyfile('%s/scripts/configure_base.sh' % waggle_image_directory, '%s/root/configure_base.sh' % mount_point)
    #run_command('chmod +x %s/root/configure_base.sh' % mount_point)


def build_image(mount_point, dependencies):
    if debug == 0:
        script_path = '/usr/lib/waggle/waggle_image/scripts/install_dependencies.sh'
        run_command('chroot {0}/ /bin/bash {1} {2}'.format(mount_point, script_path, dependencies))

    shutil.rmtree('{0}/usr/lib/waggle/waggle_image'.format(mount_point))


def generate_report(build_directory, mount_point, base_image):
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
            print("error: scp failed after 10 tries\n")
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


    if os.path.isfile( base_image +'.report.txt'):
        run_command('scp -o "StrictHostKeyChecking no" -v -i {0}/waggle-id_rsa {1}.report.txt {2}'.format(build_directory, base_image,scp_target))


    if os.path.isfile( base_image +'.build_log.txt'):
        run_command('scp -o "StrictHostKeyChecking no" -v -i {0}/waggle-id_rsa {1}.build_log.txt {2}'.format(build_directory, base_image,scp_target))


def main(argv):
    usage_message = "Usage: build-stage2-image [OPTIONS] <uuid>\n"\
                    "  build the image with UUID <uuid>\n"\
                    "OPTIONS\n"\
                    "  --help                         "\
                    "show this usage message\n"\
                    "  -b |--build-dir=<build_dir>    "\
                    "work on the disk image in the <build_dir> directory\n"\
                    ""
    try:
        opts, args = getopt.getopt(
            argv,
            "b:",
            ["help", "build-dir="])
    except getopt.GetoptError as ge:
        print("\nError:", str(ge))
        print(usage_message)
        sys.exit(1)

    compress = False
    build_directory = '/root'
    for opt, arg in opts:
        if opt == '--help':
            print("\n" + usage_message + "\n")
            sys.exit(0)
        elif opt in ('-b', '--build-dir'):
            build_directory = arg
        else:
            print("\n" + usage_message + "\n")
            sys.exit(2)

    uuid = None
    if len(args) > 0:
        uuid = args[0]
    else:
        print("Error: the UUID of the base image to build is required (see usage with --help)")
        sys.exit(3)

    base = build_config.get_base(uuid)
    if base == None:
        print("Error: unable to find a base image with UUID {}".format(uuid))
        sys.exit(4)

    os.chdir(waggle_image_directory)
    branches = subprocess.check_output(['git', 'branch']).decode().split('\n')
    branch = [b for b in branches if '*' in b][0][2:]
    print("Building branch '{}'...".format(branch))

    create_b_image = 0 # will be 1 for XU3/4

    change_partition_uuid_script = waggle_image_directory + 'scripts/change-partition-uuid'   #'/usr/lib/waggle/waggle_image/change_partition_uuid.sh'

    mount_point = "/mnt/newimage"

    base_image = get_base_image_filename(base)

    setup_mount_point(mount_point)

    os.chdir(build_directory)

    mount_new_image_local_uncompressed(base_image, mount_point, base)

    stage_image_build_script(waggle_image_directory, mount_point, branch)


    build_image(mount_point, build_config.get_base_dependencies(base=base))

    generate_report(build_directory, mount_point, base_image)

    unmount_image(mount_point)

    attach_loop_devices(base_image, 0)

    print("check boot partition")
    check_boot_partition()

    print("filesystem check on /dev/loop0p2 after chroot")
    check_data_partition()

    detach_loop_devices()

    #compress_image(base_image)

    #upload_image(build_directory, base_image)

if __name__ == '__main__':
    main(sys.argv[1:])
