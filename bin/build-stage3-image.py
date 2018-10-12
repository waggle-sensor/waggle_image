#!/usr/bin/env python3

import getopt
import os
import os.path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import socket

waggle_image_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, '%s/lib/python/' % waggle_image_directory)
from waggle.build import *

config_db_path = os.path.realpath('{}/configure/build_config.json'.format(waggle_image_directory))
build_config = Configuration(str(config_db_path))

class BuildWaggleImageError(Exception):
  def __init__(self, message):
    super(Exception, self).__init__(message)

def print_usage():
    usage_message = "Usage: build-stage3-image [OPTIONS]\n"\
                    "OPTIONS\n"\
                    "  --help                         "\
                    "show this usage message\n"\
                    "  -b |--build-dir=<build_dir>    "\
                    "work on the disk image in the <build_dir> directory\n"\
                    "  -n |--node-controller    "\
                    "build the Node Controller Waggle Docker image\n"\
                    "  -e |--edge-processor    "\
                    "build the Edge Processor Waggle Docker image\n"\
                    "  -v |--version=<version>    "\
                    "show this usage message\n"\
                    "  -r |--revision=<revision>    "\
                    "build revision <revision> of the specified version\n"\
                    "  -d |--deployment=<deployment>    "\
                    "configure the image according to deployment <deployment>\n"\
                    "  -t |--target=<target_dev>       "\
                    "target memory device (e.g. /dev/sdb) \n"\
                    "                                  to which the image should be written\n"\
                    "  -c|--compress                   "\
                    "compress the Waggle image\n"\
                    "  -u|--upload                     "\
                    "upload the compressed image to the Waggle\n"\
                    "                                  downloads page (implies -c)\n"\
                    ""
    print(usage_message)


def get_waggle_image_filename(build, node_element):
  device = None
  base = None
  if node_element == 'Node Controller':
    node_element = 'node_controller'
    device = "odroid-c1"
    base = build_config.get_base(eid=build['nc_base'])
  elif node_element == 'Edge Processor':
    node_element = 'edge_processor'
    device = "odroid-xu3"
    base = build_config.get_base(eid=build['ep_base'])
  else:
    raise BuildWaggleImageError(
      "unknown node element '{}'".format(node_element))
  version = build['published_version']
  revision = build['revision']

  return "waggle-{}-{}-{}-{}.img".format(node_element, device, version, revision)

def setup_mount_point(mount_point):
  # clean up first
  print("Unmounting lingering images.")
  unmount_mountpoint(mount_point)
  print("Detaching loop devices.")
  time.sleep(3)
  detach_loop_devices()
  create_loop_devices()

def get_base_image_filename(base):

    if base == "nc":
       stock_image="stage3_c1+"
    elif base == "ep":
       stock_image="stage3_xu4"
    base_image=stock_image
    return "{}.img".format(base_image)


def mount_new_image(build, node_element, mount_point):
  base = None
  if node_element == 'Node Controller':
    base = 'nc'
  elif node_element == 'Edge Processor':
    base = 'ep'
  else:
    raise BuildWaggleImageError(
      "unknown node element '{}'".format(node_element))
  base_image = get_base_image_filename(base)
  base_image_xz = base_image + '.xz'

  waggle_image = get_waggle_image_filename(build, node_element)
  waggle_image_xz = waggle_image + '.xz'

  waggle_downloads_url='http://www.mcs.anl.gov/research/projects/waggle/downloads/waggle_images/base/'

  if not os.path.isfile(base_image_xz):
    run_command('wget {}{}'.format(waggle_downloads_url, base_image_xz))

  try:
      os.remove(waggle_image_xz)
  except:
      pass

  if not os.path.isfile(waggle_image_xz):
      print("Copying file %s to %s ..." % (base_image_xz, waggle_image_xz))
      shutil.copyfile(base_image_xz, waggle_image_xz)

  if not os.path.isfile(waggle_image):
      print("Uncompressing file %s ..." % waggle_image_xz)
      run_command('unxz ' + waggle_image_xz)

  attach_loop_devices(waggle_image, 0)

  time.sleep(3)
  print("first filesystem check on /dev/loop0p2")
  check_data_partition()

  print("execute: mkdir -p "+mount_point)
  try:
      os.mkdir(mount_point)
  except:
      pass

  mount_mountpoint(0, mount_point)


def mount_new_image_from_uncompressed(build, node_element, mount_point):
  base = None
  if node_element == 'Node Controller':
    base = 'nc'
  elif node_element == 'Edge Processor':
    base = 'ep'
  else:
    raise BuildWaggleImageError(
      "unknown node element '{}'".format(node_element))
  base_image = get_base_image_filename(base)
  waggle_image = base_image
  attach_loop_devices(waggle_image, 0)

  time.sleep(3)
  print("first filesystem check on /dev/loop0p2")
  check_data_partition()

  print("execute: mkdir -p "+mount_point)
  try:
      os.mkdir(mount_point)
  except:
      pass

  mount_mountpoint(0, mount_point)


