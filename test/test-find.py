import subprocess

from utils import format as fm
import subprocess
import re


import subprocess


def find_drive(drive_letter):
    drive_letter = drive_letter.upper()[:1]
    partition_number = None
    disk_number = None
    # PowerShell command to get partition info for the specified drive letter
    partition_command = f"Get-Partition -DriveLetter '{drive_letter}'"
    # Run the PowerShell command to get partition info
    partition_info_result = subprocess.run(
        ["PowerShell", "-WindowStyle", "Hidden", "-Command", partition_command],
        capture_output=True,
        text=True,
    )

    # Check if the command was successful
    if partition_info_result.returncode == 0:

        for line in partition_info_result.stdout.splitlines():
            if drive_letter in line:  # Check if drive letter is present in the line
                match = re.search(r"(\d+)\s+(\w)\s+(\d+)\s+(\d+.\d+)\s+(\w+)", line)
                if match:
                    partition_number = match.group(1)  # Partition number
                    drive_letter_found = match.group(2)  # Drive letter
                    offset = match.group(3)  # Offset
                    size = match.group(4)  # Size
                    partition_info = (
                        partition_number,
                        drive_letter_found,
                        offset,
                        size,
                    )
                    # print(partition_info)
                    break
        # Now, get the disk number using the partition number
        if partition_number:
            disk_command = f"(Get-Partition -DriveLetter '{drive_letter}').DiskNumber"
            disk_info_result = subprocess.run(
                ["PowerShell", "-WindowStyle", "Hidden", "-Command", disk_command],
                capture_output=True,
                text=True,
            )

            if disk_info_result.returncode == 0:
                disk_number = disk_info_result.stdout.strip()
                print(
                    f"Disk number: {disk_number}, Partition number: {partition_number}"
                )  # Debugging line
                return disk_number, partition_number
            else:
                print(
                    f"Error retrieving disk number: {disk_info_result.stderr.strip()}"
                )
    else:
        print(
            f"Error retrieving partition info: {partition_info_result.stderr.strip()}"
        )

    return (disk_number, partition_number)


drive_letter = input("Enter the drive letter (e.g., E): ").strip().upper()
res = find_drive(drive_letter)
# res = fm.make_hybrid(drive_letter)
print(f"{res}")
