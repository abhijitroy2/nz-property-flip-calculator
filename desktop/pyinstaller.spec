# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Add the project root to the path so we can import app modules
project_root = os.path.abspath(os.path.join(os.path.dirname(SPEC), '..'))
sys.path.insert(0, project_root)

# Collect all data files and modules we need
datas = []
hiddenimports = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'apscheduler',
    'apscheduler.schedulers.blocking',
    'apscheduler.triggers.interval',
    'apscheduler.triggers.cron',
    'jinja2',
    'weasyprint',
    'smtplib',
    'email.mime.multipart',
    'email.mime.text',
    'email.mime.application',
    'pydantic',
    'pydantic_settings',
    'logging',
    'json',
    'csv',
    'datetime',
    'pathlib',
    'threading',
    'queue',
    'os',
    'sys',
    'subprocess',
    'shutil',
    'zipfile',
    'tempfile',
]

# Add app modules (reuse existing pipeline)
try:
    hiddenimports.extend([
        'app.pipeline',
        'app.scoring',
        'app.models',
        'app.main',
        'backend.calculator',
        'backend.config',
    ])
except ImportError:
    pass

a = Analysis(
    [os.path.join(project_root, 'desktop', 'app.py')],
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='RealFlipBatchAnalyzer_v2',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window for GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one
)
