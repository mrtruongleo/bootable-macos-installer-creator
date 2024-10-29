import re
import subprocess


def get_total_files(source, target):
    try:
        # Run robocopy with /L to list files without copying them
        robocopy_cmd = [
            "robocopy",
            f"{source[:1]}:",
            f"{target[:1]}:",
            "/E",
            "/NFL",
            "/NDL",
            "/NJH",
            "/L",
        ]
        output = subprocess.check_output(
            robocopy_cmd, stderr=subprocess.STDOUT, text=True
        )
        # Extract the "Files" row and get the total number of files
        files_line_match = re.search(
            r"Files\s*:\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)", output
        )
        if files_line_match:
            total_files = int(files_line_match.group(1))
            copied_files = int(files_line_match.group(2))
            return total_files, copied_files

    except subprocess.CalledProcessError as e:
        # Handle robocopy's exit code 3 (some files skipped, but not a failure)
        if e.returncode == 3:
            output = e.output  # Get output from the exception
            files_line_match = re.search(
                r"Files\s*:\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)", output
            )
            if files_line_match:
                total_files = int(files_line_match.group(1))
                copied_files = int(files_line_match.group(2))
                return total_files, copied_files
        else:
            print(f"Error getting total file count: {e}")

    return 0, 0


def find_drive(drive_letter: str):
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


import shutil
import os


def copy_file_to_drive(source_file_path, drive_letter: str):
    """
    Copies a file from the source directory to the target drive letter.

    :param source_file_path: The path to the source file (e.g., 'C:/path/to/file.txt').
    :param drive_letter: The drive letter to copy the file to (e.g., 'D').
    """
    # Ensure the drive letter is in the correct format
    drive_letter = drive_letter.upper()[:1]
    destination_drive = f"{drive_letter}:"

    # Check if the drive exists
    if not os.path.exists(destination_drive):
        print(f"Drive {destination_drive} does not exist.")
        return False

    # Get the filename from the source path
    file_name = os.path.basename(source_file_path)

    # Form the destination path
    destination_path = os.path.join(destination_drive, file_name)

    try:
        # Copy the file
        shutil.copy(source_file_path, destination_path)
        print(f"File copied successfully to {destination_path}")
        return True
    except Exception as e:
        print(f"Error copying file: {e}")
        return False


def get_directory_size(directory):
    """Recursively get the size of all files in a directory."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for file in filenames:
            fp = os.path.join(dirpath, file)
            if os.path.exists(fp):
                total_size += os.path.getsize(fp)
    return total_size


def split_command(source, target):
    # Ensure the target sources directory exists
    source = source[:1] + ":"
    target = target[:1] + ":"
    target_wim_sources_path = os.path.join(target, "sources")
    if not os.path.exists(target_wim_sources_path):
        os.makedirs(target_wim_sources_path)

    # Path to the install.wim file in the source drive (the mounted ISO)
    install_wim = os.path.join(source, "sources", "install.wim")

    # Ensure paths use backslashes for DISM
    install_wim = install_wim.replace("/", "\\")
    swm_file = os.path.join(target_wim_sources_path, "install.swm").replace("/", "\\")

    # Ensure the ImageFile path starts with a backslash after the drive letter
    drive_letter = install_wim[0:2]  # Get the drive letter (e.g., F:)
    path = install_wim[2:]  # Get the rest of the path after the drive letter
    install_wim_corrected = drive_letter + "\\" + path  # Correctly format the path

    # Command to split the install.wim file
    split_cmd = [
        "dism",
        "/Split-Image",
        f"/ImageFile:{install_wim_corrected}",  # Path to install.wim in the mounted ISO
        f"/SWMFile:{swm_file}",  # Path to the target directory
        "/FileSize:3800",  # File size limit for each split file
    ]
    # Execute the command with elevated privileges using 'runas'
    # elevated_cmd = ['runas', '/user:Administrator'] + split_cmd
    # Execute the split command and update the UI with progress
    return split_cmd


def split_wim(source_letter, target_letter):
    try:
        print("splitting wim file..")
        split_cmd = split_command(f"{source_letter[:1]}:\\", f"{target_letter[:1]}:\\")
        print(split_cmd)

        process = subprocess.Popen(
            split_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line-buffered output
        )
        print(process.stdout)
        stdout, stderr = process.communicate()

        if stderr:
            print("Error:", stderr)
    except subprocess.CalledProcessError as e:
        # Handle any errors during the split process
        print(f"Failed to split install.wim: {e}")


def copy_with_exclusions(src, dest, exclusions):
    """
    Copy files from src to dest, excluding specified files or directories.

    :param src: Source directory
    :param dest: Destination directory
    :param exclusions: List of files or directories to exclude
    """
    # Ensure the destination directory exists
    os.makedirs(dest, exist_ok=True)

    for item in os.listdir(src):
        # Create full path for the item
        src_item = os.path.join(src, item)
        dest_item = os.path.join(dest, item)

        # Check if the item should be excluded
        if item not in exclusions:
            if os.path.isdir(src_item):
                # Recursively copy directory
                shutil.copytree(src_item, dest_item, dirs_exist_ok=True)
            else:
                # Copy file
                shutil.copy2(src_item, dest_item)
        else:
            print(f"Excluded: {src_item}")


def get_disks():
    # PowerShell command to get disk information
    ps_command = [
        "powershell",
        "-Command",
        "Get-Disk",
    ]
    result = subprocess.run(ps_command, capture_output=True, text=True)

    # Output from PowerShell command
    output = result.stdout.strip().splitlines()
    # Skip the first header line and process the rest
    disk_info = []

    for line in output[2:]:  # Skip first 2 lines (header)
        # Use regular expressions to capture the relevant fields
        match = re.match(r"(\d+)\s+(\S.*\S)\s+(\d+\.?\d*\s\w+)\s+(\S+)", line)
        if match:
            disk_number = match.group(1)
            friendly_name = match.group(2)
            total_size = match.group(3)
            partition_style = match.group(4)

            disk_info.append(
                {
                    "number": disk_number,
                    "info": f'{friendly_name.split("  ")[0]}, {total_size}, {partition_style}',
                }
            )

    return sorted(disk_info, key=lambda x: x["number"]) if len(disk_info) > 0 else []


def get_disk_size(disk_number):
    try:
        # Run PowerShell command to get disk size in MB
        command = f'powershell -Command "$disk = Get-Disk -Number {disk_number}; $disk.Size / 1MB"'
        result = subprocess.run(command, capture_output=True, text=True, shell=True)

        # Parse and convert the result to float
        disk_size_mb = float(result.stdout.strip())
        return disk_size_mb
    except Exception as e:
        print(f"Error checking disk size: {e}")
