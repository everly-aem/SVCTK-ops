# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets\*','assets'),
    ('commitQueue.ui','.'),
    ('db_cfg.json','.'),
    ('dbHandler.py','.'),
    ('ui_startWarning.py','.'),
    ('startWarning.ui','.'),
    ('mainwindow.ui','.'),
    ('loadSNWindow.ui','.'),
    ('README.md','.'),
    ('continue.ui','.'),
    ('settings.ui','.'),
    ("doneTask.ui","."),
    ("searchResults.ui",".")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FTS Service Toolkit 0.0.1',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
