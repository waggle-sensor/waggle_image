import bisect
import inspect
import json
import pathlib
import re
import sys
import tkinter
import tkinter.ttk as ttk
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
  def __init__(self):
    self._db = tinydb.TinyDB("./build_config.json")
    self._waggle = self._db.table('Waggle')
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
    print(uuid)
    print(self._bases.get(tinydb.Query().uuid == uuid))
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
  def add_build(self, published_version='', revision=0, deployment_id=0, cpu_architecture_id=0,
                nc_base_id=0, ep_base_id=0, waggle_image_commit_id='', core_commit_id='',
                nc_commit_id='', ep_commit_id='', pm_commit_id='', date='', build=None):
    entry = tinydb.Query()
    if build != None:
      _build = self._builds.get((entry.published_version == build['published_version'])\
                                & (entry.revision == build['revision'])
                                & (entry.deployment == build['deployment'])
                                & (entry.cpu_architecture == build['cpu_architecture']))

      if _build == None:
        # verify that the build and base architectures match
        for base_id in [build['nc_base'], build['ep_base']]:
          base = self.get_base(eid=base_id)
          print(base)
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
                                & (entry.deployment == deployment_id)
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
           'cpu_architecture': cpu_architecture_id, 'deployment': deployment_id,
           'nc_base': nc_base_id, 'ep_base': ep_base_id,
           'waggle_image_commit': waggle_image_commit_id, 'core_commit': core_commit_id,
           'nc_commit': nc_commit_id, 'ep_commit': ep_commit_id, 'pm_commit': pm_commit_id,
           'date': date})

  def get_build(self, published_version='', revision=0, deployment=1, architecture=1, eid=0):
    if eid == None:
      return None
    if eid > 0:
      return self._builds.get(eid=eid)
    entry = tinydb.Query()
    build = self._builds.get((entry.published_version == published_version)\
                              & (entry.revision == revision)
                              & (entry.deployment == deployment)
                              & (entry.cpu_architecture == architecture))
    if build == None:
      return None
    return build

  def get_latest_build_version(self):
    sorted_builds = sorted(self._builds.all(), key=lambda bld: bld['published_version'])
    return sorted_builds['published_version']

  def get_builds(self):
    return self._builds.all()

  def remove_build(self, eid):
    return self._builds.remove(eids=[eid,])

  def get_build_dependencies(
      self, version='', revision=0, deployment_name='Public', architecture_name='armv7l'):
    if version == None:
      sorted_builds = sorted(self.get_builds(), key=lambda bld: bld['published_version'])
      version = sorted_builds[-1]['published_version']

    if revision == None:
      revisions = [bld for bld in self.get_builds() if bld['published_version'] == version]
      sorted_revisions = sorted(revisions, key=lambda bld: bld['revision'])
      revision = sorted_revisions[-1]['revision']

    if deployment_name == None:
      deployment_name = 'Public'
    deployment = self.get_deployment(deployment_name)
    if deployment == None:
      print("Error: deployment '{}' does not exist".format(deployment_name))
      sys.exit(6)

    if architecture_name == None:
      architecture_name = 'armv7l'
    architecture = self.get_cpu_architecture(architecture_name)
    if architecture == None:
      print("Error: CPU architecture '{}' does not exist".format(architecture_name))
      sys.exit(6)

    target_build = self.get_build(version, revision, deployment.eid, architecture.eid)
    nc_base = self.get_base(eid=target_build['nc_base'])
    ep_base = self.get_base(eid=target_build['ep_base'])

    string_buffer = []
    dependencies = []
    for base in (nc_base,ep_base):
      first_dep = True
      for dependency_id in base['dependencies']:
        dependency = self.get_dependency(eid=dependency_id)
        dependency_type = self.get_dependency_type(eid=dependency['type'])
        if first_dep:
          first_dep = False
        else:
          string_buffer.append(',')
        string_buffer.append('{}:{}'.format(dependency['name'], dependency_type['name']))
      dependencies.append(''.join(string_buffer))
    return dependencies
