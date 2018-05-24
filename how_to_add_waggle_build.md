<!--
waggle_topic=IGNORE
-->

# How to Add a Waggle Build
To build Waggle for Nodecontroller and Edge Processor, two build configurations need to be set. To see previous Waggle builds,
```
$ cd config
$ ./get-builds
...
14 2.9.0 (1) armv7l 2018-05-21:
  Bases:
    5 Node Controller (armv7l) 2017-10-13 - A9024069-8E15-4946-A8DA-2BC9DAD8CCB0:
    7 Edge Processor (armv7l) 2018-03-30 - 77c1857d-4ce5-4b24-b15c-4925baca7059:
  Commit IDs:
    waggle_image   abe2fd8
    core           221267d
    nodecontroller 32d209d
    edge_processor 5c369bc
    plugin_manager 8f2ea77
```
The output specifies Waggle version / revision / architecture / base image / commit IDs of each repository.

To add a new Waggle build,
```
# Example: build 2.9.1 Waggle using the base image #5 for Nodecontroller and #7 for Edge Processor
$ VERSION=2.9.1
$ NC_BASE=5
$ EP_BASE=7
$ ./add-build --version=$VERSION --architecture=armv7l --nc-base=$NC_BASE --ep-base=$EP_BASE --date=2018-05-22
15 2.9.1 (0) armv7l 2018-05-22:
  Bases:
    5 Node Controller (armv7l) 2017-10-13 - A9024069-8E15-4946-A8DA-2BC9DAD8CCB0:
    7 Edge Processor (armv7l) 2018-03-30 - 77c1857d-4ce5-4b24-b15c-4925baca7059:
  Commit IDs:
    waggle_image   abe2fd8
    core           221267d
    nodecontroller 32d209d
    edge_processor 5c369bc
    plugin_manager 8f2ea77
$ ./add-build --version=$VERSION --architecture=armv7l --nc-base=$NC_BASE --ep-base=$EP_BASE --date=2018-05-22
16 2.9.1 (1) armv7l 2018-05-22:
  Bases:
    5 Node Controller (armv7l) 2017-10-13 - A9024069-8E15-4946-A8DA-2BC9DAD8CCB0:
    7 Edge Processor (armv7l) 2018-03-30 - 77c1857d-4ce5-4b24-b15c-4925baca7059:
  Commit IDs:
    waggle_image   abe2fd8
    core           221267d
    nodecontroller 32d209d
    edge_processor 5c369bc
    plugin_manager 2cf7d81
```
__IMPORTANT__: `add-build` script must run twice in order to set the right commit IDs for the repositories (See the revision change from above example). Thus, revision 1 will be used to build Waggle image.

It is a good habit that you check commit IDs whether the IDs reflect the right version in the git repository. Also check the base image.

To remove existing build,
```
# Example: remove Waggle build 2.9.1 revision 1
$ ./remove-build --version=2.9.1
16 2.9.1 (1) armv7l 2018-05-22:
  Bases:
    5 Node Controller (armv7l) 2017-10-13 - A9024069-8E15-4946-A8DA-2BC9DAD8CCB0:
    7 Edge Processor (armv7l) 2018-03-30 - 77c1857d-4ce5-4b24-b15c-4925baca7059:
  Commit IDs:
    waggle_image   abe2fd8
    core           221267d
    nodecontroller 32d209d
    edge_processor 5c369bc
    plugin_manager 2cf7d81
```
