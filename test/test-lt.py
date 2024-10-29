import string
import win32api


def get_available_drive_letter():
    drives = win32api.GetLogicalDriveStrings().split("\000")[:-1]
    used_letters = [drive[0] for drive in drives]
    all_letters = set(string.ascii_uppercase)
    available_letters = all_letters - set(used_letters)

    if available_letters:
        return min(available_letters) + ":"
    else:
        raise Exception("No available drive letters")


# Example usage:
available_letter = get_available_drive_letter()
print(f"Available drive letter: {available_letter}")
