# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['apps/backend/src/main.py'],
    pathex=['apps/backend/src'],
    binaries=[],
    datas=[
        ('apps/backend/templates', 'templates'),
        ('apps/frontend/dist', 'apps/frontend/dist'),
        ('data', 'data'),
        ('.env', '.')
    ],
    hiddenimports=['jinja2', 'aiohttp', 'sqlite3', 'webview'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MHWChatbot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
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
    name='MHWChatbot',
)
