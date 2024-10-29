import os
import subprocess
import re
import time


def find_drive(drive_letter):
    """
    This function maps a drive letter (like 'D') to the corresponding physical drive (like '\\.\\PhysicalDrive1').
    """
    drive_letter = drive_letter.upper().replace(":", "")

    # Get the logical disk to partition mapping
    wmic_logical_to_partition_command = (
        "wmic Path Win32_LogicalDiskToPartition Get Antecedent, Dependent"
    )
    logical_to_partition_result = subprocess.run(
        wmic_logical_to_partition_command, shell=True, capture_output=True, text=True
    )

    partition_info = None

    # Find the partition associated with the given drive letter
    for line in logical_to_partition_result.stdout.splitlines():
        line = line.strip()
        if line == "" or "Antecedent" in line:  # Skip empty lines and header
            continue

        # Check if the drive letter is present in the line
        if f'Win32_LogicalDisk.DeviceID="{drive_letter}:"' in line:
            # Use regex to extract the disk and partition information
            match = re.search(r"Disk #(\d+), Partition #(\d+)", line)
            if match:
                disk_number = match.group(1)
                partition_number = f"{int(match.group(2)) + 1}"  # because wmic using number from 0 to mark partitions, but diskpart or gdisk need number from 1
                partition_info = (disk_number, partition_number)
                print(partition_info)
                break

    if partition_info is None:
        print(f"Could not find partition for {drive_letter}.")
        return None

    disk_number, partition_number = partition_info

    # Now find the physical drive associated with this disk number
    physical_command = f'wmic diskdrive where "index={disk_number}" get deviceid'
    physical_result = subprocess.run(
        physical_command, shell=True, capture_output=True, text=True
    )

    physical_drive = None

    # Extract physical drive ID
    for line in physical_result.stdout.splitlines():
        line = line.strip()
        if line == "" or "DeviceID" in line:  # Skip empty lines and header
            continue
        physical_drive = line  # Get the physical drive ID
        break

    return physical_drive, partition_number


# Example usage
drive_letter = input("Enter the drive letter (e.g., E): ").strip().upper()
res = find_drive(drive_letter)
print(res)
