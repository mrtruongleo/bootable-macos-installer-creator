import os
import subprocess
import re
from utils import format as fm

# Example usage
drive_letter = input("Enter the drive letter (e.g., E): ").strip().upper()
res = fm.make_bootable(drive_letter)
