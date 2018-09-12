# Setup

Sean: Recording what I think are the only dependencies for future reference.

Mainly uses `systemd-nspawn` to run the container and `binfmt-support` to
transparently run different architecture binaries through `qemu`.

```sh
apt-get update && apt-get install systemd-container qemu binfmt-support qemu-user-static
```
