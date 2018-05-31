import bisect
import glob
import inspect
import json
import os
import pathlib
import re
import subprocess
import sys
import time
import tinydb

class Error(Exception):
  pass

class ConfigurationError(Error):
  def __init__(self, message=''):
    self.message = message

class ArchitectureMismatchError(ConfigurationError):
  def __init__(self, element, expected, actual):
    super(ConfigurationError, self).__init__(
      "expected '{}' base with CPU architecture '{}', but got '{}'".format(
        element, expected, actual))

class NodeElementMismatchError(ConfigurationError):
  def __init__(self, expected, actual):
    super(ConfigurationError, self).__init__(
      "expected node element '{}', but got '{}'".format(expected, actual))

class Configuration:
  def __init__(self, db_path):
    self._db = tinydb.TinyDB(db_path)
    self._bases = self._db.table('Base')
    self._node_elements = self._db.table('Node Element')
    self._cpu_architectures = self._db.table('CPU Architecture')
    self._dependencies = self._db.table('Dependency')
    self._dependency_types = self._db.table('Dependency Type')
    self._registration_keys = self._db.table('Registration Key')
    self._wireless_configs = self._db.table('Wireless Config')
    self._shadow_entries = self._db.table('Shadow Entry')
    self._beehive_hosts = self._db.table('Beehive Host')
    self._build_hosts = self._db.table('Build Host')
    self._deployments = self._db.table('Deployment')
    self._builds = self._db.table('Build')

  def get_db(self):
    return self._db

  def get_by_name_or_id(self, table, name, eid):
    if eid > 0:
      return table.get(eid=eid)
    entry = tinydb.Query()
    result = table.get(entry.name == name)
    if result == None:
      return None
    return result

  # Dependency Type functions
  def add_dependency_type(self, name):
    return self._dependency_types.insert({'name': name})

  def get_dependency_type(self, name='', eid=0):
    return self.get_by_name_or_id(self._dependency_types, name, eid)

  def get_dependency_types(self):
    return self._dependency_types.all()


  # Dependency functions
  def add_dependency(self, name, type_id):
    dep_entry = tinydb.Query()
    dep = self._dependencies.get((dep_entry.name == name) & (dep_entry.type == type_id))
    if dep == None:
      return self._dependencies.insert({'name': name, 'type': type_id})
    return None

  def get_dependency(self, name='', type_id='', eid=0):
    if eid > 0:
      return self._dependencies.get(eid=eid)
    dep_entry = tinydb.Query()
    dep = self._dependencies.get((dep_entry.name == name) & (dep_entry.type == type_id))
    if dep == None:
      return None
    return dep

  def get_dependencies(self):
    return self._dependencies.all()


  # Node Element functions
  def add_node_element(self, name):
    if self._node_elements.get(tinydb.Query().name == name) == None:
      return self._node_elements.insert({'name': name})
    return None

  def get_node_element(self, name='', eid=0):
    return self.get_by_name_or_id(self._node_elements, name, eid)

  def get_node_elements(self):
    return self._node_elements.all()


  # CPU Architecture functions
  def add_cpu_architecture(self, name):
    if self._cpu_architectures.get(tinydb.Query().name == name) == None:
      return self._cpu_architectures.insert({'name': name})
    return None

  def get_cpu_architecture(self, name='', eid=0):
    return self.get_by_name_or_id(self._cpu_architectures, name, eid)

  def get_cpu_architectures(self):
    return self._cpu_architectures.all()


  # base version functions
  def add_base(self, uuid, date, dependency_ids, node_element_id, cpu_architecture_id):
    # print(uuid)
    # print(self._bases.get(tinydb.Query().uuid == uuid))
    if self._bases.get(tinydb.Query().uuid == uuid) == None:
      return self._bases.insert(
        {'uuid': uuid, 'date': date, 'dependencies': dependency_ids,
         'node_element': node_element_id, 'cpu_architecture': cpu_architecture_id})

  def get_base(self, uuid='', eid=0):
    if eid > 0:
      return self._bases.get(eid=eid)
    entry = tinydb.Query()
    result = self._bases.get(entry.uuid == uuid)
    if result == None:
      return None
    return result

  def get_bases(self):
    return self._bases.all()


  # shadow entry functions
  def add_shadow_entry(self, name, file):
    if self._shadow_entries.get(tinydb.Query().name == name) == None:
      return self._shadow_entries.insert({'name': name, 'file': file})
    return None

  def get_shadow_entry(self, name='', eid=0):
    return self.get_by_name_or_id(self._shadow_entries, name, eid)

  def get_shadow_entries(self):
    return self._shadow_entries.all()


  # wireless config functions
  def add_wireless_config(self, name, repo):
    if self._wireless_configs.get(tinydb.Query().name == name) == None:
      return self._wireless_configs.insert({'name': name, 'repo': repo})
    return None

  def get_wireless_config(self, name='', eid=0):
    return self.get_by_name_or_id(self._wireless_configs, name, eid)

  def get_wireless_configs(self):
    return self._wireless_configs.all()


  # registration key functions
  def add_registration_key(self, name, file):
    if self._registration_keys.get(tinydb.Query().name == name) == None:
      return self._registration_keys.insert({'name': name, 'file': file})
    return None

  def get_registration_key(self, name='', eid=0):
    return self.get_by_name_or_id(self._registration_keys, name, eid)

  def get_registration_keys(self):
    return self._registration_keys.all()


  # beehive hosts functions
  def add_beehive_host(self, name, fqdn, address):
    if self._beehive_hosts.get(tinydb.Query().name == name) == None:
      return self._beehive_hosts.insert({'name': name, 'fqdn': fqdn, 'address': address})
    return None

  def get_beehive_host(self, name='', eid=0):
    return self.get_by_name_or_id(self._beehive_hosts, name, eid)

  def get_beehive_hosts(self):
    return self._beehive_hosts.all()


  # build hosts functions
  def add_build_host(self, name, fqdn='', address=''):
    if self._build_hosts.get(tinydb.Query().name == name) == None:
      return self._build_hosts.insert({'name': name, 'fqdn': fqdn, 'address': address})
    return None

  def get_build_host(self, name='', eid=0):
    return self.get_by_name_or_id(self._build_hosts, name, eid)

  def get_build_hosts(self):
    return self._build_hosts.all()


  # deployment functions
  def add_deployment(self, name, shadow_entry, sudo, wireless_config, reg_key, beehive_host, build_host):
    if self._deployments.get(tinydb.Query().name == name) == None:
      return self._deployments.insert(
        {'name': name, 'shadow_entry': shadow_entry, 'sudo': sudo, 'wireless_config': wireless_config,
        'reg_key': reg_key, 'beehive_host': beehive_host, 'build_host': build_host})
    return None

  def get_deployment(self, name='', eid=0):
    return self.get_by_name_or_id(self._deployments, name, eid)

  def get_deployments(self):
    return self._deployments.all()


  # build functions
  def add_build(self, published_version='', revision=0, cpu_architecture_id=0,
                nc_base_id=0, ep_base_id=0, waggle_image_commit_id='', core_commit_id='',
                nodecontroller_commit_id='', edge_processor_commit_id='', plugin_manager_commit_id='', date='', build=None):
    entry = tinydb.Query()
    if build != None:
      _build = self._builds.get((entry.published_version == build['published_version'])\
                                & (entry.revision == build['revision'])
                                & (entry.cpu_architecture == build['cpu_architecture']))

      if _build == None:
        # verify that the build and base architectures match
        for base_id in [build['nc_base'], build['ep_base']]:
          base = self.get_base(eid=base_id)
          # print(base)
          if base == None:
            raise ConfigurationError("base with UUID '{}' was not found".format(base_id))
          if build['cpu_architecture'] != base['cpu_architecture']:
            raise ArchitectureMismatchError(
              self.get_node_element(eid=base['node_element'])['name'],
              self.get_cpu_architecture(eid=build['cpu_architecture'])['name'],
              self.get_cpu_architecture(eid=base['cpu_architecture'])['name'])
        return self._builds.insert(build)
    else:
      build = self._builds.get((entry.published_version == published_version)\
                                & (entry.revision == revision)
                                & (entry.cpu_architecture == cpu_architecture_id))
      if build == None:
        # verify that the build and base architectures match and that the base node elements are sane
        node_element_ids = [1, 2]
        base_ids = [nc_base_id, ep_base_id]
        for base_id,node_element_id in zip(base_ids, node_element_ids):
          base = self.get_base(eid=base_id)
          if base == None:
            raise ConfigurationError("base with UUID '{}' was not found".format(base_id))
          if cpu_architecture_id != base['cpu_architecture']:
            raise ArchitectureMismatchError(
              self.get_node_element(eid=base['node_element'])['name'],
              self.get_cpu_architecture(eid=cpu_architecture_id)['name'],
              self.get_cpu_architecture(eid=base['cpu_architecture'])['name'])
          if node_element_id != base['node_element']:
            raise NodeElementMismatchError(
              self.get_node_element(eid=node_element_id)['name'],
              self.get_node_element(eid=base['node_element']))
        return self._builds.insert(
          {'published_version': published_version, 'revision': revision,
           'cpu_architecture': cpu_architecture_id,
           'nc_base': nc_base_id, 'ep_base': ep_base_id,
           'waggle_image_commit': waggle_image_commit_id,
           'core_commit': core_commit_id,
           'nodecontroller_commit': nodecontroller_commit_id,
           'edge_processor_commit': edge_processor_commit_id,
           'plugin_manager_commit': plugin_manager_commit_id,
           'date': date})

  def get_build(self, published_version='', revision=0, architecture=1, eid=0):
    if eid == None:
      return None
    if eid > 0:
      return self._builds.get(eid=eid)
    entry = tinydb.Query()
    build = self._builds.get((entry.published_version == published_version)\
                              & (entry.revision == revision)
                              & (entry.cpu_architecture == architecture))
    if build == None:
      return None
    return build

  def get_latest_build(self, architecture_name='armv7l'):
    architecture_id = self.get_cpu_architecture(architecture_name).eid
    filtered_builds = [bld for bld in self._builds.all() if bld['cpu_architecture'] == architecture_id]
    if len(filtered_builds) > 0:
      sorted_builds = sorted(filtered_builds,
          key=lambda bld: ''.join((bld['published_version'], '-', str(bld['revision']))))
      return (sorted_builds[-1]['published_version'], sorted_builds[-1]['revision'])
    return None

  def get_builds(self):
    return self._builds.all()

  def remove_build(self, eid):
    return self._builds.remove(eids=[eid,])

  def get_base_dependencies(self, uuid='', base=None):
    if base == None:
      base = self.get_base(uuid)
    if base == None:
      raise ConfigurationError("unable to find base with uuid '{}'".format(uuid))
    string_buffer = []
    dependencies = ''
    first_dep = True
    for dependency_id in base['dependencies']:
      dependency = self.get_dependency(eid=dependency_id)
      dependency_type = self.get_dependency_type(eid=dependency['type'])
      if first_dep:
        first_dep = False
      else:
        string_buffer.append(',')
      string_buffer.append('{}:{}'.format(dependency['name'], dependency_type['name']))
    return ''.join(string_buffer)

  def get_build_dependencies(self, version='', revision=0, architecture_name='armv7l'):
    if version == None:
      sorted_builds = sorted(self.get_builds(), key=lambda bld: bld['published_version'])
      version = sorted_builds[-1]['published_version']

    if revision == None:
      revisions = [bld for bld in self.get_builds() if bld['published_version'] == version]
      sorted_revisions = sorted(revisions, key=lambda bld: bld['revision'])
      revision = sorted_revisions[-1]['revision']

    if architecture_name == None:
      architecture_name = 'armv7l'
    architecture = self.get_cpu_architecture(architecture_name)
    if architecture == None:
      raise ConfigurationError("CPU architecture '{}' does not exist".format(architecture_name))

    target_build = self.get_build(version, revision, architecture.eid)
    if target_build == None:
      raise ConfigurationError(
        "build not found with version '{}', revision '{}', and architecture '{}'".format(
        version, revision, architecture_name))
    nc_base = self.get_base(eid=target_build['nc_base'])
    ep_base = self.get_base(eid=target_build['ep_base'])

    dependencies = []
    for base in (nc_base, ep_base):
      dependencies.append(self.get_base_dependencies(base=base))
    return dependencies


