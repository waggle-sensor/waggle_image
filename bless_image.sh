#!/bin/bash

# By default 1) install the registration key, 2) install the wvdial.conf with the AoT APN,
# 3) disable sudo, and 4) set the AoT root password.
#
# Disable any of these options except #1 with approprite options

DISABLE_WVDIAL=0
DISABLE_APN=0
DISABLE_NO_SUDO=0
DISABLE_ROOT_PASS=0
while [[ $# -gt 0 ]]; do
  key="$1"
  echo "Key: $key"
  case $key in
    -w|--disable-wvdial)
      DISABLE_WVDIAL=1
      shift
      ;;
    -a|--disable-apn)
      DISABLE_APN=1
      shift
      ;;
    -s|--disable-no-sudo)
      DISABLE_NO_SUDO=1
      shift
      ;;
    -r|--disable-wvdial)
      DISABLE_ROOT_PASS=1
      shift
      ;;
      *)
      ;;
  esac
  shift
done


def bless_image():
  if os.path.exists('/root/id_rsa_waggle_aot_config') and run_command('ssh -T git@github.com', die=False) == 1:
    try:
      # clone the private_config repository
      run_command('git clone git@github.com:waggle-sensor/private_config.git', die=False)

      # allow the node setup script to change the root password to the AoT password
      shutil.copyfile('/root/id_rsa_waggle_aot_config', '%s/root/id_rsa_waggle_aot_config' % (mount_point_A))
      shutil.copyfile('/root/private_config/encrypted_waggle_password', '%s/root/encrypted_waggle_password' % (mount_point_A))

      if not is_extension_node:
        # allow the node to register in the field
        shutil.copyfile('/root/private_config/id_rsa_waggle_aot_registration', '%s/root/id_rsa_waggle_aot_registration' % (mount_point_A))

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
    except Exception as e:
      print("Error in private AoT configuration: %s" % str(e))
      pass
