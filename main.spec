# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_data_files
import PyQt5

# Get PyQt5 path
pyqt_path = os.path.dirname(PyQt5.__file__)
qt_plugins_path = os.path.join(pyqt_path, "Qt5", "plugins")

# Collect all Qt plugins directly
qt_plugin_paths = []
for dirname in ['platforms', 'imageformats', 'styles', 'platformthemes']:
    plugin_dir = os.path.join(qt_plugins_path, dirname)
    if os.path.exists(plugin_dir):
        qt_plugin_paths.append((plugin_dir, dirname))

# Collect binaries
binaries = []
for src_dir, dest_dir in qt_plugin_paths:
    for file in os.listdir(src_dir):
        if file.endswith('.dll'):
            binaries.append((os.path.join(src_dir, file), dest_dir))

# Add Qt base DLLs
qt_base_path = os.path.join(pyqt_path, "Qt5", "bin")
for dll in ['Qt5Core.dll', 'Qt5Gui.dll', 'Qt5Widgets.dll']:
    dll_path = os.path.join(qt_base_path, dll)
    if os.path.exists(dll_path):
        binaries.append((dll_path, '.'))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=[
        ('ui/resources/icon.png', 'ui/resources'),
        ('ui/resources/typing_text.gif', 'ui/resources'),
        ('ui/resources/icon.ico', 'ui/resources'),
        ('ui/resources/styles.qss', 'ui/resources'),
        ('.env', '.')
    ],
    hiddenimports=[
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.sip',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PCAssistant',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    onefile=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[('ui/resources/icon.ico')]
)