## File system structure on Waggle

Waggle is a remote embedded platform that provides data and user services from multiple of Waggle nodes. When Waggle nodes are deployed, it is challenging to manage the nodes operational and make them recoverable. Errors in file system such as file corruptions and damaged or deleted system files cause serious impact to Waggle nodes as they are not able to boot up normally. This even possibly leads to decommission of nodes. To prevent this, Waggle actively utilizes read-only feature on its file system.

Waggle file system consists of three parts: boot file system, root file system, and user space file system. The detail of each file system is depicted below.

```
                   NAME        Properties    Approx. size
Partition1: Boot file system   (FAT16   )       ~  130 MB
Partition2: Root file system   (Ext4, RO)       ~ 7000 MB
Partition3: User file system   (Ext4    )       ~ 7000 MB
```

Boot configurations are stored in the partition 1 whereas system files including user data and Waggle-specific configurations are stored in partition2 and 3. The root `/` is mounted on the partition 2. Because the partition 2 is read only file system, some system or user-related files that dynamically change (i.e., `/var` and `/srv`) cannot be in that file system. The directories containing such files are stored in the partition 3, writable, and properly linked to the system file system such that the OS can notify their location. The partition 3 stores all volatile contents as well as non-system-critical files. All user applications are running on the partition 3.

Some of the Waggle configurations that do not need to change during normal operation are stored in the system file system. Changing them requires the system into a safe mode. `waggle-set-mode` is root-previliaged script that allows to switch between the modes. After a change happens the root file system has to be file-system locked in order to operate the Waggle system normally. Some other Waggle or user configurations are stored in the user file system and can be changed during normal operation. User files are separatedly stored in a specific directory as multiple users can use the system.

### Frequent questions

Q1) Does the root partition mount RW briefly and then switch to RO, in normal mode, or does it boot RO with only /var and /tmp RW?

A1) The mounting is done through `fstab` entries. So in steady state, the `/` partition is mounted ro by fstab from boot

Q2) When the root file system is writable can user applications write something on `/`?

A2) No, when the system is in safe mode, making the system writable, Waggle purposely terminate all user applications. In order to run uer applications again, the system needs to lock the root file system.

Q3) How to update and install user applications with and without bringing a new library?

A3) Users are responsible for installing/updating/managing their application. Their applications are stored in the user file system. The libraries that their application uses are configured only for them. If libraries need to be installed system-wide or it is worth doing that, contact Waggle team as users do not have the ability to switch Waggle system modes.
