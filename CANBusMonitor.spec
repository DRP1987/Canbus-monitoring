# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_all

# Collect PCAN libraries
datas = []
binaries = []
hiddenimports = []

# Try to collect PCANBasic
try:
    pcan_datas, pcan_binaries, pcan_hiddenimports = collect_all('PCANBasic')
    datas += pcan_datas
    binaries += pcan_binaries
    hiddenimports += pcan_hiddenimports
except Exception as e:
    import warnings
    warnings.warn(f"Could not collect PCANBasic automatically: {e}", RuntimeWarning)

# Add application data files
datas += [
    ('configurations.json', '.'),
    ('assets/logo.png', 'assets'),
    ('assets/icon.png', 'assets'),
    ('assets/icon.ico', 'assets'),
]

# Add hidden imports
hiddenimports += [
    'PyQt5',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'PCANBasic',
]

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
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
    [],
    name='CANBusMonitor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
)
