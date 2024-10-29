# using DISKPART to clean disk
# the first partition (MSR) will be created
# If plan to create win 10 and win 11 together and can boot both on bios legacy and uefi, need to create 2 partition at next
# create hybrid for 2 partition (ussually 2 3) at once
# the MBR parts will be the first 3 partition:
DISKPART> list partition

  Partition ###  Type              Size     Offset
  -------------  ----------------  -------  -------
  Partition 1    Reserved            15 MB    17 KB
  Partition 2    Primary              9 GB    16 MB -> for win 10
  Partition 3    Primary              9 GB     9 GB -> for win 11
    <unused space>
# If just need 1 installer, then choose only 1 partition, but after that, there are no solution to add more partition to MBR part yet.
# remaining space of disk (the right side) will be normal GPT and can create macos installer