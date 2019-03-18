## File system structure on Waggle

Waggle is a remote embedded platform that provides data and user services from multiple of Waggle nodes. When Waggle nodes are deployed, it is challenging to manage the nodes operational and make them recoverable. Errors in file system such as file corruptions and damaged or deleted system files cause serious impact to Waggle nodes as they are not able to boot up normally. This even possibly leads to decommission of nodes. To prevent this, Waggle actively utilizes read-only feature on its file system.

Waggle file system consists of three parts: boot file system, system file system, and user space file system. The detail of each file system is depicted below.

```
                   NAME        Properties    Approx. size
Partition1: Boot file system   (FAT16   )       ~ 130  MB
Partition2: System file system (Ext4, RO) .     ~ 7000 MB
Partition3: User file system   (Ext4    )       ~ 7000 MB
```
