Here’s a revised version of your README that includes the new features, requirements, notes, and a TODO list in Markdown format:

```markdown
# Bootable macOS Installer Creator

![Preview](https://github.com/mrtruongleo/bootable-macos-installer-creator/blob/main/screen.jpg)

This Kivy application allows you to create a bootable macOS/Windows installer for USB drives or hard disk partitions.

## Features

- Create a bootable macOS installer from a downloaded macOS installer.
- Support for creating Windows installers for both UEFI and BIOS legacy mode (Windows version).
- Automatic splitting of Windows images into smaller than 4GB files to copy to FAT32 USB/SSD.
- Download Boot Camp support drivers for almost all models (Windows version).
- Support for USB drives and HDD partitions.
- User-friendly interface built with Kivy.

Here’s a revised version of your sentences for clarity and grammatical accuracy:

## Supported Installers

- **macOS:** You can create macOS installers for all versions from High Sierra to Sonoma using a Mac M1 (I'm not tested with Intel base Mac yet) from `.app` files located anywhere other than the Applications directory.
- **Windows:** The application supports Windows installer creation for both UEFI and BIOS legacy modes. It primarily supports Windows 10 and Windows 11. Other versions have not been tested, as they are not the versions I intend to install.

## Requirements

- macOS 11 (Big Sur) or higher. Currently, I am using a Mac M1, so I cannot confirm if it works with Intel-based Macs.
- A downloaded macOS installer in `.app` format. You can download macOS installers from the Mac App Store.
- A USB drive or hard disk partition formatted as APFS or Mac OS Extended (Journaled) for macOS installers.
- For Windows installers: In the macOS version, the installer can be created on a volume instead of the entire disk, allowing you to have both macOS and Windows installers on the same disk. Note that this only applies to the UEFI version of the Windows installer. In contrast, the Windows version of this app can create installers for both BIOS legacy and UEFI modes, but the entire disk will be formatted (as FAT32) using the MBR file system.

- **Homebrew** installed to manage packages. Install it with:
  ```bash
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  ```
- Install `wimlib` using Homebrew for working with Windows installers:
  ```bash
  brew install wimlib
  ```

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/mrtruongleo/bootable-macos-installer-creator.git
   ```

2. **Test the Application**:
   ```bash
   cd bootable-macos-installer-creator
   python -m venv env
   source env/bin/activate
   pip install -r requirements.txt
   python main.py
   ```

3. **Build the Application**:
   ```bash
   pyinstaller main.spec
   ```
   - After a successful build, change the name of `dist/your_app` to `your_app.app`. Now it can run on a Mac as a single executable file.

## Install SDL2 and GLEW

If you encounter issues related to SDL2 or GLEW not being installed, you can install them using Homebrew. Run the following commands in your terminal:

```bash
brew install sdl2
brew install glew
```

## Notes

- **Windows Installation**: The Windows installer can be created on a partition/volume instead of the whole disk, but only for UEFI mode.
- **macOS Installation**: Creating a macOS installer can only be done on a Mac machine; the Windows version is not supported yet.
- When running the Windows app, ensure to run it as **Administrator**. The target disk will be formatted (entire disk) as MBR.

## TODO

- Create a macOS installer in the Windows version.
- Download Boot Camp support drivers in the macOS version.