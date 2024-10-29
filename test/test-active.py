import subprocess

from utils import format as fm

drive_letter = input("Enter the drive letter (e.g., E): ").strip().upper()
res = fm.make_active(drive_letter)