### Disk Image Helper Functions ###

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
    for i in ['/dev', '/proc', '/run', '/sys']:
        while int(get_output('mount | grep '+mp+i+' | wc -l')) != 0:
            run_command_f('umount -d '+mp+i)
            time.sleep(3)
    run_command_f('umount '+mp)
    time.sleep(3)



def mount_mountpoint(device, mp):
    run_command('mount /dev/loop%dp2 %s' % (device, mp))
    run_command('mount -o bind /dev  %s/dev' % (mp))
    run_command('mount -o bind /proc %s/proc' % (mp))
    run_command('mount -o bind /run %s/run' % (mp))
    run_command('mount -o bind /sys  %s/sys' % (mp))
    time.sleep(3)


def check_data_partition(device_index=0):
    run_command('e2fsck -f -y /dev/loop{}p2'.format(device_index))

def check_boot_partition(device_index=0):
  run_command_f('fsck.vfat -py /dev/loop{}p1'.format(device_index))

def used_device_minors():
  device_minor_used={}

  # list devices: ls -latr /dev/loop[0-9]*
  # find minor number: stat -c %T /dev/loop2
  for device in glob.glob('/dev/loop[0-9]*'):
      print("device: ", device)
      minor=os.minor(os.stat(device).st_rdev)
      print("device minor: ", minor)
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
  print(device_minor_used)

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




