import re
import shutil

def copy_file(source_path, destination_path):
    """
    Copies a file from source_path to destination_path.

    Args:
        source_path (str): The path of the file to copy.
        destination_path (str): The path to copy the file to.
    """
    try:
        shutil.copy(source_path, destination_path)
    except FileNotFoundError:
        print("Source file not found.")
    except PermissionError:
        print("Permission denied.")
    except Exception as e:
        print(f"An error occurred: {e}")
def sanitize_label(volume_label: str):
    """Ensure the volume label complies with FAT32 naming rules."""
    # Only allow uppercase letters, digits, and spaces, and limit to 11 characters
    sanitized_label = re.sub(r"[^A-Z0-9 ]", "", volume_label.upper())[:11]
    if len(sanitized_label) == 0:
        sanitized_label = "NO_LABEL"  # Default label if input is invalid
    return sanitized_label