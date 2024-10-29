import subprocess
import os


def run_command(command):
    """Run a system command using subprocess and handle any errors."""
    try:
        print(f"Running command: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        # Check if the command succeeded
        if result.returncode == 0:
            print("Command executed successfully.")
            print(result.stdout)
        else:
            print("Command failed with error:")
            print(result.stderr)
            raise Exception(f"Command failed: {result.stderr}")
    except Exception as e:
        print(f"An error occurred: {e}")


def delete_file(filepath):
    """Delete the specified file if it exists."""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Deleted file: {filepath}")
        else:
            print(f"File not found: {filepath}")
    except Exception as e:
        print(f"Error deleting file: {e}")


def main():
    # Get user input for Windows 10 and Windows 11 ISO drive letters
    w10_drive = input("Windows 10 mounted ISO drive letter (e.g., D): ")
    w11_drive = input("Windows 11 mounted ISO drive letter (e.g., E): ")

    # DISM commands for exporting images
    cmd1 = f"Dism /Export-Image /SourceImageFile:{w10_drive}:\\sources\\install.wim /SourceIndex:6 /DestinationImageFile:C:\\w10_pro.wim /Compress:max /CheckIntegrity"
    cmd2 = f"Dism /Export-Image /SourceImageFile:{w11_drive}:\\sources\\install.wim /SourceIndex:6 /DestinationImageFile:C:\\install.wim /Compress:max /CheckIntegrity"
    cmd3 = f"Dism /Export-Image /SourceImageFile:C:\\w10_pro.wim /SourceIndex:1 /DestinationImageFile:C:\\install.wim /Compress:max /CheckIntegrity"

    # Run the commands
    run_command(cmd1)
    run_command(cmd2)
    run_command(cmd3)

    # Cleanup: delete temporary files
    delete_file("C:\\w10_pro.wim")


if __name__ == "__main__":
    main()
