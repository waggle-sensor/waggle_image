##Set up static /dev endpoints to access Wagman and Core Sensor board##

The Wagman and Coresensor boards are built on Atmel chips and flashed with 
the Arduino boot loader. The boards are hence programmed in the Arduino software 
environment. The two boards use different Atmel chips and Arduino boot loaders, 
and are distinguished using the idVendor and idProduct fields of the USB device 
descriptor. The udev rule 75-waggle-arduino.rules creates appropriate symbolic 
links to make access to the two devices easy from the software point of view. . 

##Setup:##

**As root -**
 1. Copy 75-waggle-arduino.rules to */etc/udev/rules.d/*
 2. reload udevrules - *udevadm control --reload-rules*

After the above steps, when the Wagman and Core sense board are connected, 
they should be available for access at __/dev/waggle_wagman__ and 
__/dev/waggle_coresense__ respectively. The above two are symbolic links to 
the standard Linux ttyACMX naming scheming under /dev. For example - 

$ls -l /dev/waggle_coresense /dev/waggle_sysmon </br>
lrwxrwxrwx 1 root root 7 Feb 29 11:30 /dev/waggle_coresense -> ttyACM0 </br>
lrwxrwxrwx 1 root root 7 Feb 29 11:30 /dev/waggle_sysmon -> ttyACM1 </br>







