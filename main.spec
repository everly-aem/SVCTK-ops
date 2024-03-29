# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('_internal\*.ui', '.'),
    ('_internal\*.json','.'),
    ('_internal\__assets\*','__assets'),
    ('_internal\__reports\*','__reports'),
    ('_internal\__templateStructs\*','__templateStructs'),
    ('_internal\wkhtmltox\\bin\*','wkhtmltox\\bin'),
    ('_internal\wkhtmltox\include\wkhtmltox\*','wkhtmltox\include\wkhtmltox'),
    ('src\*', 'src')],
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
    name='FTS Service Toolkit 0.1.4',
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
    name='FTS Service Toolkit 0.1.4',
)
