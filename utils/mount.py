import subprocess

# from elevate import elevate


def mount_iso(iso_path, update_output_label=None):
    if update_output_label:
        update_output_label(f"Mounting ISO from: {iso_path}")
    try:
        # Use PowerShell to mount the ISO
        mount_cmd = [
            "PowerShell",
            "-WindowStyle",
            "Hidden",
            "Mount-DiskImage",
            "-ImagePath",
            iso_path,
        ]
        subprocess.run(mount_cmd, check=True)

        # Use PowerShell to get the drive letter of the mounted ISO
        ps_script = (
            f"Get-DiskImage -ImagePath '{iso_path}' | "
            "Get-Volume | "
            "Select-Object -ExpandProperty DriveLetter"
        )
        result = (
            subprocess.check_output(
                ["PowerShell", "-WindowStyle", "Hidden", "-Command", ps_script]
            )
            .decode()
            .strip()
        )

        if result:
            drive_letter = f"{result}:"
            if update_output_label:
                update_output_label(f"Mounted ISO at {drive_letter}")
            return drive_letter
        else:
            if update_output_label:
                update_output_label("Failed to retrieve drive letter.")
            return None

    except subprocess.CalledProcessError as e:
        if update_output_label:
            update_output_label(f"Mounting ISO failed: {e}")
        return None


def unmount_iso(iso_path, update_output_label=None):
    # Elevate privileges to run the command as an administrator
    # elevate(
    #     show_console=False
    # )  # Automatically elevates the process (no need for PowerShell RunAs)
    if update_output_label:
        update_output_label(f"Unmounting ISO: {iso_path}")
    try:
        # Use PowerShell to dismount the ISO image without RunAs since elevate() is used
        subprocess.check_call(
            [
                "PowerShell",
                "-WindowStyle",
                "Hidden",
                "-Command",
                f'Dismount-DiskImage -ImagePath "{iso_path}"',
            ]
        )
        print(f"Successfully unmounted ISO: {iso_path}")
        if update_output_label:
            update_output_label(f"Successfully unmounted ISO: {iso_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to unmount ISO: {e}")
        if update_output_label:
            update_output_label(f"Failed to unmount ISO: {e}")
