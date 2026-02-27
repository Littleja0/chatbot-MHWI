# -*- mode: python ; coding: utf-8 -*-
import os
import importlib

# Resolve paths for pythonnet, clr_loader and webview packages
def get_pkg_path(pkg_name):
    mod = importlib.import_module(pkg_name)
    return os.path.dirname(mod.__file__)

pythonnet_path = get_pkg_path('pythonnet')
clr_loader_path = get_pkg_path('clr_loader')
webview_path = get_pkg_path('webview')

a = Analysis(
    ['apps/backend/src/main.py'],
    pathex=['apps/backend/src'],
    binaries=[],
    datas=[
        ('apps/backend/templates', 'templates'),
        ('apps/frontend/dist', 'apps/frontend/dist'),
        ('data', 'data'),
        ('.env', '.'),
        # pythonnet runtime (Python.Runtime.dll + deps.json)
        (os.path.join(pythonnet_path, 'runtime'), os.path.join('pythonnet', 'runtime')),
        # clr_loader native DLLs
        (os.path.join(clr_loader_path, 'ffi', 'dlls'), os.path.join('clr_loader', 'ffi', 'dlls')),
        # webview lib (WebView2 + WinForms DLLs)
        (os.path.join(webview_path, 'lib'), os.path.join('webview', 'lib')),
        (os.path.join(webview_path, 'js'), os.path.join('webview', 'js')),
    ],
    hiddenimports=[
        'jinja2',
        'aiohttp',
        'sqlite3',
        'webview',
        'webview.platforms.winforms',
        'pythonnet',
        'clr',
        'clr_loader',
        'clr_loader.netfx',
        'clr_loader.hostfxr',
        'clr_loader.ffi',
        'clr_loader.ffi.netfx',
        'clr_loader.util',
        'clr_loader.util.find',
        'clr_loader.util.clr_error',
        'clr_loader.types',
    ],
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
