GPT fdisk (gdisk) version 1.0.3
Caution: invalid main GPT header, but valid backup; regenerating main header
from backup!

Caution! After loading partitions, the CRC doesn't check out!
Warning! Main partition table CRC mismatch! Loaded backup partition table
instead of main partition table!

Warning! One or more CRCs don't match. You should repair the disk!

Partition table scan:
  MBR: hybrid
  BSD: not present
  APM: not present
  GPT: damaged

Found valid MBR and corrupt GPT. Which do you want to use? (Using the
GPT MAY permit recovery of GPT data.)
 1 - MBR
 2 - GPT
 3 - Create blank GPT

Your answer: 3
************************************************************************
Most versions of Windows cannot boot from a GPT disk except on a UEFI-based
computer, and most varieties prior to Vista cannot read GPT disks. Therefore,
you should exit now unless you understand the implications of converting MBR
to GPT or creating a new GPT disk layout!
************************************************************************

Are you SURE you want to continue? (Y/N): y

Command (? for help): n
Partition number (1-128, default 1): 
First sector (34-30433246, default = 2048) or {+-}size{KMGTP}: 
Last sector (2048-30433246, default = 30433246) or {+-}size{KMGTP}: 
Current type is 'Microsoft basic data'
Hex code or GUID (L to show codes, Enter = 700):
Changed type of partition to 'Microsoft basic data'

Command (? for help): w

Final checks complete. About to write GPT data. THIS WILL OVERWRITE EXISTING
PARTITIONS!!

Do you want to proceed? (Y/N): y
OK; writing new GUID partition table (GPT) to \\.\physicaldrive3.
Disk synchronization succeeded! The computer should now use the new
partition table.
The operation has completed successfully.