def attach_loop_devices(filename, device_number):
    """
    Create loop devices for complete image and for the root partition
    startblock (optional) is the start of the second partition
    """
    # get partition start position
    #fdisk -lu ${base_image}

    loop_device = '/dev/loop'+str(device_number)
    loop_partition_1 = loop_device+'p1' # boot partition
    loop_partition_2 = loop_device+'p2' # data/root partition

    start_block_boot_str = get_output("fdisk -lu {0} | grep '{0}1' | awk '{{print $2}}'".format(filename))
    start_block_boot=int(start_block_boot_str)
    print("start_block_boot: ", start_block_boot)

    start_block_data_str = get_output("fdisk -lu {0} | grep '{0}2' | awk '{{print $2}}'".format(filename))
    start_block_data=int(start_block_data_str)
    print("start_block_data: ", start_block_data)

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

    time.sleep(3)

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
    odroid_model_raw = get_output('cat /proc/cpuinfo | grep Hardware | grep -o "[^ ]*$"').rstrip().decode()
    print("Detected device: %s" % odroid_model_raw)

    odroid_model = ''
    if odroid_model_raw == "ODROID-XU3" or odroid_model_raw == "ODROID-XU4":
      # The XU4 is actually a XU3.
      odroid_model = 'odroid-xu3'
    elif odroid_model_raw == "ODROIDC":
      odroid_model = 'odroid-c1'
    else:
      print("Could not detect ODROID model. (%s)" % odroid_model)
      return None

    return odroid_model

