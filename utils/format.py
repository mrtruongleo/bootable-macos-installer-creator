import subprocess
import sys, os
import re
from elevate import elevate
from utils.func import find_drive, get_disk_size


def sanitize_label(volume_label: str):
    """Ensure the volume label complies with FAT32 naming rules."""
    # Only allow uppercase letters, digits, and spaces, and limit to 11 characters
    sanitized_label = re.sub(r"[^A-Z0-9 ]", "", volume_label.upper())[:11]
    if len(sanitized_label) == 0:
        sanitized_label = "NO_LABEL"  # Default label if input is invalid
    return sanitized_label


def format_drive(
    disk_number,
    scheme="mbr",
    file_system="fat32",
    volume_label="WIN",
    size="10000",
    update_info=None,
):
    try:
        print(f"Preparing disk {disk_number}...")
        if update_info:
            update_info(f"Preparing disk {disk_number}...")
        # Sanitize the label to fit FAT32 constraints
        sanitized_label = sanitize_label(volume_label)
        disk_size = get_disk_size(disk_number)
        print(f"disk size: {disk_size}")
        # Diskpart script to format the drive
        size = f" size={size}" if float(size) < disk_size else f""
        commands = f"""
        select disk {disk_number}
        clean
        convert {scheme}
        create partition primary{size}
        format fs={file_system} quick label={sanitized_label}
        assign
        exit
        """
        process = run_command("diskpart", input=commands)
        if process.returncode == 0:
            # Find the difference to get the new volume
            assigned_letter = get_first_drive_letter_by_disk_number(disk_number) or "R"
            print(
                f"Disk {disk_number}: Created partition {assigned_letter} formatted as {file_system} with label '{sanitized_label}', {size} MB."
            )
            if update_info:
                update_info(
                    f"Disk {disk_number}: Created partition {assigned_letter} formatted as {file_system} with label '{sanitized_label}', {size} MB."
                )

            return assigned_letter
        else:
            print(process.stdout)
            if update_info:
                update_info(f"Failed to format drive.")
            sys.exit(1)
    except Exception as e:
        print(f"Error formatting drive: {e}")
        sys.exit(1)


def get_first_drive_letter_by_disk_number(disk_number):
    """Get the drive letter assigned to a specific disk number using PowerShell."""
    try:
        # PowerShell command to get partition information
        command = f"powershell Get-Partition -DiskNumber {disk_number}"

        # Execute the PowerShell command
        result = subprocess.run(
            command,
            capture_output=True,  # Captures stdout and stderr
            text=True,  # Interprets the output as text (not bytes)
            shell=True,  # Necessary to properly invoke PowerShell on Windows
        )

        if result.returncode == 0:
            # Extract the drive letter using a regular expression
            output = result.stdout
            print(output)
            match = re.search(r"\s+([A-Z])\s+\d", output)
            if match:
                drive_letter = match.group(1)
                return drive_letter
            else:
                print(f"No drive letter found for disk number {disk_number}.")
                return None
        else:
            # Print the error if something went wrong
            print(f"Error: {result.stderr.strip()}")
            return None

    except Exception as e:
        print(f"Error getting drive letter: {e}")
        return None


def run_command(command, input=None):
    """Run a command without opening a new window."""
    elevate(show_console=False)
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    try:
        return subprocess.run(
            command,
            startupinfo=startupinfo,
            input=input,
            text=True,
            shell=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        sys.exit(1)


def make_hybrid(drive_letter, update_info=None):
    gdisk_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "exe",
        "gdisk64.exe",
    )
    drive_letter = drive_letter[:2]
    # Construct the commands you'd normally put in gdisk_input.txt
    physical_drive, partition_number = find_drive(drive_letter)
    print(physical_drive, partition_number)
    gdisk_input = f"""
r
h
{partition_number}
y
07
y
n
w
y
"""

    # Run gdisk64.exe with the physical drive, and pass input via stdin
    if f"{physical_drive}" != "0":
        process = subprocess.Popen(
            [gdisk_path, f"{physical_drive}:"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  # Enable text mode for stdin, stdout, and stderr
            shell=True,
        )

        # Pass the input directly and communicate with the process
        stdout, stderr = process.communicate(gdisk_input)

        # print("Output:")
        print(stdout)
        if update_info:
            # update_info(f"Hybrid: {stdout}")
            update_info(
                f"Made Hybrid MBR partition on GPT disk! (Disk: {physical_drive}, Partition: {partition_number}"
            )
        if stderr:
            if "The protective MBR's 0xEE partition is oversized" not in stderr:
                print(f"Errors:{stderr}")
                if update_info:
                    update_info(f"Failed to make Hybrid partition {stderr}")
        else:
            return True
    else:
        print("Your are working on system drive, Aborted!")


def make_active(drive_letter, update_info=None):
    # Only mark the partition active if it's an MBR disk
    drive_letter = drive_letter[:1]
    commands = f"""
    select volume {drive_letter}
    active
    exit
    """
    p = run_command("diskpart", input=commands)
    if p.returncode == 0:
        print(f"Drive {drive_letter}: partition marked as active (MBR only).")
        if update_info:
            update_info(f"Drive {drive_letter}: partition marked as active (MBR only).")
    else:
        print(f"Make active error: {p.stderr.strip()}")
        if update_info:
            update_info(f"Make active error: {p.stderr.strip()}")


def make_bootable(drive_letter, update_info=None):

    drive_letter = drive_letter[:1]
    try:
        """Make the drive bootable for Legacy BIOS."""
        p = run_command(f"bootsect /nt60 {drive_letter}: /mbr")
        if p.returncode == 0:
            print(f"Drive {drive_letter}: made bootable for Legacy BIOS.")
            if update_info:
                update_info(f"Drive {drive_letter}: made bootable for Legacy BIOS.")
        # else:
        #     print("Cant make bootable legacy")
        #     if update_info:
        #         update_info("Cant make bootable legacy")
    except:
        pass
    # try:
    #     """Make the drive bootable for UEFI."""
    #     p = run_command(f"bcdboot {drive_letter}:\\ /s {drive_letter}: /f UEFI")
    #     if p.returncode == 0:
    #         print(f"Drive {drive_letter}: made bootable for UEFI.")
    #         if update_info:
    #             update_info(f"Drive {drive_letter}: made bootable for UEFI.")
    # except:
    #     pass


if __name__ == "__main__":
    # Get the drive letter and volume label from the user
    drive_letter = input("Enter the drive letter (e.g., E): ").strip().upper()
    volume_label = (
        input("Enter the volume label (optional, default is 'MyVolume'): ").strip()
        or "MyVolume"
    )
    # FM(drive_letter,'fat32', volume_label)
    # make_active(drive_letter)
    make_bootable(drive_letter)