def stage_image_build_script(waggle_image_directory, mount_point):
  run_command('mkdir -p {0}/usr/lib/waggle'.format(mount_point))
  shutil.copyfile(waggle_image_directory+'/scripts/install_waggle.sh',
                  '{0}/usr/lib/waggle/install_waggle.sh'.format(mount_point))


def generate_repositories_string(build, repositories):
  version = build['published_version']
  revision = build['revision']
  repository_strings = []
  for repository in repositories:
    if revision == 0:
      repository_strings.append("{}:v{}".format(repository, version))
    else:
      repository_strings.append("{}:{}".format(repository, build[repository+'_commit']))
  return ','.join(repository_strings)


def build_image(build, node_element, server_host, mount_point):
  print('Building {} Waggle image...'.format(node_element))
  repositories_string = ''
  if node_element == 'Node Controller':
    base = build_config.get_base(eid=build['nc_base'])
    if base == None:
      raise BuildWaggleImageError(
        "unable to find base with DB id '{}'".format(build['nc_base']))
    repositories = ['core', 'nodecontroller', 'plugin_manager', 'wagman', 'sensors']
    repositories_string = generate_repositories_string(build, repositories)
  elif node_element == 'Edge Processor':
    base = build_config.get_base(eid=build['nc_base'])
    if base == None:
      raise BuildWaggleImageError(
        "unable to find base with DB id '{}'".format(build['ep_base']))
    repositories = ['core', 'edge_processor', 'plugin_manager']
    repositories_string = generate_repositories_string(build, repositories)

  run_command('chroot {}/ /bin/bash /usr/lib/waggle/install_waggle.sh {} {}'.format(
    mount_point, server_host, repositories_string))

  os.remove('{0}/usr/lib/waggle/install_waggle.sh'.format(mount_point))

def generate_report(build_directory, mount_point, waggle_image):
  report_file = "report.txt"
  build_report = os.path.realpath("{}/root/{}".format(mount_point, report_file))
  image_report = "{}.{}".format(waggle_image, report_file)
  try:
    os.remove(image_report)
  except:
    pass

  print("copy: ", build_report, image_report)

  if os.path.exists(build_report):
    shutil.copyfile(build_report, image_report)
  else:
    print("file not found:", build_report)


def unmount_image(mount_point):
  unmount_mountpoint(mount_point)
  time.sleep(3)
  detach_loop_devices()
  time.sleep(3)


def compress_image(waggle_image):
  waggle_image_xz = waggle_image + '.xz'
  try:
    os.remove(waggle_image_xz)
  except:
    pass

  run_command('xz -1 %s' % waggle_image)


def upload_image(deployment, build_directory, waggle_image):
  if deployment['name'] != 'Public':
    raise BuildWaggleImageError(
      "refusing to upload a non-public Waggle image to a public web site!")

  if not os.path.isfile( build_directory+ '/waggle-id_rsa'):
      return
  remote_path = '/mcs/www.mcs.anl.gov/research/projects/waggle/downloads/waggle_images/base/'
  scp_target = 'waggle@terra.mcs.anl.gov:' + remote_path
  run_command('md5sum $(basename {0}.xz) > {0}.xz.md5sum'.format(waggle_image) )


  cmd = 'scp -o "StrictHostKeyChecking no" -v -i {0}/waggle-id_rsa {1}.xz {1}.xz.md5sum {2}'.format(build_directory, waggle_image, scp_target)

  count = 0
  while 1:
    count +=1
    if (count >= 10):
      raise BuildWaggleImageError("failed to upload the image after 10 trys")

    cmd_return = 1
    print("execute: ", cmd)
    try:
      child = subprocess.Popen(['/bin/bash', '-c', cmd])
      child.wait()
      cmd_return = child.returncode

    except Exception as e:
      print("Warning: %s" % (str(e)))
      cmd_return = 1

    if cmd_return == 0:
      break

    time.sleep(10)


  run_command('echo "{0}" > {1}/latest.txt'.format(waggle_image + ".xz", build_directory))
  run_command('scp -o "StrictHostKeyChecking no" -i {0}/waggle-id_rsa {0}/latest.txt {1}/'.format(build_directory, scp_target))


  if os.path.isfile(waggle_image +'.report.txt'):
    run_command('scp -o "StrictHostKeyChecking no" -v -i {0}/waggle-id_rsa {1}.report.txt {2}'.format(build_directory, waggle_image,scp_target))


  if os.path.isfile( waggle_image +'.build_log.txt'):
    run_command('scp -o "StrictHostKeyChecking no" -v -i {0}/waggle-id_rsa {1}.build_log.txt {2}'.format(build_directory, waggle_image,scp_target))

def burn_image(waggle_image, target_device):
  run_command('dd if={0} of={1} bs=100M status=progress'.format(waggle_image, target_device))


