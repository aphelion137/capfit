# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['desktop\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('shared', 'shared'), ('web', 'web')],
    hiddenimports=['fastapi', 'uvicorn', 'uvicorn.lifespan', 'uvicorn.lifespan.on', 'uvicorn.protocols', 'uvicorn.protocols.http', 'uvicorn.protocols.websockets', 'uvicorn.loops', 'uvicorn.loops.auto', 'uvicorn.loops.asyncio', 'uvicorn.loops.uvloop', 'uvicorn.logging', 'uvicorn.config', 'uvicorn.main', 'uvicorn.server', 'jinja2', 'jinja2.ext', 'PIL', 'PIL.Image', 'PIL.ImageTk', 'numpy', 'webbrowser', 'socket', 'requests', 'typer', 'click', 'rich', 'starlette', 'pydantic', 'python_multipart'],
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
    a.binaries,
    a.datas,
    [],
    name='Capfit',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
