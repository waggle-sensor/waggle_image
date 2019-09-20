# Waggle ODROID C1+ Arch Linux Image

These tools build a Waggle image for the ODROID C1+ based on Arch Linux.

## Requirements

The main requirements are

* [systemd-nspawn](https://www.freedesktop.org/software/systemd/man/systemd-nspawn.html)
* bsdtar

## Usage

```sh
./setup-disk.sh /dev/sdX
```

## Notes

Here are some notes recording why we've included less than obvious configurations.

### extra/etc/systemd/resolved.conf.d/dnssec.conf

This conf is added to address systemd-resolved's complaints

```txt
DNSSEC validation failed for...
```

This seems to have been leading to us not being able to resolve hostnames.