# TODO: use the deployment details directly instead of converting them into parameters
#       for the bless-stage3-image script
def deploy(deployment, mount_point):
  disable_wvdial = ''
  wvdial_config = build_config.get_wireless_config(eid=deployment['wireless_config'])['name']
  if wvdial_config == 'Default':
    disable_wvdial = '--disable-wvdial '

  enable_sudo = ''
  if deployment['sudo']:
    enable_sudo = '--enable-sudo '

  disable_root_password = ''
  shadow_entry = build_config.get_shadow_entry(eid=deployment['shadow_entry'])['name']
  if shadow_entry == 'Default':
    disable_root_password = '--disable-root-pass '

  rc = run_command('{0}/bless-stage3-image {1}{2}{3}{4} --clean-up'.format(
    waggle_image_directory, disable_wvdial, enable_sudo, disable_root_password, mount_point))
  if rc != 0:
    raise BuildWaggleImageError(
      "bless-stage3-image failed with return code '{}'".format(rc))


def deploy_to_disk(waggle_image, target_device, deployment):
  deploy_mount_point = tempfile.mkdtemp()
  run_command('mount {0}2 {1}'.format(target_device, deploy_mount_point))

  burn_image(waggle_image, target_device)

  deploy(deployment, deploy_mount_point)

  run_command('umount {0}'.format(deploy_mount_point))
  shutil.rmtree(deploy_mount_point)

def main(argv):
  try:
    opts, args = getopt.getopt(
      argv, "b:nev:r:d:t:cu",
      ["help", "build-dir=", "node-controller", "edge-processor", "version=", "revision=", "deployment=",
       "target=", "compress", "upload"])
  except getopt.GetoptError as ge:
    print("\nError:", str(ge))
    print_usage()
    sys.exit(1)

  build_directory = './'
  node_controller = False
  edge_processor = False
  version = None
  revision = None
  deployment_name = 'Public'
  target_device=None
  compress = False
  upload = False
  for opt, arg in opts:
    if opt == '--help':
      print_usage()
      sys.exit(0)
    elif opt in ('-b', '--build-dir'):
      build_directory = arg
    elif opt in ('-n', '--node-controller'):
      node_controller = True
    elif opt in ('-e', '--edge-processor'):
      edge_processor = True
    elif opt in ('-v', '--version'):
      version = arg
    elif opt in ('-r', '--revision'):
      revision = int(arg)
    elif opt in ('-d', '--deployment'):
      deployment_name = arg
    elif opt in ('-t', '--target'):
      target_device = arg
    elif opt in ('-c', '--compress'):
      compress = True
    elif opt in ('-u', '--upload'):
      upload = True
    else:
      print("\n" + usage_message + "\n")
      sys.exit(2)

  architecture = 'armv7l'
  architecture_id = build_config.get_cpu_architecture(architecture).eid

  if version == None:
    version, tmp_revision = build_config.get_latest_build(architecture)
    if revision == None:
      revision = tmp_revision
  else:
    if revision == None:
      revision = int(0)

  deployment = build_config.get_deployment(deployment_name)
  if deployment == None:
    raise BuildWaggleImageError(
      "unable to find deployment with name '{}'".format(deployment))

  server_host = build_config.get_beehive_host(eid=deployment['beehive_host'])['address']

  os.chdir(waggle_image_directory)
  branches = subprocess.check_output(['git', 'branch']).decode().split('\n')
  branch = [b for b in branches if '*' in b][0][2:]

  build = build_config.get_build(version, revision, architecture_id)
  if build == None:
    raise BuildWaggleImageError(
      "unable to find build with version '{}', revision '{}', "\
      "and architecture '{}'".format(version, revision, architecture))
  node_element = None
  if node_controller:
    node_element = 'Node Controller'
    base="nc"
  elif edge_processor:
    node_element = 'Edge Processor'
    base="ep"
  else:
    raise BuildWaggleImageError(
      "no node element specified (use either --node-controller or --edge-processor)")

  # convert hostname to IP
  if re.search('[a-zA-Z]', server_host):
    hostname = server_host
    server_host = socket.gethostbyname(hostname)
    print("Resolved server host '{}' to IP '{}'.".format(hostname, server_host))

  create_b_image = 0 # will be 1 for XU3/4

  change_partition_uuid_script = waggle_image_directory + 'scripts/change-partition-uuid'   #'/usr/lib/waggle/waggle_image/change_partition_uuid.sh'

  mount_point = "/mnt/newimage"

  #waggle_image = get_waggle_image_filename(build, node_element)
  waggle_image = get_base_image_filename(base)

  setup_mount_point(mount_point)

  os.chdir(build_directory)

  #mount_new_image(build, node_element, mount_point)
  mount_new_image_from_uncompressed(build, node_element, mount_point)

  stage_image_build_script(waggle_image_directory, mount_point)

  build_image(build, node_element, server_host, mount_point)

  generate_report(build_directory, mount_point, waggle_image)

  if target_device != None:
    unmount_image(mount_point)
    deploy_to_disk(waggle_image, target_device, deployment)
  else:
    deploy(deployment, mount_point)
    unmount_image(mount_point)

  attach_loop_devices(waggle_image, 0)

  print("check boot partition")
  check_boot_partition()

  print("filesystem check on /dev/loop0p2 after chroot")
  check_data_partition()

  detach_loop_devices()

  if compress:
    compress_image(waggle_image)

  if upload:
    upload_image(deployment, build_directory, waggle_image)

if __name__ == '__main__':
  main(sys.argv[1:])
