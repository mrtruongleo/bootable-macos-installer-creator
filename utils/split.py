import os


def split_command(source, target):
    # Ensure the target sources directory exists
    wim_source_dir = os.path.join(target, "sources")
    if not os.path.exists(wim_source_dir):
        os.makedirs(wim_source_dir)

    # Path to the install.wim file in the source drive (the mounted ISO)
    install_wim = os.path.join(source, "sources", "install.wim")

    # Ensure paths use backslashes for DISM
    install_wim = install_wim.replace("/", "\\")
    swm_file = os.path.join(wim_source_dir, "install.swm").replace("/", "\\")

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
