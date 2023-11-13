# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
import mediapipe
import customtkinter

block_cipher = None

mp_init = Path(mediapipe.__file__)
mp_modules =  Path(mp_init.parent,"modules")

ctk_init = Path(customtkinter.__file__)
ctk_modules =  Path(ctk_init.parent,"modules")



app = Analysis(
    ['grimassist.py'],
    pathex=[],
    binaries=[],
    datas=[(mp_modules.as_posix(), 'mediapipe/modules'),
                    ('assets','assets'),
                    ('configs','configs'),    
                    (ctk_init.parent.as_posix(), 'customtkinter')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz_app = PYZ(app.pure, app.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz_app,
    app.scripts,
    app.binaries,
    app.zipfiles,
    app.datas,
    [],
    name='grimassist',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/images/icon.ico',
)
