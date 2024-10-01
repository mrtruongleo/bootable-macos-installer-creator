# Bootable macOS Installer Creator

This Kivy application allows you to create a bootable macOS installer for USB drives or hard disk partitions.
The application requires macOS 11 or higher and a downloaded macOS installer with the `.app` extension.

## Features

- Create a bootable macOS installer from a downloaded macOS installer.
- Support for USB drives and HDD partitions.
- User-friendly interface built with Kivy.
- Simple app

## Support installer

- Im using Mac M1, I can create Macos Monterey, Bigsur, Ventura, Sonoma
- I don't have any other mac to test with older macOS.

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

## Install SDL2 and GLEW:

- If you encounter issues related to SDL2 or GLEW not being installed, you can install them using Homebrew.
  Install Homebrew (if not already installed): Open your terminal and run:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

- Install SDL2 and GLEW: Once Homebrew is installed, run the following commands in your terminal:

```bash
brew install sdl2
brew install glew
```
