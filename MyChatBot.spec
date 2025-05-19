# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('backend/chat_dataset.db', 'backend'), ('backend/__init__.py', 'backend'), ('.env', '.'), ('frontend/components/loading_widget.py', 'frontend/components'), ('frontend/components/__init__.py', 'frontend/components'), ('frontend/components/chat_message.py', 'frontend/components'), ('frontend/controllers/__init__.py', 'frontend/controllers'), ('frontend/controllers/main_controller.py', 'frontend/controllers'), ('frontend/views/main_window.py', 'frontend/views'), ('frontend/views/__init__.py', 'frontend/views')],
    hiddenimports=['PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets', 'markdown', 'mistralai', 'python-dotenv', 'sqlite3'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PySide6.QtNetwork', 'PySide6.QtWebEngineCore', 'PySide6.QtWebEngine', 'PySide6.QtWebEngineWidgets'],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [('O', None, 'OPTION')],
    exclude_binaries=True,
    name='MyChatBot',
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
    icon=['frontend/assets/icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MyChatBot',
)
