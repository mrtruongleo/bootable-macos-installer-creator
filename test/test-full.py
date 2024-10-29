import subprocess
import os
import sys
from utils import func as fn
from utils import format as fm


def run_cmd(cmd, input=None):
    """Run gdisk to setup partitions on the USB drive."""
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    try:
        return subprocess.run(
            cmd,
            startupinfo=startupinfo,
            input=input,
            text=True,
            shell=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        sys.exit(1)


def run_diskpart(script):
    """Run gdisk to setup partitions on the USB drive."""
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    try:
        return subprocess.run(
            "diskpart",
            startupinfo=startupinfo,
            input=script,
            text=True,
            shell=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        sys.exit(1)


def run_gdisk(disk_number, gdisk_script):
    """Run gdisk to setup partitions on the USB drive."""
    try:
        process = subprocess.Popen(
            ["exe/gdisk64.exe", f"{disk_number}:"],  # Replace with the actual disk path
            stdin=subprocess.PIPE,
            text=True,
        )
        process.communicate(gdisk_script)

    except subprocess.CalledProcessError as e:
        print(f"Error running gdisk: {e}")


def clean_disk(disk_number, mbr=False):
    if mbr == True:
        convert = "convert mbr"
    else:
        convert = "convert gpt"
    diskpart_script = f"""
    select disk {disk_number}
    clean
    {convert}
    exit
    """
    run_diskpart(diskpart_script)


def gdisk_partition(disk_number):
    gdisk_partition = """
o
y
n
1

+20000M
0700
w
y
"""
    run_gdisk(disk_number, gdisk_partition)


def gdisk_hybrid(disk_number, partition_number):
    gdisk_hybrid = f"""
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
    run_gdisk(disk_number, gdisk_hybrid)


def diskpart_format(disk_number, letter="P"):
    # diskpart_script_2 = f"""
    # select disk {disk_number}
    # select partition 1
    # format quick fs=fat32 label="EFI"
    # assign letter=O
    # select partition 2
    # format quick fs=fat32 label="WIN"
    # assign letter=P
    # select partition 3
    # format quick fs=exfat label="DATA"
    # assign letter=Q
    # exit
    # """
    diskpart_script_2 = f"""
    select disk {disk_number}
    select partition 1
    format quick fs=fat32 label="WIN"
    active
    assign letter={letter}
    exit
    """
    # Step 2: Execute diskpart to create the EFI partition
    run_diskpart(diskpart_script_2)

    print("USB drive prepared successfully.")


def split_to(mounted="H", dest="P"):
    target_sources = f"{dest[:1]}:sources"
    if not os.path.exists(target_sources):
        os.makedirs(target_sources)
    cmd = f"dism /Split-Image /ImageFile:{mounted[:1]}:\sources\install.wim /SWMFile:{target_sources}\install.swm /FileSize:3800"
    run_cmd(cmd)


def copy(src="G", dest="P"):
    source_drive = f"{src}:\\"
    destination_drive = f"{dest}:\\"

    # 1. Copy the EFI folder from H:\EFI to X:\
    # shutil.copytree() is used to copy an entire directory tree
    # if os.path.exists(source_efi):
    #     print("copying EFI folder..")
    #     shutil.copytree(
    #         source_efi, destination_efi, dirs_exist_ok=True
    #     )  # `dirs_exist_ok=True` will allow overwriting existing directories
    #     print(f"Copied EFI folder from {source_efi} to {destination_efi}")
    # else:
    #     print(f"{source_efi} does not exist.")

    # 2. Copy all files and folders from H: to Y:\

    # shutil.copytree() can be used to copy the entire source directory
    if os.path.exists(source_drive):
        print("copy file..")
        robocopy_cmd = [
            "robocopy",
            source_drive.rstrip("\\"),
            destination_drive.rstrip("\\"),
            "/E",
            "/NFL",
            "/NDL",
            "/NJH",
        ]
        robocopy_cmd.extend(
            ["/XF", os.path.join(f"{source_drive[:1]}:\\", "sources", "install.wim")]
        )
        process = subprocess.run(robocopy_cmd, stderr=subprocess.STDOUT, text=True)
        print(process.stdout)
        print(f"Copied all files from {source_drive} to {destination_drive}")
    else:
        print(f"{source_drive} does not exist.")

    # print("copying splited wim...")
    # shutil.copytree(
    #     "split", os.path.join(destination_drive, "sources"), dirs_exist_ok=True
    # )  # `dirs_exist_ok=True` will allow overwriting existing directories
    # print(f"Copied splited wim to {destination_drive}")
    # run_gdisk(disk_number, gdisk_hybrid)


if __name__ == "__main__":
    disk_number = input("Enter your drive number (e.g., 1 for \\.\PhysicalDrive1): ")
    # clean_disk(disk_number, mbr=False)

    # # Step 3: Run gdisk to configure the disk layout
    # print("Configuring GPT layout with gdisk...")

    # # Create a command file for gdisk
    # mounted = "K"
    # letter = "P"
    # gdisk_partition(disk_number)
    # diskpart_format(disk_number, letter)
    # split_to(mounted, letter)
    # copy(mounted, letter)
    # # gdisk_hybrid(disk_number, 1)
    # fm.make_active(letter)
    letter = fm.get_first_drive_letter_by_disk_number(disk_number)
    print(f"Letter: {letter}")
