# Bootable macOS Installer Creator

This Kivy application allows you to create a bootable macOS installer for USB drives or hard disk partitions.
The application requires macOS 11 or higher and a downloaded macOS installer with the `.app` extension.

## Features

- Create a bootable macOS installer from a downloaded macOS installer.
- Support for USB drives and HDD partitions.
- User-friendly interface built with Kivy.

## Requirements

- macOS 11 (Big Sur) or higher
- A downloaded macOS installer in `.app` format. You can download macOS installers from the Mac App Store.
- A USB drive or hard disk partition formatted as APFS or Mac OS Extended (Journaled).

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/mrtruongleo/bootable-macos-installer-creator.git
   ```
2. **Test**
   ```bash
   cd bootable-macos-installer-creator
   python -m venv env
   source env/bin/activate
   pip install -r requirements.txt
   python main.py
   ```
3. **Build**
   ```bash
   pyinstaller main.spec
   ```

- After build success, change the name of dist/your_app to your_app.app
- Now it can run on mac with single executable file.
