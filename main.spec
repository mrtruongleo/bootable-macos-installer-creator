# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from kivymd import hooks_path as kivymd_hooks_path

block_cipher = None

# Check the platform and set dependencies accordingly
name = 'CBM'
binaries = []
trees = []
datas = []
if sys.platform == 'win32':
    # Windows specific configuration
    from kivy_deps import sdl2, glew
    sdl2_path = sdl2.dep_bins
    glew_path = glew.dep_bins
    icon_file = 'icon.ico'  # Windows uses .ico files for icons
    # binaries += [*sdl2_path, *glew_path]
    trees = [Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)]
else:
    # macOS specific configuration
    sdl2_path = '/opt/homebrew/lib/libSDL2.dylib' if os.path.exists('/opt/homebrew/lib/libSDL2.dylib') else '/usr/local/lib/libSDL2.dylib'
    glew_path = '/opt/homebrew/lib/libGLEW.dylib' if os.path.exists('/opt/homebrew/lib/libGLEW.dylib') else '/usr/local/lib/libGLEW.dylib'
    icon_file = 'icon.icns'  # macOS uses .icns files for icons
    
    # Add the dylib files to the binaries
    binaries += [
        (sdl2_path, os.path.basename(sdl2_path)),
        (glew_path, os.path.basename(glew_path))
    ]
    trees = []
datas += [
    ('kv/*.kv', 'kv/')
]
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=[],
    hookspath=[kivymd_hooks_path],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    *trees,
    [],
    name=name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True if sys.platform == 'darwin' else False,  # argv emulation for macOS
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[icon_file],
    # Important: Add the following to suppress terminal window on macOS
    windowed=True,  # Ensures the app runs as a GUI app, not in a terminal
    # Bundle the app as a macOS .app bundle
    appname=name  # This will generate a .app bundle
)
